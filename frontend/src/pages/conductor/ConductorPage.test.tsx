import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { act, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactNode } from "react";
import { ConductorPage, type MiRuta } from "./ConductorPage";
import { ToastProvider } from "../../context/ToastContext";
import { ConfirmProvider } from "../../context/ConfirmContext";

const cerrarSesion = vi.fn();

vi.mock("../../context/AuthContext", () => ({
  useAuth: () => ({
    usuario: { usuarioId: "u1", email: "conductor.prueba@routezero.dev", rolNombre: "CONDUCTOR", mfaActivo: false },
    cerrarSesion,
    recargarUsuario: vi.fn(),
  }),
}));
vi.mock("../../components/BotonTema", () => ({ BotonTema: () => null }));

// Leaflet necesita un navegador real: se sustituyen sus componentes por contenedores simples que exponen sus datos
vi.mock("react-leaflet", () => ({
  MapContainer: ({ children }: { children: ReactNode }) => <div data-testid="mapa">{children}</div>,
  TileLayer: () => null,
  CircleMarker: ({ children, radius }: { children: ReactNode; radius: number }) => (
    <div data-testid="marcador" data-radio={radius}>
      {children}
    </div>
  ),
  Polyline: ({ pathOptions }: { pathOptions: { color: string } }) => <div data-testid="linea" data-color={pathOptions.color} />,
  Popup: ({ children }: { children: ReactNode }) => <div>{children}</div>,
  Tooltip: ({ children }: { children: ReactNode }) => <span>{children}</span>,
}));
vi.mock("leaflet/dist/leaflet.css", () => ({}));

vi.mock("../../api/client", async (importOriginal) => {
  const real = await importOriginal<typeof import("../../api/client")>();
  return { ...real, api: { post: vi.fn(), get: vi.fn(), put: vi.fn(), patch: vi.fn(), delete: vi.fn() } };
});

import { api } from "../../api/client";

type Parada = NonNullable<MiRuta["ruta"]>["paradas"][number];

function parada(orden: number, extra: Partial<Parada> = {}): Parada {
  return {
    orden,
    pedido_id: `p${orden}`,
    cliente: `Cliente ${orden}`,
    peso_kg: "25.00",
    prioridad: "ESTANDAR",
    latitud: -12.06 + orden / 1000,
    longitud: -75.21,
    hora_estimada: `0${7 + orden}:30:00`,
    minutos_retraso: 0,
    estado_entrega: "PENDIENTE",
    pedido_estado: "ASIGNADO",
    ...extra,
  };
}

function datos(extra: Partial<MiRuta> = {}, paradas: Parada[] = [parada(1), parada(2), parada(3)], estado = "CONFIRMADA"): MiRuta {
  const pendientes = paradas.filter((p) => p.pedido_estado !== "CANCELADO" && p.estado_entrega === "PENDIENTE");
  const atendibles = paradas.filter((p) => p.pedido_estado !== "CANCELADO");
  return {
    fecha_jornada: "2026-10-21",
    hora: "10:00:00",
    deposito: { latitud: -12.0436, longitud: -75.2264 },
    vinculado: true,
    mensaje: null,
    conductor: { conductor_id: "c1", nombre: "Carlos Quispe" },
    ruta: {
      ruta_id: "ruta-1",
      estado,
      hora_salida: "08:00:00",
      hora_regreso: "11:00:00",
      paradas,
      tramos: paradas.concat([parada(0)]).map((_, i) => ({ desde: i, hasta: i + 1, puntos: [[-12.04, -75.22], [-12.05, -75.21]] as [number, number][] })),
    },
    siguiente_orden: pendientes.length ? Math.min(...pendientes.map((p) => p.orden)) : null,
    entregadas: atendibles.length - pendientes.length,
    pendientes: pendientes.length,
    alertas: [],
    ...extra,
  };
}

function renderPagina() {
  return render(
    <ToastProvider>
      <ConfirmProvider>
        <ConductorPage />
      </ConfirmProvider>
    </ToastProvider>,
  );
}

const marcadoresDeRadio = (radio: number) => document.querySelectorAll(`[data-testid="marcador"][data-radio="${radio}"]`);

