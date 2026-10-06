import { useEffect, useState, type FormEvent } from "react";
import { api, mensajeDeError } from "../../api/client";
import { useToast } from "../../context/ToastContext";
import { useConfirm } from "../../context/ConfirmContext";
import { SelectorUbicacion } from "../../components/SelectorUbicacion";
import { Ayuda, CampoSelect, CampoTexto } from "../../components/ui";

type Prioridad = "EXPRESS" | "ESTANDAR" | "ECONOMICO";
type EstadoPedido = "PENDIENTE" | "ASIGNADO" | "EN_CAMINO" | "ENTREGADO" | "CANCELADO";

interface Cliente {
  cliente_id: string;
  nombre: string;
  referencia?: string | null;
}

interface PaginaPedidos {
  items: Pedido[];
  total: number;
  limite: number;
  desplazamiento: number;
}

interface Pedido {
  pedido_id: string;
  cliente_id: string;
  descripcion: string | null;
  peso_kg: string;
  volumen_m3: string | null;
  prioridad: Prioridad;
  estado: EstadoPedido;
  latitud: string;
  longitud: string;
  ventana_inicio: string;
  ventana_fin: string;
  creado_en: string;
}

const PRIORIDADES: Prioridad[] = ["EXPRESS", "ESTANDAR", "ECONOMICO"];
const COLOR_PRIORIDAD: Record<Prioridad, string> = {
  EXPRESS: "var(--rz-accent)",
  ESTANDAR: "var(--rz-accent-2)",
  ECONOMICO: "var(--rz-accent-3)",
};

export function PedidosPage() {
  const { notificar } = useToast();
  const { confirmar } = useConfirm();
  const [pedidos, setPedidos] = useState<Pedido[]>([]);
  const [total, setTotal] = useState(0);
  const [cargandoMas, setCargandoMas] = useState(false);
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [pedidoSeleccionado, setPedidoSeleccionado] = useState<Pedido | null>(null);
  const [error, setError] = useState<string | null>(null);

  // La API entrega los pedidos por páginas (50 por defecto): se carga la primera y el resto con "Cargar más".
  async function cargar() {
    const [pagina, listaClientes] = await Promise.all([
      api.get<PaginaPedidos>("/api/pedidos"),
      api.get<Cliente[]>("/api/clientes"),
    ]);
    setPedidos(pagina.items);
    setTotal(pagina.total);
    setClientes(listaClientes);
  }

  async function cargarMas() {
    setCargandoMas(true);
    try {
      const pagina = await api.get<PaginaPedidos>(`/api/pedidos?desplazamiento=${pedidos.length}`);
      setPedidos((actuales) => [...actuales, ...pagina.items]);
      setTotal(pagina.total);
    } catch (err) {
      setError(mensajeDeError(err, "No se pudieron cargar más pedidos"));
    } finally {
      setCargandoMas(false);
    }
  }

  useEffect(() => {
    void cargar();
  }, []);

  async function cancelar(pedidoId: string) {
    const acepto = await confirmar({
      titulo: "Cancelar pedido",
      mensaje: "¿Cancelar este pedido? Esta acción no se puede deshacer.",
      textoAceptar: "Cancelar pedido",
      peligroso: true,
    });
    if (!acepto) return;
    setError(null);
    try {
      await api.delete(`/api/pedidos/${pedidoId}`);
      await cargar();
      notificar("Pedido cancelado", "exito");
    } catch (err) {
      const mensaje = mensajeDeError(err, "No se pudo cancelar el pedido");
      setError(mensaje);
      notificar(mensaje, "error");
    }
  }

  return (
    <div style={{ padding: 28, display: "flex", flexDirection: "column", gap: 20, maxWidth: 1440 }}>
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
            role="button"
            tabIndex={0}
            onClick={() => setPedidoSeleccionado(p)}
            onKeyDown={(e) => {
              if (e.key === "Enter") setPedidoSeleccionado(p);
            }}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 14,
              padding: "12px 16px",
              borderRadius: 12,
              border: "1px solid var(--rz-panel-border)",
              background: "var(--rz-panel-bg)",
              cursor: "pointer",
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
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  void cancelar(p.pedido_id);
                }}
                style={estiloBotonSecundario}
              >
                Cancelar
              </button>
            )}
          </div>
        ))}
        {pedidos.length < total && (
          <button type="button" onClick={() => void cargarMas()} disabled={cargandoMas} style={estiloBotonSecundario}>
            {cargandoMas ? "Cargando…" : `Cargar más (${total - pedidos.length} restantes)`}
          </button>
        )}
        {pedidos.length > 0 && (
          <div style={{ fontSize: 12, color: "var(--rz-text-muted)" }}>
            Mostrando {pedidos.length} de {total} pedidos
          </div>
        )}
        {pedidos.length === 0 && (
          <div style={{ padding: 24, textAlign: "center", color: "var(--rz-text-muted)", fontSize: 13.5 }}>
            No hay pedidos registrados todavía.
          </div>
        )}
      </div>

      {pedidoSeleccionado && (
        <DetallePedido
          pedido={pedidoSeleccionado}
          cliente={clientes.find((c) => c.cliente_id === pedidoSeleccionado.cliente_id)}
          onCerrar={() => setPedidoSeleccionado(null)}
        />
      )}
    </div>
  );
}

