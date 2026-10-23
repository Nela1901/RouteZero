import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { act, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactNode } from "react";
import { MapaPage, type RutaMapa } from "./MapaPage";

// Leaflet necesita un navegador real: se sustituyen sus componentes por contenedores simples que exponen sus datos
vi.mock("react-leaflet", () => ({
  MapContainer: ({ children }: { children: ReactNode }) => <div data-testid="mapa">{children}</div>,
  TileLayer: () => null,
  CircleMarker: ({ children, radius }: { children: ReactNode; radius: number }) => (
    <div data-testid="marcador" data-radio={radius}>
      {children}
    </div>
  ),
  Polyline: ({ children, pathOptions }: { children: ReactNode; pathOptions: { color: string; dashArray?: string } }) => (
    <div data-testid="linea" data-color={pathOptions.color} data-discontinua={pathOptions.dashArray ? "si" : "no"}>
      {children}
    </div>
  ),
  Popup: ({ children }: { children: ReactNode }) => <div>{children}</div>,
  Tooltip: ({ children }: { children: ReactNode }) => <span>{children}</span>,
}));
vi.mock("leaflet/dist/leaflet.css", () => ({}));

vi.mock("../../api/client", async (importOriginal) => {
  const real = await importOriginal<typeof import("../../api/client")>();
  return { ...real, api: { post: vi.fn(), get: vi.fn(), put: vi.fn(), delete: vi.fn() } };
});

import { api } from "../../api/client";

const pedido = (i: number) => ({
  pedido_id: `p${i}`,
  prioridad: "ESTANDAR",
  estado: "PENDIENTE",
  latitud: "-12.0653",
  longitud: "-75.2049",
  descripcion: `Pedido ${i}`,
});

const DEPOSITO = { latitud: -12.0436, longitud: -75.2264 };

