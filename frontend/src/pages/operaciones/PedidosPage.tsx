import { useEffect, useState, type FormEvent } from "react";
import { api, ErrorApi } from "../../api/client";
import { useToast } from "../../context/ToastContext";

type Prioridad = "EXPRESS" | "ESTANDAR" | "ECONOMICO";
type EstadoPedido = "PENDIENTE" | "ASIGNADO" | "EN_CAMINO" | "ENTREGADO" | "CANCELADO";

interface Cliente {
  cliente_id: string;
  nombre: string;
}

interface Pedido {
  pedido_id: string;
  cliente_id: string;
  descripcion: string | null;
  peso_kg: string;
  prioridad: Prioridad;
  estado: EstadoPedido;
  ventana_inicio: string;
  ventana_fin: string;
}

const PRIORIDADES: Prioridad[] = ["EXPRESS", "ESTANDAR", "ECONOMICO"];
const COLOR_PRIORIDAD: Record<Prioridad, string> = {
  EXPRESS: "var(--rz-accent)",
  ESTANDAR: "var(--rz-accent-2)",
  ECONOMICO: "var(--rz-accent-3)",
};

export function PedidosPage() {
  const { notificar } = useToast();
  const [pedidos, setPedidos] = useState<Pedido[]>([]);
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function cargar() {
    const [listaPedidos, listaClientes] = await Promise.all([
      api.get<Pedido[]>("/api/pedidos"),
      api.get<Cliente[]>("/api/clientes"),
    ]);
    setPedidos(listaPedidos);
    setClientes(listaClientes);
  }

  useEffect(() => {
    void cargar();
  }, []);

  async function cancelar(pedidoId: string) {
    if (!window.confirm("¿Cancelar este pedido?")) return;
    setError(null);
    try {
      await api.delete(`/api/pedidos/${pedidoId}`);
      await cargar();
      notificar("Pedido cancelado", "exito");
    } catch (err) {
      const mensaje = err instanceof ErrorApi ? String(err.detalle) : "No se pudo cancelar el pedido";
      setError(mensaje);
      notificar(mensaje, "error");
    }
  }

  return (
    <div style={{ padding: 28, display: "flex", flexDirection: "column", gap: 20, maxWidth: 1040 }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div>
          <h1 style={{ fontFamily: "var(--rz-font-display)", fontSize: 22, margin: "0 0 4px" }}>Pedidos</h1>
          <p style={{ margin: 0, fontSize: 13, color: "var(--rz-text-muted)" }}>
            Registro de pedidos con coordenadas dentro de la zona de cobertura de Huancayo.
          </p>
        </div>
        <button type="button" onClick={() => setMostrarFormulario((v) => !v)} style={estiloBotonPrimario}>
          {mostrarFormulario ? "Cancelar" : "Registrar pedido"}
        </button>
      </div>

      {mostrarFormulario && (
        <FormularioPedido
          clientes={clientes}
          onCreado={() => {
            setMostrarFormulario(false);
            void cargar();
            notificar("Pedido registrado", "exito");
          }}
          onClienteCreado={() => {
            void cargar();
            notificar("Cliente registrado", "exito");
          }}
        />
      )}

      {error && <div style={estiloAviso}>{error}</div>}

      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {pedidos.map((p) => (
          <div
            key={p.pedido_id}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 14,
              padding: "12px 16px",
              borderRadius: 12,
              border: "1px solid var(--rz-panel-border)",
              background: "var(--rz-panel-bg)",
            }}
          >
            <span
              aria-hidden="true"
              style={{ width: 8, height: 8, borderRadius: "50%", background: COLOR_PRIORIDAD[p.prioridad], flexShrink: 0 }}
            />
            <div style={{ flexGrow: 1, minWidth: 0 }}>
              <div style={{ fontSize: 13.5, fontWeight: 600 }}>{p.descripcion ?? "Pedido sin descripción"}</div>
              <div style={{ fontSize: 12, color: "var(--rz-text-muted)" }}>
                {clientes.find((c) => c.cliente_id === p.cliente_id)?.nombre ?? p.cliente_id} · {p.peso_kg} kg ·{" "}
                {p.ventana_inicio.slice(0, 5)}–{p.ventana_fin.slice(0, 5)}
              </div>
            </div>
            <span style={{ fontSize: 11.5, color: "var(--rz-text-muted)", fontFamily: "var(--rz-font-mono)" }}>
              {p.estado}
            </span>
            {p.estado === "PENDIENTE" && (
              <button type="button" onClick={() => void cancelar(p.pedido_id)} style={estiloBotonSecundario}>
                Cancelar
              </button>
            )}
          </div>
        ))}
        {pedidos.length === 0 && (
          <div style={{ padding: 24, textAlign: "center", color: "var(--rz-text-muted)", fontSize: 13.5 }}>
            No hay pedidos registrados todavía.
          </div>
        )}
      </div>
    </div>
  );
}

