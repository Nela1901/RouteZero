import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactElement } from "react";
import { ClientesPage } from "./ClientesPage";
import { ConductoresPage } from "./ConductoresPage";
import { FlotaPage } from "./FlotaPage";
import { PedidosPage } from "./PedidosPage";
import { ToastProvider } from "../../context/ToastContext";
import { ConfirmProvider } from "../../context/ConfirmContext";

// El selector de ubicación usa un mapa de Leaflet, que necesita un navegador real.
vi.mock("../../components/SelectorUbicacion", () => ({ SelectorUbicacion: () => <div>Selector de ubicación</div> }));

vi.mock("../../api/client", async (importOriginal) => {
  const real = await importOriginal<typeof import("../../api/client")>();
  return { ...real, api: { post: vi.fn(), get: vi.fn(), put: vi.fn(), delete: vi.fn() } };
});

import { api, ErrorApi } from "../../api/client";

const cliente = {
  cliente_id: "cliente-1",
  nombre: "Bodega San José",
  tipo_negocio: "BODEGA",
  referencia: "Frente al mercado",
  latitud: "-12.06530000",
  longitud: "-75.20490000",
  horario_inicio: "08:00:00",
  horario_fin: "18:00:00",
  creado_en: "2026-10-05T10:00:00Z",
};

const vehiculo = {
  vehiculo_id: "vehiculo-1",
  placa: "ABC-123",
  tipo: "CAMIONETA",
  capacidad_kg: "900.00",
  consumo_km_l: "9.50",
  factor_emision_co2: "2.3100",
  anio_fabricacion: 2021,
  estado: "DISPONIBLE",
  soat_vence: "2027-05-01",
  revision_tecnica_vence: null,
};

const conductor = {
  conductor_id: "conductor-1",
  nombre: "Carlos Mendoza",
  dni: "70000001",
  categoria_licencia: "A-IIb",
  telefono: "964100001",
  correo: null,
  licencia_vence: "2028-01-01",
  horario_inicio: "06:00:00",
  horario_fin: "14:00:00",
  disponible: true,
  horas_conducidas_hoy: "0.00",
  consentimiento_en: "2026-10-01T10:00:00Z",
};

const pedido = (estado: string) => ({
  pedido_id: "pedido-1",
  cliente_id: "cliente-1",
  descripcion: "Diez cajas de gaseosa",
  peso_kg: "40.00",
  volumen_m3: null,
  prioridad: "ESTANDAR",
  latitud: "-12.0653",
  longitud: "-75.2049",
  ventana_inicio: "08:00:00",
  ventana_fin: "12:00:00",
  estado,
  creado_en: "2026-10-05T10:00:00Z",
});

function renderizar(pagina: ReactElement) {
  return render(
    <ToastProvider>
      <ConfirmProvider>{pagina}</ConfirmProvider>
    </ToastProvider>,
  );
}

function responder(rutas: Record<string, unknown>) {
  vi.mocked(api.get).mockImplementation(async (url: string) => {
    if (url in rutas) return rutas[url];
    throw new Error(`GET sin simular: ${url}`);
  });
}

beforeEach(() => {
  vi.mocked(api.get).mockReset();
  vi.mocked(api.put).mockReset();
  vi.mocked(api.delete).mockReset();
});

