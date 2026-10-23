import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { SostenibilidadPage, type Compensacion, type Dashboard } from "./SostenibilidadPage";

vi.mock("../../api/client", async (importOriginal) => {
  const real = await importOriginal<typeof import("../../api/client")>();
  return { ...real, api: { post: vi.fn(), get: vi.fn(), put: vi.fn(), patch: vi.fn(), delete: vi.fn() } };
});

import { ErrorApi, api } from "../../api/client";

const conDatos: Dashboard = {
  desde: "2026-10-01",
  hasta: "2026-10-23",
  hay_datos: true,
  mensaje: null,
  totales: {
    rutas: 3,
    distancia_km: 120.5,
    emision_co2_kg: 28.4,
    combustible_l: 14.2,
    combustible_ahorrado_l: 2.5,
    ahorro_soles: 11.25,
    cumplimiento_ventanas_pct: 96.7,
  },
  entregas: { entregadas: 8, pendientes: 3, fallidas: 1 },
  por_dia: [
    { fecha: "2026-10-20", emision_co2_kg: 10.2, distancia_km: 40, combustible_ahorrado_l: 1 },
    { fecha: "2026-10-21", emision_co2_kg: 18.2, distancia_km: 80.5, combustible_ahorrado_l: 1.5 },
  ],
  precio_combustible_soles_l: 4.5,
};

const sinDatos: Dashboard = {
  ...conDatos,
  hay_datos: false,
  mensaje: "No hay jornadas operativas registradas en el periodo seleccionado.",
  totales: { rutas: 0, distancia_km: 0, emision_co2_kg: 0, combustible_l: 0, combustible_ahorrado_l: 0, ahorro_soles: 0, cumplimiento_ventanas_pct: 0 },
  entregas: { entregadas: 0, pendientes: 0, fallidas: 0 },
  por_dia: [],
};

const plan: Compensacion = {
  hay_datos: true,
  mensaje: null,
  emision_co2_kg: 1000,
  toneladas_co2: 1,
  kg_co2_por_arbol_anio: 22,
  arboles_necesarios: 46,
  mes_evaluado: { desde: "2026-10-01", hasta: "2026-10-23", emision_co2_kg: 1000, meta_kg: 800, porcentaje_meta: 125, excede_meta: true },
  acciones: ["Re-optimizar las rutas.", "Reducir jornadas."],
  alianzas: [{ nombre: "Gobierno Regional de Junín y SERFOR", descripcion: "Programas de reforestación." }],
};

const planSinDatos: Compensacion = {
  ...plan,
  hay_datos: false,
  mensaje: "No hay datos suficientes: ejecute al menos una jornada operativa antes de generar el plan.",
  emision_co2_kg: 0,
  toneladas_co2: 0,
  arboles_necesarios: 0,
  mes_evaluado: { ...plan.mes_evaluado, emision_co2_kg: 0, porcentaje_meta: 0, excede_meta: false },
  acciones: [],
  alianzas: [],
};

/** Responde cada URL con su dato: la pantalla consulta el dashboard y el plan de compensación a la vez. */
function responder(dashboard: Dashboard, compensacion: Compensacion) {
  vi.mocked(api.get).mockImplementation(async (ruta: string) => (ruta.includes("/compensacion") ? compensacion : dashboard) as never);
}

describe("SostenibilidadPage", () => {
  beforeEach(() => {
    vi.mocked(api.get).mockReset();
  });

  it("muestra los cinco indicadores, las entregas y el gráfico por día", async () => {
    responder(conDatos, plan);
    render(<SostenibilidadPage />);

    expect(await screen.findByText("Distancia recorrida")).toBeInTheDocument();
    expect(screen.getByText("120.5")).toBeInTheDocument();
    expect(screen.getByText("28.4")).toBeInTheDocument();
    expect(screen.getByText("2.5")).toBeInTheDocument();
    expect(screen.getByText("96.7")).toBeInTheDocument();
    expect(screen.getByText("S/ 11.25")).toBeInTheDocument();
    expect(screen.getByText("Rutas del periodo").nextElementSibling).toHaveTextContent("3");
    expect(screen.getByText("Entregas realizadas").nextElementSibling).toHaveTextContent("8");
    expect(screen.getByText("10.2 kg")).toBeInTheDocument();
    expect(screen.queryByRole("status")).not.toBeInTheDocument();
    expect(vi.mocked(api.get).mock.calls[0][0]).toMatch(/^\/api\/sostenibilidad\/dashboard\?desde=\d{4}-\d{2}-01&hasta=\d{4}-\d{2}-\d{2}$/);
  });

  it("sin jornadas muestra los valores en cero y el mensaje del periodo", async () => {
    responder(sinDatos, planSinDatos);
    render(<SostenibilidadPage />);

    expect(await screen.findByText("No hay jornadas operativas registradas en el periodo seleccionado.")).toBeInTheDocument();
    expect(screen.getByText("S/ 0.00")).toBeInTheDocument();
    expect(screen.queryByText("Emisiones de CO₂ por día")).not.toBeInTheDocument();
  });

  it("cambiar el atajo del periodo vuelve a consultar con las nuevas fechas", async () => {
    responder(conDatos, plan);
    render(<SostenibilidadPage />);
    await screen.findByText("Distancia recorrida");

    await userEvent.click(screen.getByRole("button", { name: "Hoy" }));
    await waitFor(() => expect(api.get).toHaveBeenCalledTimes(4));
    const [, hasta] = /desde=([\d-]+)&hasta=([\d-]+)/.exec(vi.mocked(api.get).mock.calls[2][0] as string)!.slice(1);
    expect(vi.mocked(api.get).mock.calls[2][0]).toContain(`desde=${hasta}`);
  });

  it("muestra los árboles necesarios, la alerta de la meta con sus acciones y las alianzas", async () => {
    responder(conDatos, plan);
    render(<SostenibilidadPage />);

    expect(await screen.findByText("46")).toBeInTheDocument();
    expect(screen.getByText(/árboles para compensar 1,000\.0 kg de CO₂/)).toBeInTheDocument();
    expect(screen.getByRole("alert")).toHaveTextContent("superan la meta");
    expect(screen.getByText("Re-optimizar las rutas.")).toBeInTheDocument();
    expect(screen.getByText(/Gobierno Regional de Junín y SERFOR\./)).toBeInTheDocument();
  });

  it("sin emisiones el plan pide ejecutar una jornada y no muestra alerta ni alianzas", async () => {
    responder(sinDatos, planSinDatos);
    render(<SostenibilidadPage />);

    expect(await screen.findByText(/ejecute al menos una jornada operativa/)).toBeInTheDocument();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
    expect(screen.queryByText(/Alianzas de reforestación/)).not.toBeInTheDocument();
  });

  it("si la API falla muestra el error y no los indicadores", async () => {
    vi.mocked(api.get).mockRejectedValue(new ErrorApi(500, "Error interno"));
    render(<SostenibilidadPage />);

    expect(await screen.findByRole("alert")).toHaveTextContent("Error interno");
    expect(screen.queryByText("Distancia recorrida")).not.toBeInTheDocument();
  });
});
