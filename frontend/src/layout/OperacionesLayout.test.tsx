import { afterEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { OperacionesLayout } from "./OperacionesLayout";
import { ConfirmProvider } from "../context/ConfirmContext";
import { ThemeProvider } from "../theme/ThemeContext";

const sesion = vi.hoisted(() => ({ rol: "ADMINISTRADOR" }));

vi.mock("../context/AuthContext", () => ({
  useAuth: () => ({
    usuario: { usuarioId: "u1", email: "prueba@routezero.dev", rolNombre: sesion.rol, mfaActivo: false },
    recargarUsuario: vi.fn(),
    cerrarSesion: vi.fn(),
  }),
}));

// La pastilla de CO₂ del encabezado consulta el dashboard de sostenibilidad
vi.mock("../api/client", async (importOriginal) => {
  const real = await importOriginal<typeof import("../api/client")>();
  return { ...real, api: { get: vi.fn().mockResolvedValue({ totales: { emision_co2_kg: 5.5 } }) } };
});

import { api } from "../api/client";

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

describe("OperacionesLayout: CO₂ emitido hoy en el encabezado", () => {
  afterEach(() => {
    sesion.rol = "ADMINISTRADOR";
    vi.mocked(api.get).mockClear();
  });

  it("el administrador ve los kilogramos emitidos hoy", async () => {
    renderEn("/app/mapa");
    expect(await screen.findByLabelText(/^CO2 emitido hoy: 5[.,]5 kilogramos$/)).toBeInTheDocument();
  });

  it("el operador no ve la pastilla ni se consulta el dashboard, que es solo del administrador", () => {
    sesion.rol = "OPERADOR";
    renderEn("/app/mapa");
    expect(screen.queryByText(/kg CO₂/)).not.toBeInTheDocument();
    expect(api.get).not.toHaveBeenCalled();
  });
});