describe("ConductorPage", () => {
  beforeEach(() => {
    vi.mocked(api.get).mockReset();
    vi.mocked(api.patch).mockReset();
    cerrarSesion.mockReset();
  });
  afterEach(() => vi.useRealTimers());

  it("una cuenta sin conductor vinculado recibe la explicación del servidor", async () => {
    vi.mocked(api.get).mockResolvedValue(datos({ vinculado: false, conductor: null, ruta: null, mensaje: "Tu usuario todavía no está vinculado a un conductor. Pide al administrador que registre tu correo." }));
    renderPagina();

    expect(await screen.findByText("Cuenta sin vincular")).toBeInTheDocument();
    expect(screen.getByText(/pide al administrador que registre tu correo/i)).toBeInTheDocument();
  });

  it("sin ruta asignada muestra el mensaje y ningún mapa", async () => {
    vi.mocked(api.get).mockResolvedValue(datos({ ruta: null, mensaje: "No tienes rutas asignadas por el momento." }));
    renderPagina();

    expect(await screen.findByText("No tienes rutas asignadas por el momento.")).toBeInTheDocument();
    expect(screen.getByText("Sin ruta por ahora")).toBeInTheDocument();
    expect(screen.queryByTestId("mapa")).not.toBeInTheDocument();
  });

  it("muestra su ruta: saludo, avance, siguiente parada, las que faltan y el mapa", async () => {
    vi.mocked(api.get).mockResolvedValue(datos());
    renderPagina();

    expect(await screen.findByText("Hola, Carlos Quispe")).toBeInTheDocument();
    expect(screen.getByText("0 de 3 entregas")).toBeInTheDocument();
    expect(screen.getByRole("progressbar", { name: "Avance de entregas" })).toHaveAttribute("aria-valuenow", "0");
    const siguiente = screen.getByRole("region", { name: "Siguiente parada" });
    expect(within(siguiente).getByText("Cliente 1")).toBeInTheDocument();
    expect(within(siguiente).getByText(/Parada 1 de 3/)).toBeInTheDocument();
    const despues = screen.getByRole("region", { name: "Paradas que faltan" });
    expect(within(despues).getByText("Cliente 2")).toBeInTheDocument();
    expect(within(despues).getByText("Cliente 3")).toBeInTheDocument();
    expect(within(despues).queryByText("Cliente 1")).not.toBeInTheDocument();
    expect(screen.getAllByTestId("linea")).toHaveLength(4); // un tramo por parada más el regreso
    expect(marcadoresDeRadio(14)).toHaveLength(1); // la siguiente parada se destaca
    expect(marcadoresDeRadio(10)).toHaveLength(2);
  });

  it("una parada express se señala como tal", async () => {
    vi.mocked(api.get).mockResolvedValue(datos({}, [parada(1, { prioridad: "EXPRESS" }), parada(2)]));
    renderPagina();
    expect(await screen.findByText("Express")).toBeInTheDocument();
  });

  it("registra la entrega después de confirmar y vuelve a pedir la ruta", async () => {
    vi.mocked(api.get).mockResolvedValue(datos());
    vi.mocked(api.patch).mockResolvedValue({ ruta_id: "ruta-1", pedido_id: "p1", estado_entrega: "ENTREGADO", estado_ruta: "EN_EJECUCION" });
    const usuario = userEvent.setup();
    renderPagina();

    await usuario.click(await screen.findByRole("button", { name: "Entregado" }));
    await usuario.click(await screen.findByRole("button", { name: "Sí, entregado" }));

    await waitFor(() => expect(api.patch).toHaveBeenCalledWith("/api/rutas/ruta-1/paradas/p1/entrega", { estado: "ENTREGADO" }));
    await waitFor(() => expect(vi.mocked(api.get).mock.calls.length).toBeGreaterThanOrEqual(2));
  });

  it("también registra una entrega fallida", async () => {
    vi.mocked(api.get).mockResolvedValue(datos());
    vi.mocked(api.patch).mockResolvedValue({});
    const usuario = userEvent.setup();
    renderPagina();

    await usuario.click(await screen.findByRole("button", { name: "No se pudo" }));
    await usuario.click(await screen.findByRole("button", { name: "Sí, no se pudo" }));
    await waitFor(() => expect(api.patch).toHaveBeenCalledWith("/api/rutas/ruta-1/paradas/p1/entrega", { estado: "FALLIDO" }));
  });

  it("si se cancela la confirmación no se registra nada", async () => {
    vi.mocked(api.get).mockResolvedValue(datos());
    const usuario = userEvent.setup();
    renderPagina();

    await usuario.click(await screen.findByRole("button", { name: "Entregado" }));
    await usuario.click(await screen.findByRole("button", { name: /cancelar/i }));
    expect(api.patch).not.toHaveBeenCalled();
  });

  it("muestra lo ya atendido, el avance y pasa a la siguiente parada", async () => {
    vi.mocked(api.get).mockResolvedValue(datos({}, [parada(1, { estado_entrega: "ENTREGADO" }), parada(2, { estado_entrega: "FALLIDO" }), parada(3)]));
    renderPagina();

    expect(await screen.findByText("2 de 3 entregas")).toBeInTheDocument();
    const siguiente = screen.getByRole("region", { name: "Siguiente parada" });
    expect(within(siguiente).getByText("Cliente 3")).toBeInTheDocument();
    const atendidas = screen.getByRole("region", { name: "Paradas atendidas" });
    expect(within(atendidas).getByText("Entregado")).toBeInTheDocument();
    expect(within(atendidas).getByText("Fallido")).toBeInTheDocument();
  });

  it("al terminar todas las paradas muestra que la ruta está completada", async () => {
    vi.mocked(api.get).mockResolvedValue(datos({}, [parada(1, { estado_entrega: "ENTREGADO" }), parada(2, { estado_entrega: "ENTREGADO" })], "COMPLETADA"));
    renderPagina();

    expect(await screen.findByText("Ruta completada")).toBeInTheDocument();
    expect(screen.getByText(/buen trabajo/i)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Entregado" })).not.toBeInTheDocument();
  });

  it("un pedido cancelado se avisa y no se ofrece como siguiente parada", async () => {
    vi.mocked(api.get).mockResolvedValue(datos({}, [parada(1, { pedido_estado: "CANCELADO" }), parada(2), parada(3)]));
    renderPagina();

    const siguiente = await screen.findByRole("region", { name: "Siguiente parada" });
    expect(within(siguiente).getByText("Cliente 2")).toBeInTheDocument();
    expect(screen.getByText("0 de 2 entregas")).toBeInTheDocument();
    const cancelados = screen.getByRole("region", { name: "Pedidos cancelados" });
    expect(within(cancelados).getByText(/Cliente 1/)).toBeInTheDocument();
    expect(screen.getByText(/no los atiendas/i)).toBeInTheDocument();
  });

  it("muestra las alertas de tráfico y marca las que están en su ruta", async () => {
    vi.mocked(api.get).mockResolvedValue(
      datos({
        alertas: [
          { calle: "Av. Ferrocarril", nivel: "ROJO", factor: 3, motivos: ["incidente"], en_tu_ruta: true, segmentos: [[[-12.06, -75.2], [-12.061, -75.201]]] },
          { calle: "Calle Real", nivel: "AMARILLO", factor: 1.3, motivos: ["hora punta"], en_tu_ruta: false, segmentos: [] },
        ],
      }),
    );
    renderPagina();

    const alertas = await screen.findByRole("region", { name: "Alertas de tráfico" });
    expect(within(alertas).getByText(/Av\. Ferrocarril/)).toBeInTheDocument();
    expect(within(alertas).getByText(/Congestión alta \(incidente\)/)).toBeInTheDocument();
    expect(within(alertas).getByText(/Congestión moderada \(hora punta\)/)).toBeInTheDocument();
    expect(within(alertas).getAllByText("En tu ruta")).toHaveLength(1);
    // la vía que cruza su ruta se dibuja en el mapa además de su recorrido
    const colores = screen.getAllByTestId("linea").map((l) => l.getAttribute("data-color"));
    expect(colores.filter((c) => c === "#d63031")).toHaveLength(1);
  });

  it("sin alertas no muestra esa sección", async () => {
    vi.mocked(api.get).mockResolvedValue(datos());
    renderPagina();
    await screen.findByText("Hola, Carlos Quispe");
    expect(screen.queryByRole("region", { name: "Alertas de tráfico" })).not.toBeInTheDocument();
  });

  it("vuelve a pedir la ruta cada 30 s y con el botón Actualizar", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    vi.mocked(api.get).mockResolvedValue(datos());
    renderPagina();
    await waitFor(() => expect(api.get).toHaveBeenCalledTimes(1));

    fireEvent.click(screen.getByRole("button", { name: "Actualizar" }));
    await waitFor(() => expect(api.get).toHaveBeenCalledTimes(2));
    await act(async () => {
      await vi.advanceTimersByTimeAsync(30_000);
    });
    expect(vi.mocked(api.get).mock.calls.length).toBeGreaterThanOrEqual(3);
    expect(api.get).toHaveBeenCalledWith("/api/rutas/mi-ruta");
  });

  it("si la API falla muestra el error", async () => {
    vi.mocked(api.get).mockRejectedValue(new Error("sin conexión"));
    renderPagina();
    expect(await screen.findByText(/no se pudo cargar tu ruta/i)).toBeInTheDocument();
  });

  it("el botón Cerrar sesión cierra la sesión", async () => {
    vi.mocked(api.get).mockResolvedValue(datos());
    const usuario = userEvent.setup();
    renderPagina();
    await usuario.click(await screen.findByRole("button", { name: "Cerrar sesión" }));
    expect(cerrarSesion).toHaveBeenCalledOnce();
  });
});