describe("Clientes: detalle, edición y eliminación", () => {
  beforeEach(() => responder({ "/api/clientes": [cliente] }));

  it("el ícono de ver abre el detalle con los datos del cliente", async () => {
    const usuario = userEvent.setup();
    renderizar(<ClientesPage />);

    await usuario.click(await screen.findByRole("button", { name: "Ver detalle de Bodega San José" }));

    const dialogo = await screen.findByRole("dialog", { name: "Bodega San José" });
    expect(within(dialogo).getByText("Frente al mercado")).toBeInTheDocument();
    expect(within(dialogo).getByText("-12.06530000, -75.20490000")).toBeInTheDocument();
    await usuario.keyboard("{Escape}");
    await waitFor(() => expect(screen.queryByRole("dialog")).not.toBeInTheDocument());
  });

  it("al editar envía solo los campos que cambiaron", async () => {
    vi.mocked(api.put).mockResolvedValue({});
    const usuario = userEvent.setup();
    renderizar(<ClientesPage />);

    await usuario.click(await screen.findByRole("button", { name: "Editar Bodega San José" }));
    const dialogo = await screen.findByRole("dialog");
    const nombre = within(dialogo).getByLabelText("Nombre del negocio");
    await usuario.clear(nombre);
    await usuario.type(nombre, "Bodega San José Norte");
    await usuario.click(within(dialogo).getByRole("button", { name: "Guardar cambios" }));

    await waitFor(() =>
      expect(api.put).toHaveBeenCalledWith("/api/clientes/cliente-1", { nombre: "Bodega San José Norte" }),
    );
  });

  it("sin cambios no llama a la API y avisa", async () => {
    const usuario = userEvent.setup();
    renderizar(<ClientesPage />);

    await usuario.click(await screen.findByRole("button", { name: "Editar Bodega San José" }));
    await usuario.click(within(await screen.findByRole("dialog")).getByRole("button", { name: "Guardar cambios" }));

    expect(await screen.findByText("No hay cambios para guardar")).toBeInTheDocument();
    expect(api.put).not.toHaveBeenCalled();
  });

  it("eliminar pide confirmación y borra el cliente", async () => {
    vi.mocked(api.delete).mockResolvedValue(undefined);
    const usuario = userEvent.setup();
    renderizar(<ClientesPage />);

    await usuario.click(await screen.findByRole("button", { name: "Eliminar Bodega San José" }));
    await usuario.click(await screen.findByRole("button", { name: "Eliminar" }));

    await waitFor(() => expect(api.delete).toHaveBeenCalledWith("/api/clientes/cliente-1"));
    expect(await screen.findByText("Cliente eliminado")).toBeInTheDocument();
  });

  it("si cancela la confirmación no borra nada", async () => {
    const usuario = userEvent.setup();
    renderizar(<ClientesPage />);

    await usuario.click(await screen.findByRole("button", { name: "Eliminar Bodega San José" }));
    await usuario.click(await screen.findByRole("button", { name: "Cancelar" }));

    expect(api.delete).not.toHaveBeenCalled();
  });

  it("si el cliente tiene pedidos muestra el motivo que devuelve la API", async () => {
    vi.mocked(api.delete).mockRejectedValue(
      new ErrorApi(409, "El cliente tiene pedidos registrados y no se puede eliminar"),
    );
    const usuario = userEvent.setup();
    renderizar(<ClientesPage />);

    await usuario.click(await screen.findByRole("button", { name: "Eliminar Bodega San José" }));
    await usuario.click(await screen.findByRole("button", { name: "Eliminar" }));

    expect(await screen.findByText("El cliente tiene pedidos registrados y no se puede eliminar")).toBeInTheDocument();
  });
});

describe("Flota: detalle, edición y eliminación", () => {
  beforeEach(() => responder({ "/api/vehiculos": [vehiculo] }));

  it("el detalle muestra capacidad, consumo y documentos", async () => {
    const usuario = userEvent.setup();
    renderizar(<FlotaPage />);

    await usuario.click(await screen.findByRole("button", { name: "Ver detalle de ABC-123" }));

    const dialogo = await screen.findByRole("dialog", { name: "Vehículo ABC-123" });
    expect(within(dialogo).getByText("900.00 kg")).toBeInTheDocument();
    expect(within(dialogo).getByText("9.50 km/L")).toBeInTheDocument();
  });

  it("al editar la placa y la capacidad envía solo esos campos", async () => {
    vi.mocked(api.put).mockResolvedValue({});
    const usuario = userEvent.setup();
    renderizar(<FlotaPage />);

    await usuario.click(await screen.findByRole("button", { name: "Editar ABC-123" }));
    const dialogo = await screen.findByRole("dialog");
    const placa = within(dialogo).getByLabelText("Placa");
    await usuario.clear(placa);
    await usuario.type(placa, "xyz-789");
    const capacidad = within(dialogo).getByLabelText("Capacidad (kg)");
    await usuario.clear(capacidad);
    await usuario.type(capacidad, "1200");
    await usuario.click(within(dialogo).getByRole("button", { name: "Guardar cambios" }));

    await waitFor(() =>
      expect(api.put).toHaveBeenCalledWith("/api/vehiculos/vehiculo-1", { placa: "XYZ-789", capacidad_kg: "1200" }),
    );
  });

  it("un vehículo con rutas no se elimina y se muestra el motivo", async () => {
    vi.mocked(api.delete).mockRejectedValue(
      new ErrorApi(409, "El vehículo tiene rutas registradas y no se puede eliminar"),
    );
    const usuario = userEvent.setup();
    renderizar(<FlotaPage />);

    await usuario.click(await screen.findByRole("button", { name: "Eliminar ABC-123" }));
    await usuario.click(await screen.findByRole("button", { name: "Eliminar" }));

    expect(await screen.findByText("El vehículo tiene rutas registradas y no se puede eliminar")).toBeInTheDocument();
  });
});

