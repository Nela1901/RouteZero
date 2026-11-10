import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { SostenibilidadPage, type Compensacion, type Dashboard } from "./SostenibilidadPage";

vi.mock("../../api/client", async (importOriginal) => {
  const real = await importOriginal<typeof import("../../api/client")>();
  return { ...real, api: { post: vi.fn(), get: vi.fn(), put: vi.fn(), patch: vi.fn(), delete: vi.fn(), descargar: vi.fn() } };
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
    { fecha: "2026-10-20", rutas: 1, emision_co2_kg: 10.2, distancia_km: 40, combustible_ahorrado_l: 1, entregadas: 3, fallidas: 0 },
    { fecha: "2026-10-21", rutas: 2, emision_co2_kg: 18.2, distancia_km: 80.5, combustible_ahorrado_l: 1.5, entregadas: 5, fallidas: 1 },
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
    // Los totales también aparecen en la última fila del historial: cada indicador se busca dentro de su tarjeta
    const tarjeta = (etiqueta: string) => within(screen.getByText(etiqueta).parentElement as HTMLElement);
    expect(tarjeta("Distancia recorrida").getByText("120.5")).toBeInTheDocument();
    expect(tarjeta("Emisiones de CO₂").getByText("28.4")).toBeInTheDocument();
    expect(tarjeta("Combustible ahorrado").getByText("2.5")).toBeInTheDocument();
    expect(screen.getByText("96.7")).toBeInTheDocument();
    expect(screen.getByText("S/ 11.25")).toBeInTheDocument();
    expect(screen.getByText("Rutas del periodo").nextElementSibling).toHaveTextContent("3");
    expect(screen.getByText("Entregas realizadas").nextElementSibling).toHaveTextContent("8");
    expect(screen.getByRole("region", { name: "Emisiones de CO₂ por día" })).toBeInTheDocument();
    expect(screen.getByRole("img", { name: /2 días con jornadas, 28\.4 kg en total, promedio de 14\.2 kg por día y máximo de 18\.2 kg/ })).toBeInTheDocument();
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

  it("«Descargar reporte PDF» pide el PDF del periodo y lo descarga", async () => {
    responder(conDatos, plan);
    vi.mocked(api.descargar).mockResolvedValue(new Blob(["%PDF-1.4"], { type: "application/pdf" }));
    const crear = vi.fn(() => "blob:reporte");
    const revocar = vi.fn();
    Object.assign(URL, { createObjectURL: crear, revokeObjectURL: revocar });
    const clic = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => {});
    render(<SostenibilidadPage />);
    await screen.findByText("Distancia recorrida");

    await userEvent.click(screen.getByRole("button", { name: "Descargar reporte PDF" }));

    expect(await screen.findByText("El reporte se descargó.")).toBeInTheDocument();
    expect(api.descargar).toHaveBeenCalledWith(expect.stringMatching(/^\/api\/sostenibilidad\/reporte\?desde=\d{4}-\d{2}-01&hasta=\d{4}-\d{2}-\d{2}$/));
    expect(crear).toHaveBeenCalledTimes(1);
    expect(clic).toHaveBeenCalledTimes(1);
    expect(revocar).toHaveBeenCalledWith("blob:reporte");
    clic.mockRestore();
  });

  it("si el periodo no tiene datos, el reporte muestra el aviso de la API y no descarga nada", async () => {
    responder(sinDatos, planSinDatos);
    vi.mocked(api.descargar).mockRejectedValue(
      new ErrorApi(404, "No hay datos suficientes para generar el reporte en el periodo seleccionado. Seleccione otro periodo."),
    );
    const clic = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => {});
    render(<SostenibilidadPage />);
    await screen.findByText("S/ 0.00");

    await userEvent.click(screen.getByRole("button", { name: "Descargar reporte PDF" }));

    expect(await screen.findByText(/Seleccione otro periodo/)).toBeInTheDocument();
    expect(clic).not.toHaveBeenCalled();
    clic.mockRestore();
  });

  it("si la API falla muestra el error y no los indicadores", async () => {
    vi.mocked(api.get).mockRejectedValue(new ErrorApi(500, "Error interno"));
    render(<SostenibilidadPage />);

    expect(await screen.findByRole("alert")).toHaveTextContent("Error interno");
    expect(screen.queryByText("Distancia recorrida")).not.toBeInTheDocument();
  });

  describe("historial, proyección y comparación de periodos", () => {
    const dia = (n: number, kg: number) => ({
      fecha: `2026-11-${String(n).padStart(2, "0")}`, rutas: 4, emision_co2_kg: kg, distancia_km: 60, combustible_ahorrado_l: 2, entregadas: 30, fallidas: 2,
    });
    const delMes = (porDia: Dashboard["por_dia"], desde = "2026-11-01", hasta = "2026-11-10"): Dashboard => ({ ...conDatos, desde, hasta, por_dia: porDia });

    it("el historial lista cada día, el más reciente primero, con sus rutas, su CO₂ y sus entregas, y el total", async () => {
      responder(conDatos, plan);
      render(<SostenibilidadPage />);

      const tabla = await screen.findByRole("table");
      const filas = within(tabla).getAllByRole("row");
      // encabezado + 2 días + total
      expect(filas).toHaveLength(4);
      expect(within(filas[1]).getByText(/21 oct/)).toBeInTheDocument();
      expect(within(filas[1]).getAllByRole("cell").map((c) => c.textContent)).toEqual(["2", "80.5", "18.2", "1.5", "5 / 1"]);
      expect(within(filas[3]).getAllByRole("cell").map((c) => c.textContent)).toEqual(["3", "120.5", "28.4", "2.5", "8 / 1"]);
    });

    it("con más de 10 días muestra los últimos 10 y permite ver todos", async () => {
      const doce = Array.from({ length: 12 }, (_, i) => dia(i + 1, 20));
      responder(delMes(doce), plan);
      render(<SostenibilidadPage />);

      const tabla = await screen.findByRole("table");
      expect(within(tabla).getAllByRole("row")).toHaveLength(1 + 10 + 1);
      await userEvent.click(screen.getByRole("button", { name: "Ver los 12 días" }));
      expect(within(tabla).getAllByRole("row")).toHaveLength(1 + 12 + 1);
      expect(screen.getByRole("button", { name: "Mostrar solo los últimos 10" })).toBeInTheDocument();
    });

    it("proyecta el cierre del mes y avisa si superaría la meta", async () => {
      // 10 días con 100 kg cada uno = 1000 kg; 1000 / 10 × 30 = 3000 kg contra una meta de 800
      responder(delMes(Array.from({ length: 10 }, (_, i) => dia(i + 1, 100))), plan);
      render(<SostenibilidadPage />);

      const seccion = await screen.findByRole("region", { name: /Proyección de cierre del mes/ });
      expect(within(seccion).getByText(/cerraría en unos 3,000 kg de CO₂, el 375 % de la meta de 800 kg/)).toBeInTheDocument();
      expect(within(seccion).getByText("Supera la meta")).toBeInTheDocument();
    });

    it("si el ritmo queda por debajo de la meta lo dice", async () => {
      responder(delMes([dia(3, 20), dia(4, 20)]), plan);
      render(<SostenibilidadPage />);

      const seccion = await screen.findByRole("region", { name: /Proyección de cierre del mes/ });
      expect(within(seccion).getByText("Dentro de la meta")).toBeInTheDocument();
    });

    it("un mes completo no se proyecta: informa en cuánto cerró", async () => {
      responder(delMes([dia(5, 600)], "2026-10-01", "2026-10-31"), plan);
      render(<SostenibilidadPage />);

      const seccion = await screen.findByRole("region", { name: /Proyección de cierre del mes/ });
      expect(within(seccion).getByText(/El mes cerró en 600 kg de CO₂, el 75 % de la meta de 800 kg/)).toBeInTheDocument();
    });

    it("sin un mes desde el día 1 no hay proyección, pero sí el historial", async () => {
      responder(delMes([dia(8, 50)], "2026-11-05", "2026-11-10"), plan);
      render(<SostenibilidadPage />);

      await screen.findByRole("table");
      expect(screen.queryByRole("region", { name: /Proyección de cierre del mes/ })).not.toBeInTheDocument();
    });

    it("«Mes anterior» consulta el mes calendario anterior completo", async () => {
      responder(conDatos, plan);
      render(<SostenibilidadPage />);
      await screen.findByText("Distancia recorrida");

      await userEvent.click(screen.getByRole("button", { name: "Mes anterior" }));
      await waitFor(() => expect(api.get).toHaveBeenCalledTimes(4));
      const ultima = vi.mocked(api.get).mock.calls[2][0] as string;
      expect(ultima).toMatch(/desde=\d{4}-\d{2}-01&hasta=\d{4}-\d{2}-(28|29|30|31)$/);
      const [desde, hasta] = /desde=([\d-]+)&hasta=([\d-]+)/.exec(ultima)!.slice(1);
      expect(desde.slice(0, 7)).toBe(hasta.slice(0, 7)); // el periodo es un solo mes
    });
  });
});
