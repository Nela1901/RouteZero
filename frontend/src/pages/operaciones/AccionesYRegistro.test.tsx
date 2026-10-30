import { beforeEach, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactElement } from "react";
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

const vehiculo = (id: string, placa: string, estado: string) => ({
  vehiculo_id: id,
  placa,
  tipo: "CAMIONETA",
  capacidad_kg: "900.00",
  consumo_km_l: "9.50",
  factor_emision_co2: "2.3100",
  anio_fabricacion: 2021,
  estado,
  soat_vence: "2027-05-01",
  revision_tecnica_vence: null,
  precio_compra_soles: null,
  vida_util_anios: null,
});

const conductor = (id: string, nombre: string, disponible: boolean) => ({
  conductor_id: id,
  nombre,
  dni: "70000001",
  categoria_licencia: "A-IIb",
  telefono: "964100001",
  correo: null,
  licencia_vence: "2028-01-01",
  horario_inicio: "06:00:00",
  horario_fin: "14:00:00",
  disponible,
  horas_conducidas_hoy: "0.00",
  consentimiento_en: "2026-10-01T10:00:00Z",
});

const pedido = (id: string, estado = "PENDIENTE") => ({
  pedido_id: id,
  cliente_id: "cliente-1",
  descripcion: `Pedido ${id}`,
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
  vi.mocked(api.post).mockReset();
  vi.mocked(api.put).mockReset();
  vi.mocked(api.delete).mockReset();
});

