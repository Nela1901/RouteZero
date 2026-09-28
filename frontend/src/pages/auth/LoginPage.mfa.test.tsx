import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { LoginPage } from "./LoginPage";
import { ErrorApi } from "../../api/client";
import { ThemeProvider } from "../../theme/ThemeContext";

function renderLoginPage() {
  return render(
    <ThemeProvider>
      <LoginPage />
    </ThemeProvider>,
  );
}

const confirmarMfa = vi.fn();
const cancelarMfa = vi.fn();

vi.mock("../../context/AuthContext", () => ({
  useAuth: () => ({
    iniciarSesion: vi.fn(),
    mfaPendiente: { mfaToken: "token-parcial", factorId: "factor-123" },
    confirmarMfa,
    cerrarSesion: vi.fn(),
    cancelarMfa,
  }),
}));

describe("LoginPage — verificación de código TOTP en el login", () => {
  beforeEach(() => {
    confirmarMfa.mockReset();
    cancelarMfa.mockReset();
  });

  it("con un código válido, llama a confirmarMfa y no muestra error", async () => {
    confirmarMfa.mockResolvedValueOnce(undefined);
    const usuario = userEvent.setup();

    renderLoginPage();

    const campoCodigo = screen.getByLabelText("Código");
    await usuario.type(campoCodigo, "123456");
    await usuario.click(screen.getByRole("button", { name: /verificar/i }));

    await waitFor(() => expect(confirmarMfa).toHaveBeenCalledWith("123456"));
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  it("con un código inválido, muestra el mensaje de error del backend", async () => {
    confirmarMfa.mockRejectedValueOnce(new ErrorApi(400, "Código TOTP inválido"));
    const usuario = userEvent.setup();

    renderLoginPage();

    const campoCodigo = screen.getByLabelText("Código");
    await usuario.type(campoCodigo, "000000");
    await usuario.click(screen.getByRole("button", { name: /verificar/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Código TOTP inválido");
  });

  it("el botón «Volver a intentar con otra cuenta» llama a cancelarMfa", async () => {
    const usuario = userEvent.setup();
    renderLoginPage();

    await usuario.click(screen.getByRole("button", { name: /volver a intentar con otra cuenta/i }));

    expect(cancelarMfa).toHaveBeenCalledOnce();
  });
});
