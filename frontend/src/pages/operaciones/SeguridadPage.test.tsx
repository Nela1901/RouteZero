import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { SeguridadPage } from "./SeguridadPage";
import { ToastProvider } from "../../context/ToastContext";
import { ConfirmProvider } from "../../context/ConfirmContext";

function renderConProviders() {
  return render(
    <ToastProvider>
      <ConfirmProvider>
        <SeguridadPage />
      </ConfirmProvider>
    </ToastProvider>,
  );
}

const recargarUsuario = vi.fn();

vi.mock("../../context/AuthContext", () => ({
  useAuth: () => ({
    usuario: { usuarioId: "u1", email: "prueba@routezero.dev", rolNombre: "ADMINISTRADOR", mfaActivo: false },
    recargarUsuario,
    cerrarSesion: vi.fn(),
  }),
}));

vi.mock("../../api/client", async (importOriginal) => {
  const real = await importOriginal<typeof import("../../api/client")>();
  return {
    ...real,
    api: {
      post: vi.fn(),
      get: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
    },
  };
});

import { api } from "../../api/client";
import { ErrorApi } from "../../api/client";

const QR_SVG = '<svg width="10" height="10"><rect width="10" height="10"/></svg>';

describe("SeguridadPage — inscripción TOTP", () => {
  beforeEach(() => {
    vi.mocked(api.get).mockReset().mockResolvedValue([]);
    vi.mocked(api.post).mockReset();
    recargarUsuario.mockReset().mockResolvedValue(undefined);
  });

  it("con un código válido, confirma la inscripción y recarga al usuario", async () => {
    vi.mocked(api.post).mockImplementation(async (ruta: string) => {
      if (ruta === "/api/auth/mfa/inscribir") {
        return { factor_id: "factor-1", qr_code: QR_SVG, secret: "ABCDEFGHIJKLMNOP" };
      }
      return undefined;
    });
    const usuario = userEvent.setup();

    renderConProviders();

    await usuario.click(screen.getByRole("button", { name: /activar verificación en dos pasos/i }));
    expect(await screen.findByText("Escanea el código QR")).toBeInTheDocument();
    expect(screen.getByText("ABCDEFGHIJKLMNOP")).toBeInTheDocument();

    await usuario.type(screen.getByLabelText(/código de 6 dígitos/i), "123456");
    await usuario.click(screen.getByRole("button", { name: /confirmar y activar/i }));

    await waitFor(() =>
      expect(api.post).toHaveBeenCalledWith("/api/auth/mfa/confirmar", { factor_id: "factor-1", codigo: "123456" }),
    );
    expect(await screen.findByText(/activada correctamente/i)).toBeInTheDocument();
    expect(recargarUsuario).toHaveBeenCalledOnce();
  });

  it("con un código inválido, muestra el error y deja el formulario abierto para reintentar", async () => {
    vi.mocked(api.post).mockImplementation(async (ruta: string) => {
      if (ruta === "/api/auth/mfa/inscribir") {
        return { factor_id: "factor-1", qr_code: QR_SVG, secret: "ABCDEFGHIJKLMNOP" };
      }
      if (ruta === "/api/auth/mfa/confirmar") {
        throw new ErrorApi(400, "Código TOTP inválido");
      }
      return undefined;
    });
    const usuario = userEvent.setup();

    renderConProviders();

    await usuario.click(screen.getByRole("button", { name: /activar verificación en dos pasos/i }));
    await usuario.type(await screen.findByLabelText(/código de 6 dígitos/i), "000000");
    await usuario.click(screen.getByRole("button", { name: /confirmar y activar/i }));

    expect(await screen.findByText("Código TOTP inválido")).toBeInTheDocument();
    // El formulario de confirmación sigue visible: no se perdió el QR ni la inscripción en curso.
    expect(screen.getByText("Escanea el código QR")).toBeInTheDocument();
    expect(recargarUsuario).not.toHaveBeenCalled();
  });
});
