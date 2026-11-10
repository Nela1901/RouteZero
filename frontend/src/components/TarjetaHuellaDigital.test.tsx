import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { act, render, screen } from "@testing-library/react";

const medicion = vi.hoisted(() => ({ bytes: 0 }));

vi.mock("./huellaDigital", async (importOriginal) => {
  const real = await importOriginal<typeof import("./huellaDigital")>();
  return { ...real, bytesTransferidos: () => medicion.bytes };
});

import { TarjetaHuellaDigital } from "./TarjetaHuellaDigital";

describe("TarjetaHuellaDigital: huella de carbono de la sesión con SWDM v4", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    medicion.bytes = 143_360; // 140 KB
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("muestra los datos descargados, la energía y la emisión estimada", () => {
    render(<TarjetaHuellaDigital />);

    expect(screen.getByRole("region", { name: /Huella digital de esta sesión/ })).toBeInTheDocument();
    expect(screen.getByText(/^140[.,]0 KB$/)).toBeInTheDocument();
    expect(screen.getByText(/^0[.,]043 Wh$/)).toBeInTheDocument(); // 4.3008 × 10⁻⁵ kWh
    expect(screen.getByText(/^21[.,]2 mg CO₂e$/)).toBeInTheDocument(); // 0.021246 g, igual que CO2.js
  });

  it("compara con la visita promedio calculada en el informe", () => {
    render(<TarjetaHuellaDigital />);

    expect(screen.getByText("Visita promedio (informe de impacto ambiental)")).toBeInTheDocument();
    expect(screen.getByText(/^16[.,]9 mg CO₂e$/)).toBeInTheDocument();
  });

  it("se actualiza cada 5 segundos con lo que se va descargando", () => {
    medicion.bytes = 0;
    render(<TarjetaHuellaDigital />);
    expect(screen.getByText(/^0[.,]0 KB$/)).toBeInTheDocument();

    medicion.bytes = 143_360;
    act(() => {
      vi.advanceTimersByTime(5000);
    });
    expect(screen.getByText(/^140[.,]0 KB$/)).toBeInTheDocument();
  });
});