function FormularioPedido({
  clientes,
  onCreado,
  onClienteCreado,
}: {
  clientes: Cliente[];
  onCreado: () => void;
  onClienteCreado: () => void;
}) {
  const [clienteId, setClienteId] = useState(clientes[0]?.cliente_id ?? "");
  const [descripcion, setDescripcion] = useState("");
  const [pesoKg, setPesoKg] = useState("");
  const [prioridad, setPrioridad] = useState<Prioridad>("ESTANDAR");
  const [latitud, setLatitud] = useState("-12.0653");
  const [longitud, setLongitud] = useState("-75.2049");
  const [ventanaInicio, setVentanaInicio] = useState("09:00");
  const [ventanaFin, setVentanaFin] = useState("18:00");
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);
  const [mostrarClienteNuevo, setMostrarClienteNuevo] = useState(clientes.length === 0);

  async function enviar(evento: FormEvent) {
    evento.preventDefault();
    setError(null);
    setEnviando(true);
    try {
      await api.post("/api/pedidos", {
        cliente_id: clienteId,
        descripcion: descripcion || null,
        peso_kg: pesoKg,
        prioridad,
        latitud,
        longitud,
        ventana_inicio: `${ventanaInicio}:00`,
        ventana_fin: `${ventanaFin}:00`,
      });
      onCreado();
    } catch (err) {
      setError(err instanceof ErrorApi ? String(err.detalle) : "No se pudo registrar el pedido");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: 16,
        padding: 20,
        borderRadius: 16,
        background: "var(--rz-panel-bg)",
        border: "1px solid var(--rz-panel-border)",
      }}
    >
      {mostrarClienteNuevo ? (
        <FormularioClienteRapido
          onCreado={(cliente) => {
            setClienteId(cliente.cliente_id);
            setMostrarClienteNuevo(false);
            onClienteCreado();
          }}
          onCancelar={clientes.length > 0 ? () => setMostrarClienteNuevo(false) : undefined}
        />
      ) : (
        <form onSubmit={enviar} style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 14 }}>
          <label style={estiloEtiqueta}>
            Cliente
            <div style={{ display: "flex", gap: 6 }}>
              <select value={clienteId} onChange={(e) => setClienteId(e.target.value)} style={estiloInput} required>
                {clientes.map((c) => (
                  <option key={c.cliente_id} value={c.cliente_id}>
                    {c.nombre}
                  </option>
                ))}
              </select>
              <button type="button" onClick={() => setMostrarClienteNuevo(true)} style={estiloBotonSecundario}>
                Nuevo
              </button>
            </div>
          </label>
          <CampoTexto etiqueta="Descripción" valor={descripcion} onCambio={setDescripcion} />
          <CampoTexto etiqueta="Peso (kg)" valor={pesoKg} onCambio={setPesoKg} tipo="number" />
          <CampoSelect etiqueta="Prioridad" valor={prioridad} opciones={PRIORIDADES} onCambio={(v) => setPrioridad(v as Prioridad)} />
          <CampoTexto etiqueta="Latitud" valor={latitud} onCambio={setLatitud} tipo="number" />
          <CampoTexto etiqueta="Longitud" valor={longitud} onCambio={setLongitud} tipo="number" />
          <CampoTexto etiqueta="Ventana desde" valor={ventanaInicio} onCambio={setVentanaInicio} tipo="time" />
          <CampoTexto etiqueta="Ventana hasta" valor={ventanaFin} onCambio={setVentanaFin} tipo="time" />
          {error && <div style={{ ...estiloAviso, gridColumn: "1 / -1" }}>{error}</div>}
          <div style={{ gridColumn: "1 / -1" }}>
            <button type="submit" disabled={enviando} style={estiloBotonPrimario}>
              {enviando ? "Registrando…" : "Guardar pedido"}
            </button>
          </div>
        </form>
      )}
    </div>
  );
}

