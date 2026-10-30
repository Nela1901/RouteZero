import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { EstadoVencimiento, diasParaVencer } from "./ui";

function fechaEn(dias: number): string {
  const f = new Date();
  f.setDate(f.getDate() + dias);
  const dos = (n: number) => String(n).padStart(2, "0");
  return `${f.getFullYear()}-${dos(f.getMonth() + 1)}-${dos(f.getDate())}`;
}

describe("EstadoVencimiento", () => {
  it("cuenta los días que faltan, con signo negativo si ya venció", () => {
    expect(diasParaVencer(fechaEn(10))).toBe(10);
    expect(diasParaVencer(fechaEn(-3))).toBe(-3);
  });

  it("marca un documento vencido", () => {
    render(<EstadoVencimiento fecha={fechaEn(-1)} />);
    expect(screen.getByText("Vencida")).toBeInTheDocument();
  });

  it("avisa cuántos días faltan si vence dentro de 30 días", () => {
    render(<EstadoVencimiento fecha={fechaEn(12)} />);
    expect(screen.getByText("Vence en 12 d")).toBeInTheDocument();
  });

  it("no muestra aviso si falta más de 30 días", () => {
    render(<EstadoVencimiento fecha={fechaEn(90)} />);
    expect(screen.queryByText(/Vence en|Vencida/)).not.toBeInTheDocument();
  });

  it("muestra un guion si no hay fecha", () => {
    render(<EstadoVencimiento fecha={null} />);
    expect(screen.getByText("—")).toBeInTheDocument();
  });
});
