import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { SeguridadPage } from "./SeguridadPage";
import { ToastProvider } from "../../context/ToastContext";
import { ConfirmProvider } from "../../context/ConfirmContext";

const auth = vi.hoisted(() => ({
  mfaActivo: false,
  cerrarSesion: vi.fn(),
  recargarUsuario: vi.fn(),
}));

vi.mock("../../context/AuthContext", () => ({
  useAuth: () => ({
    usuario: { usuarioId: "u1", email: "prueba@routezero.dev", rolNombre: "ADMINISTRADOR", mfaActivo: auth.mfaActivo },
    recargarUsuario: auth.recargarUsuario,
    cerrarSesion: auth.cerrarSesion,
  }),
}));

vi.mock("../../api/client", async (importOriginal) => {
  const real = await importOriginal<typeof import("../../api/client")>();
  return { ...real, api: { post: vi.fn(), get: vi.fn(), put: vi.fn(), delete: vi.fn() } };
});

import { api, ErrorApi } from "../../api/client";

const sesion = (id: string, dispositivo: string | null, actual: boolean) => ({
  sesion_id: id,
  dispositivo_info: dispositivo,
  ip_origen: "190.8.1.1",
  creado_en: "2026-10-28T10:00:00Z",
  ultimo_uso_en: "2026-10-29T10:00:00Z",
  actual,
});

function renderizar() {
  return render(
    <ToastProvider>
      <ConfirmProvider>
        <SeguridadPage />
      </ConfirmProvider>
    </ToastProvider>,
  );
}

beforeEach(() => {
  auth.mfaActivo = false;
  auth.cerrarSesion.mockReset();
  auth.recargarUsuario.mockReset();
  vi.mocked(api.get).mockReset();
  vi.mocked(api.post).mockReset();
  vi.mocked(api.delete).mockReset();
});

describe("Seguridad: verificación en dos pasos", () => {
  it("con el MFA activo informa que la verificación está activa y no ofrece activarla", async () => {
    auth.mfaActivo = true;
    vi.mocked(api.get).mockResolvedValue([]);
    renderizar();

    expect(await screen.findByText("Verificación en dos pasos activa")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /activar verificación en dos pasos/i })).not.toBeInTheDocument();
  });

  it("si no se puede iniciar la inscripción muestra el motivo", async () => {
    vi.mocked(api.get).mockResolvedValue([]);
    vi.mocked(api.post).mockRejectedValue(new ErrorApi(409, "Ya hay una inscripción en curso"));
    const usuario = userEvent.setup();
    renderizar();

    await usuario.click(screen.getByRole("button", { name: /activar verificación en dos pasos/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Ya hay una inscripción en curso");
  });

  it("cancelar la inscripción vuelve al botón para activarla", async () => {
    vi.mocked(api.get).mockResolvedValue([]);
    vi.mocked(api.post).mockResolvedValue({ factor_id: "factor-1", qr_code: "<svg></svg>", secret: "ABCDEFGHIJKLMNOP" });
    const usuario = userEvent.setup();
    renderizar();

    await usuario.click(screen.getByRole("button", { name: /activar verificación en dos pasos/i }));
    await usuario.click(await screen.findByRole("button", { name: "Cancelar" }));

    expect(await screen.findByRole("button", { name: /activar verificación en dos pasos/i })).toBeInTheDocument();
  });
});

describe("Seguridad: sesiones activas", () => {
  const dos = [sesion("s1", "Chrome en Windows", true), sesion("s2", "Safari en iPhone", false)];

  it("sin sesiones lo indica", async () => {
    vi.mocked(api.get).mockResolvedValue([]);
    renderizar();

    expect(await screen.findByText("No hay sesiones activas.")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Cerrar todas" })).not.toBeInTheDocument();
  });

  it("si las sesiones no cargan muestra una alerta", async () => {
    vi.mocked(api.get).mockRejectedValue(new Error("sin red"));
    renderizar();

    expect(await screen.findByRole("alert")).toHaveTextContent("No se pudieron cargar las sesiones");
  });

  it("la sesión actual no se puede cerrar desde la lista y las demás sí", async () => {
    vi.mocked(api.get).mockResolvedValue(dos);
    renderizar();

    expect(await screen.findByText("Chrome en Windows")).toBeInTheDocument();
    expect(screen.getByText("Safari en iPhone")).toBeInTheDocument();
    expect(screen.getAllByRole("button", { name: "Cerrar sesión" })).toHaveLength(1);
  });

  it("cerrar otra sesión pide confirmación, la revoca y avisa", async () => {
    vi.mocked(api.get).mockResolvedValue(dos);
    vi.mocked(api.delete).mockResolvedValue(undefined);
    const usuario = userEvent.setup();
    renderizar();

    await usuario.click(await screen.findByRole("button", { name: "Cerrar sesión" }));
    await usuario.click(within(await screen.findByRole("alertdialog")).getByRole("button", { name: "Cerrar sesión" }));

    await waitFor(() => expect(api.delete).toHaveBeenCalledWith("/api/auth/sesiones/s2"));
    expect(await screen.findByText("Sesión cerrada")).toBeInTheDocument();
  });

  it("si cierra la confirmación no se revoca nada", async () => {
    vi.mocked(api.get).mockResolvedValue(dos);
    const usuario = userEvent.setup();
    renderizar();

    await usuario.click(await screen.findByRole("button", { name: "Cerrar sesión" }));
    await usuario.click(within(await screen.findByRole("alertdialog")).getByRole("button", { name: "Cancelar" }));

    expect(api.delete).not.toHaveBeenCalled();
  });

  it("si la revocación falla muestra el motivo", async () => {
    vi.mocked(api.get).mockResolvedValue(dos);
    vi.mocked(api.delete).mockRejectedValue(new ErrorApi(404, "La sesión ya no existe"));
    const usuario = userEvent.setup();
    renderizar();

    await usuario.click(await screen.findByRole("button", { name: "Cerrar sesión" }));
    await usuario.click(within(await screen.findByRole("alertdialog")).getByRole("button", { name: "Cerrar sesión" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("La sesión ya no existe");
  });

  it("cerrar todas las sesiones pide confirmación y cierra la sesión actual", async () => {
    vi.mocked(api.get).mockResolvedValue(dos);
    auth.cerrarSesion.mockResolvedValue(undefined);
    const usuario = userEvent.setup();
    renderizar();

    await usuario.click(await screen.findByRole("button", { name: "Cerrar todas" }));
    await usuario.click(within(await screen.findByRole("alertdialog")).getByRole("button", { name: "Cerrar todas" }));

    await waitFor(() => expect(auth.cerrarSesion).toHaveBeenCalledOnce());
  });
});