function DetallePedido({
  pedido,
  cliente,
  onCerrar,
}: {
  pedido: Pedido;
  cliente?: Cliente;
  onCerrar: () => void;
}) {
  return (
    <div
      role="presentation"
      onClick={onCerrar}
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(10, 13, 14, 0.55)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 1500,
        padding: 20,
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-label="Detalle del pedido"
        onClick={(e) => e.stopPropagation()}
        style={{
          width: "100%",
          maxWidth: 440,
          borderRadius: 18,
          background: "var(--rz-panel-solid-bg)",
          border: "1px solid var(--rz-panel-border)",
          boxShadow: "0 24px 60px rgba(0, 0, 0, 0.35)",
          padding: 24,
          display: "flex",
          flexDirection: "column",
          gap: 14,
        }}
      >
        <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 12 }}>
          <div>
            <div style={{ fontFamily: "var(--rz-font-display)", fontWeight: 700, fontSize: 17 }}>
              {pedido.descripcion ?? "Pedido sin descripción"}
            </div>
            <span
              style={{
                display: "inline-block",
                marginTop: 6,
                fontSize: 11,
                fontWeight: 700,
                textTransform: "uppercase",
                color: "var(--rz-accent)",
                background: "var(--rz-accent-soft-bg)",
                padding: "2px 10px",
                borderRadius: 999,
              }}
            >
              {pedido.estado}
            </span>
          </div>
          <button type="button" onClick={onCerrar} aria-label="Cerrar" style={estiloBotonCerrar}>
            ✕
          </button>
        </div>

        <FilaDetalle etiqueta="Cliente" valor={cliente?.nombre ?? pedido.cliente_id} />
        {cliente?.referencia && <FilaDetalle etiqueta="Punto de referencia" valor={cliente.referencia} />}
        <FilaDetalle etiqueta="Prioridad" valor={pedido.prioridad} />
        <FilaDetalle etiqueta="Peso" valor={`${pedido.peso_kg} kg`} />
        {pedido.volumen_m3 && <FilaDetalle etiqueta="Volumen" valor={`${pedido.volumen_m3} m³`} />}
        <FilaDetalle
          etiqueta="Horario de entrega"
          valor={`${pedido.ventana_inicio.slice(0, 5)} – ${pedido.ventana_fin.slice(0, 5)}`}
        />
        <FilaDetalle etiqueta="Coordenadas" valor={`${pedido.latitud}, ${pedido.longitud}`} />
        <FilaDetalle etiqueta="Registrado" valor={new Date(pedido.creado_en).toLocaleString("es-PE")} />

        <button type="button" onClick={onCerrar} style={estiloBotonSecundario}>
          Cerrar
        </button>
      </div>
    </div>
  );
}

