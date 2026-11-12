import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { PedidosPage } from "./PedidosPage";
import { ToastProvider } from "../../context/ToastContext";
import { ConfirmProvider } from "../../context/ConfirmContext";

vi.mock("../../api/client", async (importOriginal) => {
  const real = await importOriginal<typeof import("../../api/client")>();
  return { ...real, api: { post: vi.fn(), get: vi.fn(), put: vi.fn(), delete: vi.fn() } };
});

import { api } from "../../api/client";

function pedido(i: number) {
  return {
    pedido_id: `pedido-${i}`,
    cliente_id: "cliente-1",
    descripcion: `Pedido número ${i}`,
    peso_kg: "10.00",
    volumen_m3: null,
    prioridad: "ESTANDAR",
    latitud: "-12.0653",
    longitud: "-75.2049",
    ventana_inicio: "09:00:00",
    ventana_fin: "18:00:00",
    estado: "PENDIENTE",
    creado_en: "2026-10-05T10:00:00Z",
  };
}

const pagina = (desde: number, cantidad: number, total: number) => ({
  items: Array.from({ length: cantidad }, (_, k) => pedido(desde + k)),
  total,
  limite: 12,
  desplazamiento: desde,
});

function renderPagina() {
  return render(
    <ToastProvider>
      <ConfirmProvider>
        <PedidosPage />
      </ConfirmProvider>
    </ToastProvider>,
  );
}

describe("PedidosPage — paginación", () => {
  beforeEach(() => {
    vi.mocked(api.get).mockReset();
  });

  it("con más de 12 pedidos muestra la primera página y el botón para cargar el resto", async () => {
    vi.mocked(api.get).mockImplementation(async (url: string) => {
      if (url === "/api/pedidos") return pagina(0, 12, 20);
      if (url === "/api/clientes") return [{ cliente_id: "cliente-1", nombre: "Calzados Puno", referencia: null }];
      return pagina(12, 8, 20);
    });
    const usuario = userEvent.setup();
    renderPagina();

    expect(await screen.findByText("Pedido número 0")).toBeInTheDocument();
    expect(screen.getByText("Mostrando 12 de 20 pedidos")).toBeInTheDocument();
    expect(screen.queryByText("Pedido número 15")).not.toBeInTheDocument();

    await usuario.click(screen.getByRole("button", { name: "Cargar más (8 restantes)" }));

    await waitFor(() => expect(api.get).toHaveBeenCalledWith("/api/pedidos?desplazamiento=12"));
    expect(await screen.findByText("Pedido número 15")).toBeInTheDocument();
    expect(screen.getByText("Mostrando 20 de 20 pedidos")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /cargar más/i })).not.toBeInTheDocument();
  });

  it("con 12 pedidos o menos no muestra el botón de cargar más", async () => {
    vi.mocked(api.get).mockImplementation(async (url: string) => {
      if (url === "/api/pedidos") return pagina(0, 3, 3);
      return [];
    });
    renderPagina();

    expect(await screen.findByText("Pedido número 2")).toBeInTheDocument();
    expect(screen.getByText("Mostrando 3 de 3 pedidos")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /cargar más/i })).not.toBeInTheDocument();
  });
});