describe("Conductores: detalle, edición y eliminación", () => {
  beforeEach(() => responder({ "/api/conductores": [conductor] }));

  it("el detalle muestra la licencia y el consentimiento", async () => {
    const usuario = userEvent.setup();
    renderizar(<ConductoresPage />);

    await usuario.click(await screen.findByRole("button", { name: "Ver detalle de Carlos Mendoza" }));

    const dialogo = await screen.findByRole("dialog", { name: "Carlos Mendoza" });
    expect(within(dialogo).getByText("70000001")).toBeInTheDocument();
    expect(within(dialogo).getByText("Consentimiento de datos")).toBeInTheDocument();
  });

  it("al editar no pide de nuevo el consentimiento y envía solo lo cambiado", async () => {
    vi.mocked(api.put).mockResolvedValue({});
    const usuario = userEvent.setup();
    renderizar(<ConductoresPage />);

    await usuario.click(await screen.findByRole("button", { name: "Editar Carlos Mendoza" }));
    const dialogo = await screen.findByRole("dialog");
    expect(within(dialogo).queryByRole("checkbox")).not.toBeInTheDocument();

    const telefono = within(dialogo).getByLabelText("Teléfono de contacto");
    await usuario.clear(telefono);
    await usuario.type(telefono, "964999999");
    await usuario.click(within(dialogo).getByRole("button", { name: "Guardar cambios" }));

    await waitFor(() =>
      expect(api.put).toHaveBeenCalledWith("/api/conductores/conductor-1", { telefono: "964999999" }),
    );
  });

  it("el teléfono solo acepta dígitos y hasta 9", async () => {
    const usuario = userEvent.setup();
    renderizar(<ConductoresPage />);

    await usuario.click(await screen.findByRole("button", { name: "Editar Carlos Mendoza" }));
    const telefono = within(await screen.findByRole("dialog")).getByLabelText("Teléfono de contacto");
    await usuario.clear(telefono);
    await usuario.type(telefono, "9a8 7-6543210099");

    expect(telefono).toHaveValue("987654321");
  });

  it("eliminar pide confirmación y borra al conductor", async () => {
    vi.mocked(api.delete).mockResolvedValue(undefined);
    const usuario = userEvent.setup();
    renderizar(<ConductoresPage />);

    await usuario.click(await screen.findByRole("button", { name: "Eliminar Carlos Mendoza" }));
    await usuario.click(await screen.findByRole("button", { name: "Eliminar" }));

    await waitFor(() => expect(api.delete).toHaveBeenCalledWith("/api/conductores/conductor-1"));
  });
});