function FilaDetalle({ etiqueta, valor }: { etiqueta: string; valor: string }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", gap: 16, fontSize: 13 }}>
      <span style={{ color: "var(--rz-text-muted)" }}>{etiqueta}</span>
      <span style={{ fontWeight: 600, textAlign: "right" }}>{valor}</span>
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
      setError(mensajeDeError(err, "No se pudo registrar el pedido"));
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
        <form onSubmit={enviar} style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 200px), 1fr))", gap: 14 }}>
          <div style={estiloEtiqueta}>
            <span>
              <label htmlFor="pedido-cliente">Cliente</label>
              <Ayuda texto="Negocio al que se entrega el pedido. Si no está en la lista, usa el botón Nuevo para registrarlo." />
            </span>
            <div style={{ display: "flex", gap: 6 }}>
              <select id="pedido-cliente" value={clienteId} onChange={(e) => setClienteId(e.target.value)} style={estiloInput} required>
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
          </div>
          <CampoTexto
            etiqueta="Descripción"
            valor={descripcion}
            onCambio={setDescripcion}
            ayuda="Qué se entrega, por ejemplo: 10 cajas de gaseosa. Ayuda al conductor a reconocer el pedido."
          />
          <CampoTexto
            etiqueta="Peso (kg)"
            valor={pesoKg}
            onCambio={setPesoKg}
            tipo="number"
            paso="0.01"
            ayuda="Peso total del pedido en kilogramos. Ejemplo: 25.5. El optimizador lo suma para no superar la capacidad de cada vehículo."
          />
          <CampoSelect
            etiqueta="Prioridad"
            valor={prioridad}
            opciones={PRIORIDADES}
            onCambio={(v) => setPrioridad(v as Prioridad)}
            ayuda="EXPRESS se asigna a la primera ruta disponible y se entrega antes que los demás. ESTANDAR es el trato normal. ECONOMICO puede esperar y agruparse con otros pedidos."
          />
          <SelectorUbicacion
            latitud={latitud}
            longitud={longitud}
            onCambio={(lat, lon) => {
              setLatitud(lat);
              setLongitud(lon);
            }}
          />
          <CampoTexto
            etiqueta="Entregar desde"
            valor={ventanaInicio}
            onCambio={setVentanaInicio}
            tipo="time"
            ayuda="Hora a partir de la cual el cliente puede recibir el pedido (ventana de tiempo de entrega)."
          />
          <CampoTexto
            etiqueta="Entregar hasta"
            valor={ventanaFin}
            onCambio={setVentanaFin}
            tipo="time"
            ayuda="Hora límite de entrega. Debe ser posterior a la hora de inicio; una entrega fuera de la ventana se penaliza en la ruta."
          />
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
      setError(mensajeDeError(err, "No se pudo registrar el cliente"));
    } finally {
      setEnviando(false);
    }
  }

  return (
    <form onSubmit={enviar} style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 200px), 1fr))", gap: 14 }}>
      <div style={{ gridColumn: "1 / -1", fontSize: 13, color: "var(--rz-text-muted)" }}>Registrar cliente nuevo</div>
      <CampoTexto
        etiqueta="Nombre del negocio"
        valor={nombre}
        onCambio={setNombre}
        ayuda="Nombre con el que se conoce al cliente, por ejemplo: Bodega San José."
      />
      <SelectorUbicacion
        latitud={latitud}
        longitud={longitud}
        onCambio={(lat, lon) => {
          setLatitud(lat);
          setLongitud(lon);
        }}
      />
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

const estiloBotonCerrar: React.CSSProperties = {
  width: 28,
  height: 28,
  borderRadius: 8,
  border: "1px solid var(--rz-panel-border)",
  background: "transparent",
  color: "var(--rz-text-muted)",
  fontSize: 13,
  cursor: "pointer",
  flexShrink: 0,
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
