import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { MapaPage } from "./MapaPage";

// Leaflet necesita un navegador real: se sustituyen sus componentes por contenedores simples
vi.mock("react-leaflet", () => ({
  MapContainer: ({ children }: { children: ReactNode }) => <div data-testid="mapa">{children}</div>,
  TileLayer: () => null,
  CircleMarker: ({ children }: { children: ReactNode }) => <div data-testid="marcador">{children}</div>,
  Popup: ({ children }: { children: ReactNode }) => <div>{children}</div>,
}));
vi.mock("leaflet/dist/leaflet.css", () => ({}));

vi.mock("../../api/client", async (importOriginal) => {
  const real = await importOriginal<typeof import("../../api/client")>();
  return { ...real, api: { post: vi.fn(), get: vi.fn(), put: vi.fn(), delete: vi.fn() } };
});

import { api } from "../../api/client";

const pedido = (i: number) => ({
  pedido_id: `p${i}`,
  prioridad: "ESTANDAR",
  estado: "PENDIENTE",
  latitud: "-12.0653",
  longitud: "-75.2049",
  descripcion: `Pedido ${i}`,
});

describe("MapaPage", () => {
  beforeEach(() => vi.mocked(api.get).mockReset());

  it("dibuja un marcador por pedido del listado paginado (regresión: esperaba una lista y fallaba con `e.map is not a function`)", async () => {
    vi.mocked(api.get).mockResolvedValue({ items: [pedido(1), pedido(2), pedido(3)], total: 3, limite: 200, desplazamiento: 0 });
    render(<MapaPage />);

    await waitFor(() => expect(screen.getAllByTestId("marcador")).toHaveLength(3));
    expect(api.get).toHaveBeenCalledWith("/api/pedidos?limite=200");
  });

  it("con una página vacía muestra el mapa sin marcadores", async () => {
    vi.mocked(api.get).mockResolvedValue({ items: [], total: 0, limite: 200, desplazamiento: 0 });
    render(<MapaPage />);

    expect(await screen.findByTestId("mapa")).toBeInTheDocument();
    await waitFor(() => expect(api.get).toHaveBeenCalledOnce());
    expect(screen.queryAllByTestId("marcador")).toHaveLength(0);
  });
});
