import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { RutasPage, type Ruta } from "./RutasPage";
import { ToastProvider } from "../../context/ToastContext";
import { ConfirmProvider } from "../../context/ConfirmContext";

const rolActual = { valor: "ADMINISTRADOR" };

vi.mock("../../context/AuthContext", () => ({
  useAuth: () => ({
    usuario: { usuarioId: "u1", email: "prueba@routezero.dev", rolNombre: rolActual.valor, mfaActivo: false },
    recargarUsuario: vi.fn(),
    cerrarSesion: vi.fn(),
  }),
}));

vi.mock("../../api/client", async (importOriginal) => {
  const real = await importOriginal<typeof import("../../api/client")>();
  return { ...real, api: { post: vi.fn(), get: vi.fn(), put: vi.fn(), patch: vi.fn(), delete: vi.fn() } };
});

import { api } from "../../api/client";

function ruta(estado: string, extra: Partial<Ruta> = {}): Ruta {
  return {
    ruta_id: "ruta-1",
    lote_id: "lote-1",
    fecha_jornada: "2026-10-12",
    estado,
    vehiculo: { vehiculo_id: "v1", placa: "ABC-101", tipo: "CAMIONETA" },
    conductor: { conductor_id: "c1", nombre: "Carlos Quispe Mendoza" },
    hora_salida: "08:00:00",
    hora_regreso: "13:30:00",
    distancia_km: "42.50",
    tiempo_min: 330,
    cantidad_paradas: 2,
    metricas: {
      emision_co2_kg: "10.6250",
      combustible_l: "4.2500",
      combustible_ahorrado_l: "0.5000",
      distancia_km: "42.50",
      cumplimiento_ventanas_pct: "100.00",
    },
    paradas: [],
    ...extra,
  };
}

function renderPagina() {
  return render(
    <ToastProvider>
      <ConfirmProvider>
        <RutasPage />
      </ConfirmProvider>
    </ToastProvider>,
  );
}

function rutasEnLaApi(lista: Ruta[], incidentes: unknown[] = [], estadoDetalle = "PLANIFICADA", paradasDetalle?: Ruta["paradas"]) {
  vi.mocked(api.get).mockImplementation(async (url: string) => {
    if (url === "/api/rutas/incidentes") return incidentes;
    if (url.startsWith("/api/rutas/ruta-1")) {
      if (paradasDetalle) return ruta(estadoDetalle, { paradas: paradasDetalle });
      return ruta(estadoDetalle, {
        paradas: [
          { orden: 1, pedido_id: "p1", cliente: "Bodega San José", descripcion: null, peso_kg: "25.00", prioridad: "EXPRESS", hora_estimada: "08:20:00", minutos_retraso: 0 },
          { orden: 2, pedido_id: "p2", cliente: "Calzados Puno", descripcion: null, peso_kg: "40.00", prioridad: "ESTANDAR", hora_estimada: "09:05:00", minutos_retraso: 12 },
        ],
      });
    }
    return lista;
  });
}

