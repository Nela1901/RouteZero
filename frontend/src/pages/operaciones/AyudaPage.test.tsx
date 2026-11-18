import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { AyudaPage } from "./AyudaPage";

const sesion = vi.hoisted(() => ({ rol: "ADMINISTRADOR" }));

vi.mock("../../context/AuthContext", () => ({
  useAuth: () => ({ usuario: { usuarioId: "u1", email: "prueba@routezero.dev", rolNombre: sesion.rol, mfaActivo: false } }),
}));

describe("AyudaPage", () => {
  it("el administrador ve el título de la pantalla y su guía", () => {
    sesion.rol = "ADMINISTRADOR";
    render(<AyudaPage />);

    expect(screen.getByRole("heading", { name: "Ayuda y primeros pasos", level: 1 })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Primeros pasos como administrador" })).toBeInTheDocument();
    expect(screen.getByText("¿Cuánto tarda en generar las rutas?")).toBeInTheDocument();
  });

  it("el operador ve la guía del operador", () => {
    sesion.rol = "OPERADOR";
    render(<AyudaPage />);

    expect(screen.getByRole("heading", { name: "Primeros pasos como operador" })).toBeInTheDocument();
    expect(screen.queryByText("¿Cuánto tarda en generar las rutas?")).not.toBeInTheDocument();
  });
});