describe("Flota: filtros, estado, documentos y errores", () => {
  const flota = [vehiculo("v1", "ABC-123", "DISPONIBLE"), vehiculo("v2", "XYZ-789", "MANTENIMIENTO")];

  it("si la flota no carga muestra el motivo como alerta", async () => {
    vi.mocked(api.get).mockRejectedValue(new ErrorApi(500, "La base de datos no responde"));
    renderizar(<FlotaPage />);

    expect(await screen.findByRole("alert")).toHaveTextContent("La base de datos no responde");
  });

  it("el filtro por estado deja solo los vehículos de ese estado", async () => {
    responder({ "/api/vehiculos": flota });
    const usuario = userEvent.setup();
    renderizar(<FlotaPage />);

    expect(await screen.findByText("ABC-123")).toBeInTheDocument();
    expect(screen.getByText("XYZ-789")).toBeInTheDocument();

    await usuario.click(screen.getByRole("button", { name: "MANTENIMIENTO" }));
    expect(screen.queryByText("ABC-123")).not.toBeInTheDocument();
    expect(screen.getByText("XYZ-789")).toBeInTheDocument();

    await usuario.click(screen.getByRole("button", { name: "Todos" }));
    expect(screen.getByText("ABC-123")).toBeInTheDocument();
  });

  it("cambiar el estado del vehículo envía solo el estado", async () => {
    responder({ "/api/vehiculos": flota });
    vi.mocked(api.put).mockResolvedValue({});
    const usuario = userEvent.setup();
    renderizar(<FlotaPage />);

    await usuario.selectOptions(await screen.findByLabelText("Estado del vehículo ABC-123"), "MANTENIMIENTO");

    await waitFor(() => expect(api.put).toHaveBeenCalledWith("/api/vehiculos/v1", { estado: "MANTENIMIENTO" }));
    expect(await screen.findByText("Vehículo actualizado a MANTENIMIENTO")).toBeInTheDocument();
  });

  it("renovar el SOAT envía solo la fecha nueva", async () => {
    responder({ "/api/vehiculos": flota });
    vi.mocked(api.put).mockResolvedValue({});
    renderizar(<FlotaPage />);

    fireEvent.change(await screen.findByLabelText("SOAT de ABC-123"), { target: { value: "2028-06-01" } });

    await waitFor(() => expect(api.put).toHaveBeenCalledWith("/api/vehiculos/v1", { soat_vence: "2028-06-01" }));
    expect(await screen.findByText("Fecha de vencimiento actualizada")).toBeInTheDocument();
  });

  it("un cambio rechazado por la API se muestra como alerta", async () => {
    responder({ "/api/vehiculos": flota });
    vi.mocked(api.put).mockRejectedValue(new ErrorApi(409, "El vehículo está en una ruta confirmada"));
    const usuario = userEvent.setup();
    renderizar(<FlotaPage />);

    await usuario.selectOptions(await screen.findByLabelText("Estado del vehículo ABC-123"), "INACTIVO");

    expect(await screen.findByRole("alert")).toHaveTextContent("El vehículo está en una ruta confirmada");
  });

  it("si la API rechaza la eliminación avisa con el motivo y no recarga la flota", async () => {
    responder({ "/api/vehiculos": flota });
    vi.mocked(api.delete).mockRejectedValue(new ErrorApi(409, "El vehículo tiene rutas"));
    const usuario = userEvent.setup();
    renderizar(<FlotaPage />);

    await usuario.click(await screen.findByRole("button", { name: "Eliminar ABC-123" }));
    await usuario.click(within(await screen.findByRole("alertdialog")).getByRole("button", { name: "Eliminar" }));

    expect(await screen.findByText("El vehículo tiene rutas")).toBeInTheDocument();
    expect(screen.getByText("ABC-123")).toBeInTheDocument();
  });

  it("registrar un vehículo envía el formulario y avisa", async () => {
    responder({ "/api/vehiculos": flota });
    vi.mocked(api.post).mockResolvedValue({});
    const usuario = userEvent.setup();
    renderizar(<FlotaPage />);

    await usuario.click(await screen.findByRole("button", { name: "Registrar vehículo" }));
    await usuario.type(screen.getByLabelText("Placa"), "nnn-111");
    await usuario.type(screen.getByLabelText("Capacidad (kg)"), "1200");
    await usuario.type(screen.getByLabelText("Consumo (km/L)"), "10.5");
    await usuario.type(screen.getByLabelText("Factor CO₂ (kg/km)"), "0.25");
    await usuario.type(screen.getByLabelText("Año de fabricación"), "2022");
    fireEvent.change(screen.getByLabelText("Vencimiento del SOAT"), { target: { value: "2027-05-01" } });
    fireEvent.change(screen.getByLabelText("Vencimiento de la revisión técnica"), { target: { value: "2027-06-01" } });
    await usuario.click(screen.getByRole("button", { name: "Guardar vehículo" }));

    await waitFor(() => expect(api.post).toHaveBeenCalled());
    const [ruta, cuerpo] = vi.mocked(api.post).mock.calls[0];
    expect(ruta).toBe("/api/vehiculos");
    expect(cuerpo).toMatchObject({ placa: "NNN-111", capacidad_kg: "1200", tipo: "CAMIONETA" });
    expect(await screen.findByText("Vehículo registrado")).toBeInTheDocument();
  });

  it("si la API rechaza el registro muestra el motivo en el formulario", async () => {
    responder({ "/api/vehiculos": flota });
    vi.mocked(api.post).mockRejectedValue(new ErrorApi(409, "Ya existe un vehículo con esa placa"));
    const usuario = userEvent.setup();
    renderizar(<FlotaPage />);

    await usuario.click(await screen.findByRole("button", { name: "Registrar vehículo" }));
    await usuario.type(screen.getByLabelText("Placa"), "abc-123");
    await usuario.type(screen.getByLabelText("Capacidad (kg)"), "900");
    await usuario.type(screen.getByLabelText("Consumo (km/L)"), "9.5");
    await usuario.type(screen.getByLabelText("Factor CO₂ (kg/km)"), "0.25");
    await usuario.type(screen.getByLabelText("Año de fabricación"), "2021");
    fireEvent.change(screen.getByLabelText("Vencimiento del SOAT"), { target: { value: "2027-05-01" } });
    fireEvent.change(screen.getByLabelText("Vencimiento de la revisión técnica"), { target: { value: "2027-06-01" } });
    await usuario.click(screen.getByRole("button", { name: "Guardar vehículo" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Ya existe un vehículo con esa placa");
  });
});

describe("Pedidos: registro, cliente nuevo y errores", () => {
  const clientes = [{ cliente_id: "cliente-1", nombre: "Bodega San José", referencia: "Frente al mercado" }];

  function simular(items = [pedido("p1")]) {
    responder({
      "/api/pedidos": { items, total: items.length, limite: 50, desplazamiento: 0 },
      "/api/clientes": clientes,
    });
  }

  it("registrar un pedido envía el formulario con la ventana de entrega y avisa", async () => {
    simular();
    vi.mocked(api.post).mockResolvedValue({});
    const usuario = userEvent.setup();
    renderizar(<PedidosPage />);

    await usuario.click(await screen.findByRole("button", { name: "Registrar pedido" }));
    await usuario.type(screen.getByLabelText("Descripción"), "Veinte cajas de agua");
    await usuario.type(screen.getByLabelText("Peso (kg)"), "25.5");
    await usuario.click(screen.getByRole("button", { name: "Guardar pedido" }));

    await waitFor(() => expect(api.post).toHaveBeenCalled());
    const [ruta, cuerpo] = vi.mocked(api.post).mock.calls[0];
    expect(ruta).toBe("/api/pedidos");
    expect(cuerpo).toMatchObject({
      cliente_id: "cliente-1",
      descripcion: "Veinte cajas de agua",
      peso_kg: "25.5",
      prioridad: "ESTANDAR",
      ventana_inicio: "09:00:00",
      ventana_fin: "18:00:00",
    });
    expect(await screen.findByText("Pedido registrado")).toBeInTheDocument();
  });

  it("si la API rechaza el pedido muestra el motivo dentro del formulario", async () => {
    simular();
    vi.mocked(api.post).mockRejectedValue(new ErrorApi(422, "La ubicación está fuera de la zona de cobertura"));
    const usuario = userEvent.setup();
    renderizar(<PedidosPage />);

    await usuario.click(await screen.findByRole("button", { name: "Registrar pedido" }));
    await usuario.type(screen.getByLabelText("Descripción"), "Cajas de agua");
    await usuario.type(screen.getByLabelText("Peso (kg)"), "10");
    await usuario.click(screen.getByRole("button", { name: "Guardar pedido" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("La ubicación está fuera de la zona de cobertura");
  });

  it("el botón Nuevo abre el formulario de cliente y, al guardarlo, el pedido queda con ese cliente", async () => {
    simular();
    vi.mocked(api.post).mockResolvedValue({ cliente_id: "cliente-9", nombre: "Tienda Nueva" });
    const usuario = userEvent.setup();
    renderizar(<PedidosPage />);

    await usuario.click(await screen.findByRole("button", { name: "Registrar pedido" }));
    await usuario.click(screen.getByRole("button", { name: "Nuevo" }));
    await usuario.type(screen.getByLabelText("Nombre del negocio"), "Tienda Nueva");
    await usuario.click(screen.getByRole("button", { name: "Guardar cliente" }));

    await waitFor(() => expect(api.post).toHaveBeenCalledWith("/api/clientes", expect.objectContaining({ nombre: "Tienda Nueva" })));
    expect(await screen.findByText("Cliente registrado")).toBeInTheDocument();
    expect(await screen.findByRole("button", { name: "Guardar pedido" })).toBeInTheDocument();
  });

  it("cancelar el formulario de cliente vuelve al pedido", async () => {
    simular();
    const usuario = userEvent.setup();
    renderizar(<PedidosPage />);

    await usuario.click(await screen.findByRole("button", { name: "Registrar pedido" }));
    await usuario.click(screen.getByRole("button", { name: "Nuevo" }));
    const formulario = screen.getByRole("button", { name: "Guardar cliente" }).closest("form") as HTMLElement;
    await usuario.click(within(formulario).getByRole("button", { name: "Cancelar" }));

    expect(screen.getByRole("button", { name: "Guardar pedido" })).toBeInTheDocument();
  });

  it("si el cliente nuevo no se puede registrar muestra el motivo", async () => {
    simular();
    vi.mocked(api.post).mockRejectedValue(new ErrorApi(422, "El nombre ya existe"));
    const usuario = userEvent.setup();
    renderizar(<PedidosPage />);

    await usuario.click(await screen.findByRole("button", { name: "Registrar pedido" }));
    await usuario.click(screen.getByRole("button", { name: "Nuevo" }));
    await usuario.type(screen.getByLabelText("Nombre del negocio"), "Bodega");
    await usuario.click(screen.getByRole("button", { name: "Guardar cliente" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("El nombre ya existe");
  });

  it("si el pedido no se puede cancelar muestra el motivo como alerta", async () => {
    simular();
    vi.mocked(api.delete).mockRejectedValue(new ErrorApi(409, "El pedido ya fue entregado"));
    const usuario = userEvent.setup();
    renderizar(<PedidosPage />);

    await usuario.click(await screen.findByRole("button", { name: "Cancelar Pedido p1" }));
    await usuario.click(within(await screen.findByRole("alertdialog")).getByRole("button", { name: "Cancelar pedido" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("El pedido ya fue entregado");
  });

  it("cancelar un pedido asignado avisa que se retirará de la ruta", async () => {
    simular([pedido("p2", "ASIGNADO")]);
    const usuario = userEvent.setup();
    renderizar(<PedidosPage />);

    await usuario.click(await screen.findByRole("button", { name: "Cancelar Pedido p2" }));

    expect(await screen.findByText(/ya está en una ruta/)).toBeInTheDocument();
  });

  it("si cargar más pedidos falla muestra el motivo", async () => {
    vi.mocked(api.get).mockImplementation(async (url: string) => {
      if (url === "/api/pedidos") return { items: [pedido("p1")], total: 3, limite: 50, desplazamiento: 0 };
      if (url === "/api/clientes") return clientes;
      throw new ErrorApi(500, "No se pudo leer la página siguiente");
    });
    const usuario = userEvent.setup();
    renderizar(<PedidosPage />);

    await usuario.click(await screen.findByRole("button", { name: /Cargar más/ }));

    expect(await screen.findByRole("alert")).toHaveTextContent("No se pudo leer la página siguiente");
  });
});

describe("Conductores: filtros, disponibilidad, registro y errores", () => {
  const equipo = [conductor("c1", "Carlos Mendoza", true), conductor("c2", "Lucía Paredes", false)];

  it("si los conductores no cargan muestra el motivo como alerta", async () => {
    vi.mocked(api.get).mockRejectedValue(new ErrorApi(500, "La base de datos no responde"));
    renderizar(<ConductoresPage />);

    expect(await screen.findByRole("alert")).toHaveTextContent("La base de datos no responde");
  });

  it("los filtros dejan solo los disponibles o solo los no disponibles", async () => {
    responder({ "/api/conductores": equipo });
    const usuario = userEvent.setup();
    renderizar(<ConductoresPage />);

    expect(await screen.findByText("Carlos Mendoza")).toBeInTheDocument();
    expect(screen.getByText("Lucía Paredes")).toBeInTheDocument();

    await usuario.click(screen.getByRole("button", { name: "Disponibles" }));
    expect(screen.getByText("Carlos Mendoza")).toBeInTheDocument();
    expect(screen.queryByText("Lucía Paredes")).not.toBeInTheDocument();

    await usuario.click(screen.getByRole("button", { name: "No disponibles" }));
    expect(screen.queryByText("Carlos Mendoza")).not.toBeInTheDocument();
    expect(screen.getByText("Lucía Paredes")).toBeInTheDocument();

    await usuario.click(screen.getByRole("button", { name: "Todos" }));
    expect(screen.getByText("Carlos Mendoza")).toBeInTheDocument();
  });

  it("marcar a un conductor como no disponible envía solo ese dato y avisa", async () => {
    responder({ "/api/conductores": equipo });
    vi.mocked(api.put).mockResolvedValue({});
    const usuario = userEvent.setup();
    renderizar(<ConductoresPage />);

    await usuario.selectOptions(await screen.findByLabelText("Disponibilidad de Carlos Mendoza"), "no");

    await waitFor(() => expect(api.put).toHaveBeenCalledWith("/api/conductores/c1", { disponible: false }));
    expect(await screen.findByText("Conductor marcado como no disponible")).toBeInTheDocument();
  });

  it("marcar a un conductor como disponible avisa con el texto correspondiente", async () => {
    responder({ "/api/conductores": equipo });
    vi.mocked(api.put).mockResolvedValue({});
    const usuario = userEvent.setup();
    renderizar(<ConductoresPage />);

    await usuario.selectOptions(await screen.findByLabelText("Disponibilidad de Lucía Paredes"), "si");

    expect(await screen.findByText("Conductor marcado como disponible")).toBeInTheDocument();
  });

  it("si la API rechaza el cambio de disponibilidad lo muestra como alerta", async () => {
    responder({ "/api/conductores": equipo });
    vi.mocked(api.put).mockRejectedValue(new ErrorApi(409, "El conductor tiene una ruta en curso"));
    const usuario = userEvent.setup();
    renderizar(<ConductoresPage />);

    await usuario.selectOptions(await screen.findByLabelText("Disponibilidad de Carlos Mendoza"), "no");

    expect(await screen.findByRole("alert")).toHaveTextContent("El conductor tiene una ruta en curso");
  });

  it("si la API rechaza la eliminación avisa con el motivo", async () => {
    responder({ "/api/conductores": equipo });
    vi.mocked(api.delete).mockRejectedValue(new ErrorApi(409, "El conductor tiene rutas asignadas"));
    const usuario = userEvent.setup();
    renderizar(<ConductoresPage />);

    await usuario.click(await screen.findByRole("button", { name: "Eliminar Carlos Mendoza" }));
    await usuario.click(within(await screen.findByRole("alertdialog")).getByRole("button", { name: "Eliminar" }));

    expect(await screen.findByText("El conductor tiene rutas asignadas")).toBeInTheDocument();
  });

  async function llenarFormulario(usuario: ReturnType<typeof userEvent.setup>) {
    await usuario.click(await screen.findByRole("button", { name: "Registrar conductor" }));
    await usuario.type(screen.getByLabelText("Nombre completo"), "Ana Quispe");
    await usuario.type(screen.getByLabelText("DNI"), "71234567");
    await usuario.type(screen.getByLabelText("Teléfono de contacto"), "987654321");
    fireEvent.change(screen.getByLabelText("Vencimiento de la licencia"), { target: { value: "2030-01-01" } });
    await usuario.click(screen.getByRole("checkbox"));
    await usuario.click(screen.getByRole("button", { name: "Guardar conductor" }));
  }

  it("registrar un conductor envía el formulario con el consentimiento y avisa", async () => {
    responder({ "/api/conductores": equipo });
    vi.mocked(api.post).mockResolvedValue({});
    const usuario = userEvent.setup();
    renderizar(<ConductoresPage />);

    await llenarFormulario(usuario);

    await waitFor(() => expect(api.post).toHaveBeenCalled());
    const [ruta, cuerpo] = vi.mocked(api.post).mock.calls[0];
    expect(ruta).toBe("/api/conductores");
    expect(cuerpo).toMatchObject({ nombre: "Ana Quispe", dni: "71234567", telefono: "987654321", consentimiento_datos: true });
    expect(await screen.findByText("Conductor registrado")).toBeInTheDocument();
  });

  it("si la API rechaza el registro muestra el motivo en el formulario", async () => {
    responder({ "/api/conductores": equipo });
    vi.mocked(api.post).mockRejectedValue(new ErrorApi(409, "Ya existe un conductor con ese DNI"));
    const usuario = userEvent.setup();
    renderizar(<ConductoresPage />);

    await llenarFormulario(usuario);

    expect(await screen.findByRole("alert")).toHaveTextContent("Ya existe un conductor con ese DNI");
  });
});