describe("RutasPage", () => {
  beforeEach(() => {
    rolActual.valor = "ADMINISTRADOR";
    vi.mocked(api.get).mockReset();
    vi.mocked(api.post).mockReset();
    vi.mocked(api.patch).mockReset();
    vi.mocked(api.delete).mockReset();
  });

  it("el Administrador ve el aviso de borrador con los botones para confirmar y descartar", async () => {
    rutasEnLaApi([ruta("PLANIFICADA")]);
    renderPagina();

    expect(await screen.findByText(/borrador sin confirmar/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Confirmar rutas" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Descartar" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /generar rutas/i })).toBeInTheDocument();
    expect(screen.getByText("ABC-101")).toBeInTheDocument();
    expect(screen.getByText("Carlos Quispe Mendoza", { exact: false })).toBeInTheDocument();
  });

  it("el Operador ve el borrador pero no puede generar, confirmar ni descartar", async () => {
    rolActual.valor = "OPERADOR";
    rutasEnLaApi([ruta("PLANIFICADA")]);
    renderPagina();

    expect(await screen.findByText(/borrador sin confirmar/i)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Confirmar rutas" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Descartar" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /generar rutas/i })).not.toBeInTheDocument();
  });

  it("sin borradores no se muestra el aviso, y una ruta confirmada figura como Confirmada", async () => {
    rutasEnLaApi([ruta("CONFIRMADA")]);
    renderPagina();

    expect(await screen.findByText("Confirmada")).toBeInTheDocument();
    expect(screen.queryByText(/borrador sin confirmar/i)).not.toBeInTheDocument();
  });

  it("confirma el lote después de aceptar el diálogo", async () => {
    rutasEnLaApi([ruta("PLANIFICADA")]);
    vi.mocked(api.post).mockResolvedValue({ lote_id: "lote-1", rutas_confirmadas: 1, pedidos_asignados: 2 });
    const usuario = userEvent.setup();
    renderPagina();

    await usuario.click(await screen.findByRole("button", { name: "Confirmar rutas" }));
    const dialogo = await screen.findByRole("alertdialog");
    await usuario.click(within(dialogo).getByRole("button", { name: "Confirmar rutas" }));

    await waitFor(() => expect(api.post).toHaveBeenCalledWith("/api/rutas/lotes/lote-1/confirmar"));
  });

  it("no confirma si se cancela el diálogo", async () => {
    rutasEnLaApi([ruta("PLANIFICADA")]);
    const usuario = userEvent.setup();
    renderPagina();

    await usuario.click(await screen.findByRole("button", { name: "Confirmar rutas" }));
    await usuario.click(within(await screen.findByRole("alertdialog")).getByRole("button", { name: "Cancelar" }));

    expect(api.post).not.toHaveBeenCalled();
  });

  it("descarta el borrador después de aceptar el diálogo", async () => {
    rutasEnLaApi([ruta("PLANIFICADA")]);
    vi.mocked(api.delete).mockResolvedValue({ lote_id: "lote-1", rutas_eliminadas: 1 });
    const usuario = userEvent.setup();
    renderPagina();

    await usuario.click(await screen.findByRole("button", { name: "Descartar" }));
    await usuario.click(within(await screen.findByRole("alertdialog")).getByRole("button", { name: "Descartar" }));

    await waitFor(() => expect(api.delete).toHaveBeenCalledWith("/api/rutas/lotes/lote-1"));
  });

  it("muestra el error de la API cuando la confirmación se rechaza", async () => {
    rutasEnLaApi([ruta("PLANIFICADA")]);
    const { ErrorApi } = await import("../../api/client");
    vi.mocked(api.post).mockRejectedValue(new ErrorApi(409, "No se puede confirmar: 1 pedido(s) ya no están pendientes. Regenere las rutas."));
    const usuario = userEvent.setup();
    renderPagina();

    await usuario.click(await screen.findByRole("button", { name: "Confirmar rutas" }));
    await usuario.click(within(await screen.findByRole("alertdialog")).getByRole("button", { name: "Confirmar rutas" }));

    expect((await screen.findAllByText(/ya no están pendientes/i)).length).toBeGreaterThan(0);
  });

  it("al generar muestra los pedidos sin cobertura con su motivo y la mejora sobre la solución inicial", async () => {
    rutasEnLaApi([]);
    vi.mocked(api.post).mockResolvedValue({
      lote_id: "lote-1",
      imposible: false,
      mensaje: "",
      rutas: [],
      sin_cobertura: [{ pedido_id: "abcdef123456", motivo: "PESO_EXCEDE_CAPACIDAD", sugerencia: "Divida el pedido en envíos más livianos." }],
      fuente_distancias: "calles",
      puntos_aproximados: 0,
      comparativa_base: { mejora_distancia_pct: 12.4, mejora_co2_pct: 9.8 },
      tiempo_ejecucion_s: 8.2,
    });
    const usuario = userEvent.setup();
    renderPagina();

    await usuario.click(await screen.findByRole("button", { name: /generar rutas/i }));

    expect(await screen.findByText(/1 pedido\(s\) sin cobertura/i)).toBeInTheDocument();
    expect(screen.getByText(/Pesa más que cualquier vehículo/i)).toBeInTheDocument();
    expect(screen.getByText(/12 %/)).toBeInTheDocument();
    expect(api.post).toHaveBeenCalledWith("/api/rutas/generar", expect.objectContaining({ fecha_jornada: expect.any(String) }));
  });

  it("cuando no es posible generar rutas muestra el mensaje de la API", async () => {
    rutasEnLaApi([]);
    vi.mocked(api.post).mockResolvedValue({
      lote_id: null,
      imposible: true,
      mensaje: "No es posible generar rutas: no hay vehículos disponibles y conductores elegibles.",
      rutas: [],
      sin_cobertura: [],
      fuente_distancias: "calles",
      puntos_aproximados: 0,
      comparativa_base: null,
      tiempo_ejecucion_s: 0.1,
    });
    const usuario = userEvent.setup();
    renderPagina();

    await usuario.click(await screen.findByRole("button", { name: /generar rutas/i }));
    expect(await screen.findByText(/no es posible generar rutas/i)).toBeInTheDocument();
  });

  it("al abrir una ruta trae sus paradas en orden con el retraso", async () => {
    rutasEnLaApi([ruta("PLANIFICADA")]);
    const usuario = userEvent.setup();
    renderPagina();

    await usuario.click(await screen.findByRole("button", { name: /ver paradas/i }));

    expect(await screen.findByText(/Bodega San José/)).toBeInTheDocument();
    expect(screen.getByText(/EXPRESS/)).toBeInTheDocument();
    expect(screen.getByText(/Calzados Puno/)).toBeInTheDocument();
    expect(screen.getByText(/\+12 min/)).toBeInTheDocument();
  });

  // ------------------------------------------------------------------ HU-012
  it("el Administrador puede re-optimizar cuando hay rutas en curso; el Operador no", async () => {
    rutasEnLaApi([ruta("CONFIRMADA")]);
    const { unmount } = renderPagina();
    expect(await screen.findByRole("button", { name: "Re-optimizar rutas" })).toBeInTheDocument();
    unmount();

    rolActual.valor = "OPERADOR";
    renderPagina();
    await screen.findByText("ABC-101");
    expect(screen.queryByRole("button", { name: "Re-optimizar rutas" })).not.toBeInTheDocument();
  });

  it("sin rutas en curso no se ofrece re-optimizar", async () => {
    rutasEnLaApi([ruta("PLANIFICADA")]);
    renderPagina();
    await screen.findByText("ABC-101");
    expect(screen.queryByRole("button", { name: "Re-optimizar rutas" })).not.toBeInTheDocument();
  });

  it("al re-optimizar envía la fecha y la hora de referencia y resume el resultado", async () => {
    rutasEnLaApi([ruta("EN_EJECUCION")]);
    vi.mocked(api.post).mockResolvedValue({
      lote_id: "lote-2",
      sin_rutas_activas: false,
      mensaje: "",
      hora_considerada: "10:00:00",
      rutas: [],
      sin_cobertura: [{ pedido_id: "99999999-aaaa", motivo: "FLOTA_INSUFICIENTE", sugerencia: "Incorpore más vehículos." }],
      pedidos_nuevos: 2,
      pedidos_retirados: 1,
      incidentes_aplicados: ["Av. Ferrocarril"],
      tiempo_ejecucion_s: 12.3,
      dentro_del_limite: true,
    });
    const usuario = userEvent.setup();
    renderPagina();

    await usuario.type(await screen.findByLabelText(/hora de referencia/i), "10:00");
    await usuario.click(screen.getByRole("button", { name: "Re-optimizar rutas" }));

    await waitFor(() =>
      expect(api.post).toHaveBeenCalledWith("/api/rutas/reoptimizar", { fecha_jornada: expect.any(String), hora_actual: "10:00" }),
    );
    expect(await screen.findByText(/dentro del límite de 30 s/i)).toBeInTheDocument();
    expect(screen.getByText(/2 pedido\(s\) nuevo\(s\) integrado\(s\)/)).toBeInTheDocument();
    expect(screen.getByText(/Incidentes aplicados: Av\. Ferrocarril/)).toBeInTheDocument();
    expect(screen.getByText(/1 pedido\(s\) sin cobertura/)).toBeInTheDocument();
  });

  it("sin rutas activas muestra el mensaje de la API que sugiere generar rutas", async () => {
    rutasEnLaApi([ruta("EN_EJECUCION")]);
    vi.mocked(api.post).mockResolvedValue({
      lote_id: null,
      sin_rutas_activas: true,
      mensaje: "No hay rutas activas para re-optimizar en esa fecha. Genere nuevas rutas desde el módulo de rutas.",
      hora_considerada: null,
      rutas: [],
      sin_cobertura: [],
      pedidos_nuevos: 0,
      pedidos_retirados: 0,
      incidentes_aplicados: [],
      tiempo_ejecucion_s: 0,
      dentro_del_limite: true,
    });
    const usuario = userEvent.setup();
    renderPagina();

    await usuario.click(await screen.findByRole("button", { name: "Re-optimizar rutas" }));
    expect(await screen.findByText(/genere nuevas rutas/i)).toBeInTheDocument();
  });

  it("un borrador de re-optimización se distingue del borrador de una generación", async () => {
    rutasEnLaApi([ruta("PLANIFICADA", { reemplaza_ruta_id: "ruta-original" })]);
    renderPagina();
    expect(await screen.findByText(/re-optimización sin confirmar/i)).toBeInTheDocument();
    expect(screen.queryByText(/borrador sin confirmar/i)).not.toBeInTheDocument();
  });

  const paradasEnCurso: Ruta["paradas"] = [
    { orden: 1, pedido_id: "p1", cliente: "Bodega San José", descripcion: null, peso_kg: "25.00", prioridad: "ESTANDAR", hora_estimada: "08:20:00", minutos_retraso: 0, estado_entrega: "ENTREGADO", pedido_estado: "ENTREGADO" },
    { orden: 2, pedido_id: "p2", cliente: "Calzados Puno", descripcion: null, peso_kg: "40.00", prioridad: "ESTANDAR", hora_estimada: "09:05:00", minutos_retraso: 0, estado_entrega: "PENDIENTE", pedido_estado: "ASIGNADO" },
    { orden: 3, pedido_id: "p3", cliente: "Minimarket Real", descripcion: null, peso_kg: "10.00", prioridad: "ESTANDAR", hora_estimada: "09:40:00", minutos_retraso: 0, estado_entrega: "PENDIENTE", pedido_estado: "CANCELADO" },
  ];

  it("en una ruta en curso se registran las entregas pendientes, no las hechas ni las canceladas", async () => {
    rutasEnLaApi([ruta("EN_EJECUCION")], [], "EN_EJECUCION", paradasEnCurso);
    vi.mocked(api.patch).mockResolvedValue({ ruta_id: "ruta-1", pedido_id: "p2", estado_entrega: "ENTREGADO", estado_ruta: "EN_EJECUCION" });
    const usuario = userEvent.setup();
    renderPagina();

    await usuario.click(await screen.findByRole("button", { name: /ver paradas/i }));
    expect(await screen.findByText("Entregado", { selector: "span" })).toBeInTheDocument();
    expect(screen.getByText("Pedido cancelado")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Marcar entregado Bodega San José" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Marcar entregado Minimarket Real" })).not.toBeInTheDocument();

    await usuario.click(screen.getByRole("button", { name: "Marcar entregado Calzados Puno" }));
    await waitFor(() =>
      expect(api.patch).toHaveBeenCalledWith("/api/rutas/ruta-1/paradas/p2/entrega", { estado: "ENTREGADO" }),
    );
  });

  it("también se puede marcar una entrega como fallida, y el Operador puede registrar entregas", async () => {
    rolActual.valor = "OPERADOR";
    rutasEnLaApi([ruta("CONFIRMADA")], [], "CONFIRMADA", paradasEnCurso);
    vi.mocked(api.patch).mockResolvedValue({ ruta_id: "ruta-1", pedido_id: "p2", estado_entrega: "FALLIDO", estado_ruta: "EN_EJECUCION" });
    const usuario = userEvent.setup();
    renderPagina();

    await usuario.click(await screen.findByRole("button", { name: /ver paradas/i }));
    await usuario.click(await screen.findByRole("button", { name: "Marcar fallido Calzados Puno" }));
    await waitFor(() => expect(api.patch).toHaveBeenCalledWith("/api/rutas/ruta-1/paradas/p2/entrega", { estado: "FALLIDO" }));
  });

  it("un borrador no muestra botones de entrega", async () => {
    rutasEnLaApi([ruta("PLANIFICADA")], [], "PLANIFICADA", paradasEnCurso);
    const usuario = userEvent.setup();
    renderPagina();
    await usuario.click(await screen.findByRole("button", { name: /ver paradas/i }));
    await screen.findByText(/Calzados Puno/);
    expect(screen.queryByRole("button", { name: /marcar entregado/i })).not.toBeInTheDocument();
  });

  // ------------------------------------------------------------------ incidentes de tráfico
  const incidenteActivo = { incidente_id: "inc-1", calle: "Av. Ferrocarril", factor: 3, descripcion: null, activo: true, creado_en: "2026-10-21T10:00:00Z" };

  it("lista los incidentes activos; el Administrador los registra y resuelve", async () => {
    rutasEnLaApi([ruta("CONFIRMADA")], [incidenteActivo]);
    vi.mocked(api.post).mockResolvedValue({});
    vi.mocked(api.delete).mockResolvedValue({});
    const usuario = userEvent.setup();
    renderPagina();

    expect(await screen.findByText(/3 veces más lento/)).toBeInTheDocument();
    await usuario.selectOptions(screen.getByLabelText("Vía"), "Calle Real");
    await usuario.selectOptions(screen.getByLabelText("Congestión"), "5 veces más lento");
    await usuario.click(screen.getByRole("button", { name: "Registrar incidente" }));
    await waitFor(() => expect(api.post).toHaveBeenCalledWith("/api/rutas/incidentes", { calle: "Calle Real", factor: 5 }));

    await usuario.click(screen.getByRole("button", { name: "Resolver incidente de Av. Ferrocarril" }));
    await waitFor(() => expect(api.delete).toHaveBeenCalledWith("/api/rutas/incidentes/inc-1"));
  });

  it("el Operador ve los incidentes pero no puede registrarlos ni resolverlos", async () => {
    rolActual.valor = "OPERADOR";
    rutasEnLaApi([ruta("CONFIRMADA")], [incidenteActivo]);
    renderPagina();

    expect(await screen.findByText(/3 veces más lento/)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Registrar incidente" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /resolver incidente/i })).not.toBeInTheDocument();
  });

  it("sin incidentes lo dice", async () => {
    rutasEnLaApi([ruta("CONFIRMADA")]);
    renderPagina();
    expect(await screen.findByText(/no hay incidentes de tráfico activos/i)).toBeInTheDocument();
  });
});
