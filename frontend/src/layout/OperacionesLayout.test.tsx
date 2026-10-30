import { describe, expect, it, vi } from "vitest";
import { render } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { OperacionesLayout } from "./OperacionesLayout";
import { ConfirmProvider } from "../context/ConfirmContext";
import { ThemeProvider } from "../theme/ThemeContext";

vi.mock("../context/AuthContext", () => ({
  useAuth: () => ({
    usuario: { usuarioId: "u1", email: "prueba@routezero.dev", rolNombre: "ADMINISTRADOR", mfaActivo: false },
    recargarUsuario: vi.fn(),
    cerrarSesion: vi.fn(),
  }),
}));

function renderEn(ruta: string) {
  return render(
    <ThemeProvider>
    <ConfirmProvider>
      <MemoryRouter initialEntries={[ruta]}>
        <Routes>
          <Route path="/app" element={<OperacionesLayout />}>
            <Route path="*" element={<p>contenido</p>} />
          </Route>
          <Route path="*" element={<OperacionesLayout />} />
        </Routes>
      </MemoryRouter>
    </ConfirmProvider>
    </ThemeProvider>,
  );
}

describe("OperacionesLayout: título de cada pantalla (WCAG 2.4.2)", () => {
  it("pone el nombre de la sección en el título del documento", () => {
    renderEn("/app/pedidos");
    expect(document.title).toBe("Pedidos · RouteZero");
  });

  it("cambia el título al pasar a otra sección", () => {
    renderEn("/app/seguridad");
    expect(document.title).toBe("Seguridad · RouteZero");
  });

  it("usa el título general si la ruta no es de una sección", () => {
    renderEn("/otra-ruta");
    expect(document.title).toBe("RouteZero");
  });
});
