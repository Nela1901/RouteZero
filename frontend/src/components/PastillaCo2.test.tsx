import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";

vi.mock("../api/client", async (importOriginal) => {
  const real = await importOriginal<typeof import("../api/client")>();
  return { ...real, api: { get: vi.fn() } };
});

import { api } from "../api/client";
import { PastillaCo2 } from "./PastillaCo2";

const obtener = vi.mocked(api.get);

describe("PastillaCo2: CO₂ emitido hoy en el encabezado", () => {
  beforeEach(() => {
    obtener.mockReset();
  });

  it("muestra los kilogramos que emitieron hoy las rutas", async () => {
    obtener.mockResolvedValue({ totales: { emision_co2_kg: 12.34 } });
    render(<PastillaCo2 />);

    expect(await screen.findByText(/^12[.,]3 kg CO₂$/)).toBeInTheDocument();
    expect(screen.getByLabelText(/^CO2 emitido hoy: 12[.,]3 kilogramos$/)).toBeInTheDocument();
    expect(screen.getByText("emitidos hoy")).toBeInTheDocument();
  });

  it("consulta solo el día de hoy, una vez", async () => {
    obtener.mockResolvedValue({ totales: { emision_co2_kg: 0 } });
    render(<PastillaCo2 />);

    await screen.findByText(/^0[.,]0 kg CO₂$/);
    expect(obtener).toHaveBeenCalledTimes(1);
    expect(obtener).toHaveBeenCalledWith(expect.stringMatching(/^\/api\/sostenibilidad\/dashboard\?desde=(\d{4}-\d{2}-\d{2})&hasta=\1$/));
  });

  it("mientras carga muestra puntos suspensivos", () => {
    obtener.mockReturnValue(new Promise(() => undefined));
    render(<PastillaCo2 />);

    expect(screen.getByText("… kg CO₂")).toBeInTheDocument();
    expect(screen.getByLabelText("CO2 emitido hoy: sin dato")).toBeInTheDocument();
  });

  it("si no puede cargar el dato muestra una raya y lo explica", async () => {
    obtener.mockRejectedValue(new Error("sin conexión"));
    render(<PastillaCo2 />);

    const pastilla = await screen.findByText("— kg CO₂");
    expect(pastilla.closest("output")).toHaveAttribute("title", "No se pudo cargar el dato de hoy");
  });
});
