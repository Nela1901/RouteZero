import { describe, expect, it } from "vitest";
import { diasDelMes, proyeccionDelMes } from "./proyeccionMes";

describe("proyeccionMes: cierre estimado del mes", () => {
  it("cuenta los días del calendario, también en febrero de un año bisiesto", () => {
    expect(diasDelMes(2026, 11)).toBe(30);
    expect(diasDelMes(2026, 10)).toBe(31);
    expect(diasDelMes(2026, 2)).toBe(28);
    expect(diasDelMes(2028, 2)).toBe(29);
  });

  it("acumula día a día y proyecta el cierre con el promedio del calendario transcurrido", () => {
    // Del 1 al 10 de noviembre (30 días): 100 kg el día 2, 50 kg el día 5 y 30 kg el día 10
    const porDia = [
      { fecha: "2026-11-02", emision_co2_kg: 100 },
      { fecha: "2026-11-05", emision_co2_kg: 50 },
      { fecha: "2026-11-10", emision_co2_kg: 30 },
    ];
    const p = proyeccionDelMes(porDia, "2026-11-01", "2026-11-10")!;

    expect(p.diasDelMes).toBe(30);
    expect(p.diaActual).toBe(10);
    expect(p.acumulado).toHaveLength(10);
    expect(p.acumulado[0]).toEqual({ dia: 1, kg: 0 });
    expect(p.acumulado[1]).toEqual({ dia: 2, kg: 100 });
    expect(p.acumulado[4]).toEqual({ dia: 5, kg: 150 });
    expect(p.acumulado[9]).toEqual({ dia: 10, kg: 180 });
    expect(p.emisionAcumulada).toBe(180);
    expect(p.proyeccionKg).toBeCloseTo(540, 6); // 180 kg en 10 días → 18 kg por día × 30 días
    expect(p.cierraEnKg).toBeCloseTo(540, 6);
  });

  it("si el mes ya terminó no hay proyección: cierra en lo acumulado", () => {
    const p = proyeccionDelMes([{ fecha: "2026-10-15", emision_co2_kg: 420.5 }, { fecha: "2026-10-31", emision_co2_kg: 10 }], "2026-10-01", "2026-10-31")!;
    expect(p.diaActual).toBe(31);
    expect(p.proyeccionKg).toBeNull();
    expect(p.cierraEnKg).toBeCloseTo(430.5, 6);
  });

  it("un mes sin emisiones proyecta cero", () => {
    const p = proyeccionDelMes([], "2026-11-01", "2026-11-10")!;
    expect(p.emisionAcumulada).toBe(0);
    expect(p.proyeccionKg).toBe(0);
  });

  it("solo aplica a «el mes desde el día 1 hasta una fecha del mismo mes»", () => {
    expect(proyeccionDelMes([], "2026-11-05", "2026-11-10")).toBeNull(); // no empieza el día 1
    expect(proyeccionDelMes([], "2026-10-01", "2026-11-10")).toBeNull(); // abarca dos meses
    expect(proyeccionDelMes([], "2025-11-01", "2026-11-10")).toBeNull(); // mismo mes de otro año
  });
});