function parada(orden: number, extra: Partial<RutaMapa["paradas"][number]> = {}): RutaMapa["paradas"][number] {
  return {
    orden,
    pedido_id: `pp${orden}`,
    cliente: `Cliente ${orden}`,
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

function ruta(id: string, placa: string, estado = "CONFIRMADA", paradas = [parada(1), parada(2)]): RutaMapa {
  const puntos: [number, number][] = [[-12.04, -75.22], [-12.05, -75.21]];
  return {
    ruta_id: id,
    estado,
    reemplaza_ruta_id: null,
    vehiculo: { vehiculo_id: `v-${id}`, placa, tipo: "CAMIONETA" },
    conductor: { conductor_id: `c-${id}`, nombre: `Conductor ${placa}` },
    hora_salida: "08:00:00",
    hora_regreso: "11:00:00",
    paradas,
    tramos: [
      { desde: 0, hasta: 1, distancia_km: 3.25, duracion_min: 8.4, en_punta: true, puntos },
      { desde: 1, hasta: 2, distancia_km: 1.5, duracion_min: 4, en_punta: false, puntos },
      { desde: 2, hasta: 0, distancia_km: 2, duracion_min: 5.5, en_punta: false, puntos },
    ],
  };
}

const vias = (niveles: [string, string, string] = ["VERDE", "VERDE", "VERDE"]) => ({
  hora: "10:00:00",
  en_punta: false,
  vias: [
    { calle: "Av. Ferrocarril", nivel: niveles[0], factor: 1, motivos: [], segmentos: [[[-12.06, -75.2], [-12.061, -75.201]]] },
    { calle: "Av. Giráldez", nivel: niveles[1], factor: 1, motivos: [], segmentos: [[[-12.07, -75.2], [-12.071, -75.201]]] },
    { calle: "Calle Real", nivel: niveles[2], factor: 1, motivos: [], segmentos: [[[-12.08, -75.2], [-12.081, -75.201]]] },
  ],
});

function api_responde(rutas: RutaMapa[], congestion: unknown = vias(), pedidos: unknown[] = []) {
  vi.mocked(api.get).mockImplementation(async (url: string) => {
    if (url.startsWith("/api/rutas/mapa")) return { fecha_jornada: "2026-10-21", deposito: DEPOSITO, rutas };
    if (url.startsWith("/api/rutas/congestion")) return congestion;
    if (url.startsWith("/api/pedidos")) return { items: pedidos, total: pedidos.length, limite: 200, desplazamiento: 0 };
    throw new Error(`URL inesperada ${url}`);
  });
}

const llamadasA = (prefijo: string) => vi.mocked(api.get).mock.calls.filter(([u]) => String(u).startsWith(prefijo));
const marcadoresDeRadio = (radio: number) => document.querySelectorAll(`[data-testid="marcador"][data-radio="${radio}"]`);

describe("MapaPage", () => {
  beforeEach(() => {
    vi.mocked(api.get).mockReset();
  });
  afterEach(() => vi.useRealTimers());

  it("dibuja un marcador por pedido pendiente del listado paginado (regresión: esperaba una lista y fallaba con `e.map is not a function`)", async () => {
    api_responde([], vias(), [pedido(1), pedido(2), pedido(3)]);
    render(<MapaPage />);

    await waitFor(() => expect(marcadoresDeRadio(7)).toHaveLength(3));
    expect(api.get).toHaveBeenCalledWith("/api/pedidos?limite=200");
  });

  it("no dibuja como pendientes los pedidos que ya están asignados o entregados", async () => {
    api_responde([], vias(), [pedido(1), { ...pedido(2), estado: "ASIGNADO" }, { ...pedido(3), estado: "ENTREGADO" }]);
    render(<MapaPage />);
    await waitFor(() => expect(marcadoresDeRadio(7)).toHaveLength(1));
  });

  it("el filtro de pedidos pendientes los oculta y los vuelve a mostrar", async () => {
    api_responde([], vias(), [pedido(1), pedido(2)]);
    const usuario = userEvent.setup();
    render(<MapaPage />);
    await waitFor(() => expect(marcadoresDeRadio(7)).toHaveLength(2));

    await usuario.click(screen.getByLabelText("Pedidos pendientes"));
    expect(marcadoresDeRadio(7)).toHaveLength(0);
    await usuario.click(screen.getByLabelText("Pedidos pendientes"));
    expect(marcadoresDeRadio(7)).toHaveLength(2);
  });

  it("sin rutas en la fecha muestra el mapa base, el depósito y el mensaje", async () => {
    api_responde([]);
    render(<MapaPage />);

    expect(await screen.findByText(/no hay rutas para esta fecha/i)).toBeInTheDocument();
    expect(screen.getByTestId("mapa")).toBeInTheDocument();
    expect(marcadoresDeRadio(9)).toHaveLength(1); // el depósito
    expect(screen.getAllByTestId("linea")).toHaveLength(3); // solo las tres vías
  });

  it("dibuja cada tramo de cada ruta con su color y numera las paradas", async () => {
    api_responde([ruta("r1", "ABC-101"), ruta("r2", "XYZ-202")]);
    render(<MapaPage />);

    await waitFor(() => expect(screen.getAllByTestId("linea")).toHaveLength(3 + 6)); // 3 vías + 3 tramos por ruta
    expect(marcadoresDeRadio(10)).toHaveLength(4); // 2 paradas por ruta
    const colores = screen.getAllByTestId("linea").slice(3).map((l) => l.getAttribute("data-color"));
    expect(new Set(colores).size).toBe(2); // cada ruta, un color
    expect(colores.slice(0, 3)).toEqual([colores[0], colores[0], colores[0]]);
  });

  it("lista cada ruta con el tiempo estimado y la distancia de cada tramo", async () => {
    api_responde([ruta("r1", "ABC-101")]);
    render(<MapaPage />);

    const panel = await screen.findByRole("complementary", { name: /rutas y congestión/i });
    expect(within(panel).getByText("ABC-101")).toBeInTheDocument();
    expect(within(panel).getByText(/Conductor ABC-101/)).toBeInTheDocument();
    expect(within(panel).getByText("Depósito → Parada 1")).toBeInTheDocument();
    expect(within(panel).getByText(/8\.4 min · 3\.25 km · punta/)).toBeInTheDocument();
    expect(within(panel).getByText("Parada 2 → Depósito")).toBeInTheDocument();
    expect(within(panel).getByText(/2 parada\(s\) · 6\.8 km · 18 min/)).toBeInTheDocument();
  });

  it("el estado de cada parada se ve en el mapa: entregada, fallida, cancelada o pendiente", async () => {
    api_responde([
      ruta("r1", "ABC-101", "EN_EJECUCION", [
        parada(1, { estado_entrega: "ENTREGADO" }),
        parada(2, { estado_entrega: "FALLIDO" }),
        parada(3, { pedido_estado: "CANCELADO" }),
        parada(4),
      ]),
    ]);
    render(<MapaPage />);

    expect(await screen.findByText("1✓")).toBeInTheDocument();
    expect(screen.getByText("2✗")).toBeInTheDocument();
    expect(screen.getByText("3✕")).toBeInTheDocument();
    expect(screen.getByText("4")).toBeInTheDocument();
    expect(screen.getByText(/Pedido cancelado/)).toBeInTheDocument();
    expect(screen.getByText(/Entregado$/)).toBeInTheDocument();
    expect(screen.getByText(/Entrega fallida/)).toBeInTheDocument();
    expect(screen.getByText(/Pendiente de entrega/)).toBeInTheDocument();
  });

  it("un borrador se dibuja con línea discontinua y una ruta confirmada con línea continua", async () => {
    api_responde([ruta("r1", "ABC-101", "PLANIFICADA"), ruta("r2", "XYZ-202", "CONFIRMADA")]);
    render(<MapaPage />);

    await waitFor(() => expect(screen.getAllByTestId("linea")).toHaveLength(9));
    const discontinuas = screen.getAllByTestId("linea").slice(3).map((l) => l.getAttribute("data-discontinua"));
    expect(discontinuas).toEqual(["si", "si", "si", "no", "no", "no"]);
  });

  it("ocultar una ruta quita sus tramos y sus paradas del mapa", async () => {
    api_responde([ruta("r1", "ABC-101"), ruta("r2", "XYZ-202")]);
    const usuario = userEvent.setup();
    render(<MapaPage />);
    await waitFor(() => expect(screen.getAllByTestId("linea")).toHaveLength(9));

    await usuario.click(screen.getAllByLabelText("Mostrar en el mapa")[0]);
    expect(screen.getAllByTestId("linea")).toHaveLength(6);
    expect(marcadoresDeRadio(10)).toHaveLength(2);
  });

  it("el panel se puede ocultar para ver todo el mapa y volver a mostrar", async () => {
    api_responde([ruta("r1", "ABC-101")]);
    const usuario = userEvent.setup();
    render(<MapaPage />);

    expect(await screen.findByRole("complementary", { name: /rutas y congestión/i })).toBeInTheDocument();
    await usuario.click(screen.getByRole("button", { name: "Ocultar panel" }));
    expect(screen.queryByRole("complementary", { name: /rutas y congestión/i })).not.toBeInTheDocument();
    expect(screen.getAllByTestId("linea").length).toBeGreaterThan(0); // el mapa sigue dibujado
    await usuario.click(screen.getByRole("button", { name: "Mostrar panel" }));
    expect(screen.getByRole("complementary", { name: /rutas y congestión/i })).toBeInTheDocument();
  });

  it("muestra el nivel de congestión de cada vía con su color y la hora punta", async () => {
    api_responde([], {
      hora: "08:30:00",
      en_punta: true,
      vias: [
        { calle: "Av. Ferrocarril", nivel: "ROJO", factor: 5.4, motivos: ["hora punta", "incidente"], segmentos: [[[-12.06, -75.2], [-12.061, -75.201]]] },
        { calle: "Av. Giráldez", nivel: "AMARILLO", factor: 1.6, motivos: ["hora punta"], segmentos: [[[-12.07, -75.2], [-12.071, -75.201]]] },
        { calle: "Calle Real", nivel: "VERDE", factor: 1, motivos: [], segmentos: [[[-12.08, -75.2], [-12.081, -75.201]]] },
      ],
    });
    render(<MapaPage />);

    const seccion = await screen.findByRole("region", { name: "Congestión de las vías" });
    expect(within(seccion).getByText(/Congestión a las 08:30/)).toBeInTheDocument();
    expect(within(seccion).getByText("· hora punta")).toBeInTheDocument();
    expect(within(seccion).getByText("Congestión alta · hora punta + incidente")).toBeInTheDocument();
    expect(within(seccion).getByText("Congestión moderada · hora punta")).toBeInTheDocument();
    expect(within(seccion).getByText("Fluido")).toBeInTheDocument();
    const colores = screen.getAllByTestId("linea").map((l) => l.getAttribute("data-color"));
    expect(colores).toEqual(["#d63031", "#e0a800", "#2e9e57"]);
  });

  it("cambiar la hora vuelve a pedir la congestión a esa hora", async () => {
    api_responde([]);
    render(<MapaPage />);
    await waitFor(() => expect(llamadasA("/api/rutas/congestion")).toHaveLength(1));

    fireEvent.change(screen.getByLabelText("Hora de la congestión"), { target: { value: "12:30" } });
    await waitFor(() => expect(api.get).toHaveBeenCalledWith("/api/rutas/congestion?hora=12:30"));
  });

  it("cambiar la fecha vuelve a pedir las rutas de ese día", async () => {
    api_responde([]);
    render(<MapaPage />);
    await waitFor(() => expect(llamadasA("/api/rutas/mapa")).toHaveLength(1));

    fireEvent.change(screen.getByLabelText("Fecha de la jornada"), { target: { value: "2026-11-05" } });
    await waitFor(() => expect(api.get).toHaveBeenCalledWith("/api/rutas/mapa?fecha=2026-11-05"));
  });

  it("el botón Actualizar y el refresco de cada 30 s vuelven a pedir los datos; se puede desactivar", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    api_responde([]);
    render(<MapaPage />);
    await waitFor(() => expect(llamadasA("/api/rutas/mapa")).toHaveLength(1));

    fireEvent.click(screen.getByRole("button", { name: "Actualizar" }));
    await waitFor(() => expect(llamadasA("/api/rutas/mapa")).toHaveLength(2));

    await act(async () => {
      await vi.advanceTimersByTimeAsync(30_000);
    });
    expect(llamadasA("/api/rutas/mapa").length).toBeGreaterThanOrEqual(3);

    fireEvent.click(screen.getByLabelText("Actualizar cada 30 s"));
    const antes = llamadasA("/api/rutas/mapa").length;
    await act(async () => {
      await vi.advanceTimersByTimeAsync(90_000);
    });
    expect(llamadasA("/api/rutas/mapa")).toHaveLength(antes);
  });

  it("mientras calcula los recorridos avisa que la primera carga puede tardar, y luego indica la hora de la actualización", async () => {
    let terminar: (valor: unknown) => void = () => {};
    vi.mocked(api.get).mockImplementation((url: string) => {
      if (url.startsWith("/api/rutas/mapa")) return new Promise((resolver) => (terminar = resolver)) as never;
      if (url.startsWith("/api/rutas/congestion")) return Promise.resolve(vias()) as never;
      return Promise.resolve({ items: [], total: 0, limite: 200, desplazamiento: 0 }) as never;
    });
    render(<MapaPage />);

    expect(await screen.findByText(/calculando los recorridos por calles/i)).toBeInTheDocument();
    await act(async () => terminar({ fecha_jornada: "2026-10-21", deposito: DEPOSITO, rutas: [] }));
    expect(await screen.findByText(/actualizado a las/i)).toBeInTheDocument();
    expect(screen.queryByText(/calculando los recorridos/i)).not.toBeInTheDocument();
  });

  it("si la API falla muestra el error en lugar de un mapa en blanco", async () => {
    vi.mocked(api.get).mockRejectedValue(new Error("sin conexión"));
    render(<MapaPage />);
    expect(await screen.findByText(/no se pudo cargar el mapa/i)).toBeInTheDocument();
  });
});