describe("Pedidos: edición y cancelación", () => {
  function simular(estado: string) {
    responder({
      "/api/pedidos": { items: [pedido(estado)], total: 1, limite: 50, desplazamiento: 0 },
      "/api/clientes": [{ cliente_id: "cliente-1", nombre: "Bodega San José", referencia: null }],
    });
  }

  it("un pedido pendiente se puede ver, editar y cancelar", async () => {
    simular("PENDIENTE");
    renderizar(<PedidosPage />);

    expect(await screen.findByRole("button", { name: "Ver detalle de Diez cajas de gaseosa" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Editar Diez cajas de gaseosa" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Cancelar Diez cajas de gaseosa" })).toBeInTheDocument();
  });

  it("un pedido asignado solo se puede ver", async () => {
    simular("ASIGNADO");
    renderizar(<PedidosPage />);

    expect(await screen.findByRole("button", { name: "Ver detalle de Diez cajas de gaseosa" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Editar Diez cajas de gaseosa" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Cancelar Diez cajas de gaseosa" })).not.toBeInTheDocument();
  });

  it("al editar el peso envía solo ese campo", async () => {
    simular("PENDIENTE");
    vi.mocked(api.put).mockResolvedValue({});
    const usuario = userEvent.setup();
    renderizar(<PedidosPage />);

    await usuario.click(await screen.findByRole("button", { name: "Editar Diez cajas de gaseosa" }));
    const dialogo = await screen.findByRole("dialog", { name: "Editar pedido" });
    const peso = within(dialogo).getByLabelText("Peso (kg)");
    await usuario.clear(peso);
    await usuario.type(peso, "55.5");
    await usuario.click(within(dialogo).getByRole("button", { name: "Guardar cambios" }));

    await waitFor(() => expect(api.put).toHaveBeenCalledWith("/api/pedidos/pedido-1", { peso_kg: "55.5" }));
  });
});

describe("Campos de texto y numéricos de los formularios", () => {
  it("el nombre del conductor no admite números ni signos", async () => {
    responder({ "/api/conductores": [conductor] });
    const usuario = userEvent.setup();
    renderizar(<ConductoresPage />);

    await usuario.click(await screen.findByRole("button", { name: "Editar Carlos Mendoza" }));
    const nombre = within(await screen.findByRole("dialog")).getByLabelText("Nombre completo");
    await usuario.clear(nombre);
    await usuario.type(nombre, "Sara 12 Hernán_@ Cañari");

    expect(nombre).toHaveValue("Sara  Hernán Cañari");
  });

  it("el nombre de un negocio admite números pero no signos raros", async () => {
    responder({ "/api/clientes": [cliente] });
    const usuario = userEvent.setup();
    renderizar(<ClientesPage />);

    await usuario.click(await screen.findByRole("button", { name: "Editar Bodega San José" }));
    const nombre = within(await screen.findByRole("dialog")).getByLabelText("Nombre del negocio");
    await usuario.clear(nombre);
    await usuario.type(nombre, "Bodega 24 Horas <x>$");

    expect(nombre).toHaveValue("Bodega 24 Horas x");
  });

  it("el punto de referencia descarta los caracteres especiales", async () => {
    responder({ "/api/clientes": [cliente] });
    const usuario = userEvent.setup();
    renderizar(<ClientesPage />);

    await usuario.click(await screen.findByRole("button", { name: "Editar Bodega San José" }));
    const referencia = within(await screen.findByRole("dialog")).getByLabelText(/Punto de referencia/);
    await usuario.clear(referencia);
    await usuario.type(referencia, "Av. Real #5 $10 100% <b>");

    expect(referencia).toHaveValue("Av. Real #5 10 100 b");
  });

  it("los campos numéricos no admiten e, + ni -, ni más decimales de los permitidos", async () => {
    responder({ "/api/vehiculos": [vehiculo] });
    const usuario = userEvent.setup();
    renderizar(<FlotaPage />);

    await usuario.click(await screen.findByRole("button", { name: "Editar ABC-123" }));
    const capacidad = within(await screen.findByRole("dialog")).getByLabelText("Capacidad (kg)");
    await usuario.clear(capacidad);
    await usuario.type(capacidad, "-1e+5.678");

    expect(capacidad).toHaveValue(15.67);
  });

  it("la placa se escribe en mayúsculas y sin signos", async () => {
    responder({ "/api/vehiculos": [vehiculo] });
    const usuario = userEvent.setup();
    renderizar(<FlotaPage />);

    await usuario.click(await screen.findByRole("button", { name: "Editar ABC-123" }));
    const placa = within(await screen.findByRole("dialog")).getByLabelText("Placa");
    await usuario.clear(placa);
    await usuario.type(placa, "ab c*1_2-3");

    expect(placa).toHaveValue("ABC12-3");
  });
});