function FormularioClienteRapido({
  onCreado,
  onCancelar,
}: {
  onCreado: (cliente: Cliente) => void;
  onCancelar?: () => void;
}) {
  const [nombre, setNombre] = useState("");
  const [latitud, setLatitud] = useState("-12.0653");
  const [longitud, setLongitud] = useState("-75.2049");
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function enviar(evento: FormEvent) {
    evento.preventDefault();
    setError(null);
    setEnviando(true);
    try {
      const cliente = await api.post<Cliente>("/api/clientes", {
        nombre,
        tipo_negocio: "OTRO",
        latitud,
        longitud,
      });
      onCreado(cliente);
    } catch (err) {
      setError(err instanceof ErrorApi ? String(err.detalle) : "No se pudo registrar el cliente");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <form onSubmit={enviar} style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 14 }}>
      <div style={{ gridColumn: "1 / -1", fontSize: 13, color: "var(--rz-text-muted)" }}>Registrar cliente nuevo</div>
      <CampoTexto etiqueta="Nombre del negocio" valor={nombre} onCambio={setNombre} />
      <CampoTexto etiqueta="Latitud" valor={latitud} onCambio={setLatitud} tipo="number" />
      <CampoTexto etiqueta="Longitud" valor={longitud} onCambio={setLongitud} tipo="number" />
      {error && <div style={{ ...estiloAviso, gridColumn: "1 / -1" }}>{error}</div>}
      <div style={{ gridColumn: "1 / -1", display: "flex", gap: 10 }}>
        <button type="submit" disabled={enviando} style={estiloBotonPrimario}>
          {enviando ? "Guardando…" : "Guardar cliente"}
        </button>
        {onCancelar && (
          <button type="button" onClick={onCancelar} style={estiloBotonSecundario}>
            Cancelar
          </button>
        )}
      </div>
    </form>
  );
}

function CampoTexto(props: { etiqueta: string; valor: string; onCambio: (v: string) => void; tipo?: string }) {
  return (
    <label style={estiloEtiqueta}>
      {props.etiqueta}
      <input required type={props.tipo ?? "text"} value={props.valor} onChange={(e) => props.onCambio(e.target.value)} style={estiloInput} />
    </label>
  );
}

function CampoSelect(props: { etiqueta: string; valor: string; opciones: string[]; onCambio: (v: string) => void }) {
  return (
    <label style={estiloEtiqueta}>
      {props.etiqueta}
      <select value={props.valor} onChange={(e) => props.onCambio(e.target.value)} style={estiloInput}>
        {props.opciones.map((o) => (
          <option key={o} value={o}>
            {o}
          </option>
        ))}
      </select>
    </label>
  );
}

const estiloEtiqueta: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: 4,
  fontSize: 12.5,
  color: "var(--rz-text-muted)",
};

const estiloBotonPrimario: React.CSSProperties = {
  height: 40,
  padding: "0 18px",
  borderRadius: 12,
  border: "none",
  background: "var(--rz-accent)",
  color: "var(--rz-bg)",
  fontWeight: 700,
  fontSize: 13.5,
  cursor: "pointer",
};

const estiloBotonSecundario: React.CSSProperties = {
  height: 38,
  padding: "0 14px",
  borderRadius: 10,
  border: "1px solid var(--rz-panel-border)",
  background: "transparent",
  color: "var(--rz-text)",
  fontSize: 12.5,
  cursor: "pointer",
};

const estiloInput: React.CSSProperties = {
  height: 38,
  borderRadius: 10,
  border: "1px solid var(--rz-panel-border)",
  background: "var(--rz-bg)",
  color: "var(--rz-text)",
  padding: "0 12px",
  fontSize: 13.5,
};

const estiloAviso: React.CSSProperties = {
  borderRadius: 10,
  background: "var(--rz-danger-soft-bg)",
  color: "var(--rz-danger)",
  padding: "10px 12px",
  fontSize: 13,
};
