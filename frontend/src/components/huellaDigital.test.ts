import { afterEach, describe, expect, it, vi } from "vitest";
import { KWH_POR_GB, emisionG, energiaKwh } from "./huellaDigital";

describe("huellaDigital: modelo SWDM v4", () => {
  it("suma la energía operativa (0.194) y la incorporada (0.106) en 0.300 kWh por GB", () => {
    expect(KWH_POR_GB).toBeCloseTo(0.3, 10);
  });

  // Valores de `new co2({ model: "swd", version: 4 }).perByte(bytes)` de CO2.js 0.16.9 (1 KB = 1024 bytes, 1 GB = 10⁹ bytes)
  it.each([
    [140, 0.021246],
    [171, 0.02595],
    [213, 0.032324],
    [244, 0.037029],
  ])("una carga de %i KB emite %f g CO₂e, igual que CO2.js", (kb, esperado) => {
    expect(emisionG(kb * 1024)).toBeCloseTo(esperado, 6);
  });

  it("calcula la energía en kWh: 213 KB son 6.543 × 10⁻⁵ kWh", () => {
    expect(energiaKwh(213 * 1024)).toBeCloseTo(6.543e-5, 8);
  });

  it("sin datos transferidos no hay energía ni emisión", () => {
    expect(energiaKwh(0)).toBe(0);
    expect(emisionG(0)).toBe(0);
  });
});

describe("huellaDigital: medición de lo descargado", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.resetModules();
  });

  it("suma el tamaño transferido de cada recurso y no cuenta los que informan 0 (caché o de otro dominio)", async () => {
    let avisar: (lista: { getEntries: () => { transferSize: number }[] }) => void = () => undefined;
    const observar = vi.fn();
    vi.stubGlobal(
      "PerformanceObserver",
      class {
        constructor(callback: typeof avisar) {
          avisar = callback;
        }
        observe = observar;
      },
    );
    const modulo = await import("./huellaDigital");
    modulo.iniciarMedicionDeTransferencia();
    modulo.iniciarMedicionDeTransferencia(); // idempotente
    avisar({ getEntries: () => [{ transferSize: 2048 }, { transferSize: 0 }, { transferSize: 1024 }] });

    expect(modulo.bytesTransferidos()).toBe(3072);
    expect(observar).toHaveBeenCalledTimes(2);
    expect(observar).toHaveBeenCalledWith({ type: "navigation", buffered: true });
    expect(observar).toHaveBeenCalledWith({ type: "resource", buffered: true });
  });

  it("sin soporte de PerformanceObserver no falla y queda en cero", async () => {
    vi.stubGlobal("PerformanceObserver", undefined);
    const modulo = await import("./huellaDigital");
    expect(() => modulo.iniciarMedicionDeTransferencia()).not.toThrow();
    expect(modulo.bytesTransferidos()).toBe(0);
  });

  it("si el navegador no admite un tipo de medición, lo ignora", async () => {
    vi.stubGlobal(
      "PerformanceObserver",
      class {
        observe() {
          throw new TypeError("tipo no admitido");
        }
      },
    );
    const modulo = await import("./huellaDigital");
    expect(() => modulo.iniciarMedicionDeTransferencia()).not.toThrow();
    expect(modulo.bytesTransferidos()).toBe(0);
  });
});
