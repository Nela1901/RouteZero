import { useEffect, useState, type FormEvent } from "react";
import { api, mensajeDeError } from "../../api/client";
import { useConfirm } from "../../context/ConfirmContext";
import { useToast } from "../../context/ToastContext";
import { SelectorUbicacion } from "../../components/SelectorUbicacion";
import { AccionesFila, FilaDetalle, Modal } from "../../components/acciones";
import { estiloBotonSecundario, filtrarNombreNegocio, filtrarTexto, soloCambios } from "../../components/utilesCrud";
import {
  CampoSelect,
  CampoTexto,
  estiloAviso,
  estiloBotonPrimario,
  FiltroChip,
  Td,
  Th,
} from "../../components/ui";

type TipoNegocio = "BODEGA" | "RESTAURANTE" | "MERCADO" | "COMERCIO" | "OTRO";

interface Cliente {
  cliente_id: string;
  nombre: string;
  tipo_negocio: TipoNegocio;
  referencia: string | null;
  latitud: string;
  longitud: string;
  horario_inicio: string;
  horario_fin: string;
  creado_en: string;
}

const TIPOS: TipoNegocio[] = ["BODEGA", "RESTAURANTE", "MERCADO", "COMERCIO", "OTRO"];

// La API devuelve HH:MM:SS; en pantalla basta HH:MM.
const hora = (valor: string) => valor.slice(0, 5);

export function ClientesPage() {
  const { notificar } = useToast();
  const { confirmar } = useConfirm();
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [filtro, setFiltro] = useState<TipoNegocio | "">("");
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [detalle, setDetalle] = useState<Cliente | null>(null);
  const [edicion, setEdicion] = useState<Cliente | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Una sola carga; el filtro por tipo de negocio se aplica en el navegador (igual que Flota).
  async function cargar() {
    try {
      setClientes(await api.get<Cliente[]>("/api/clientes"));
    } catch (err) {
      setError(mensajeDeError(err, "No se pudieron cargar los clientes"));
    }
  }

  useEffect(() => {
    void cargar();
  }, []);

  async function eliminar(cliente: Cliente) {
    const acepto = await confirmar({
      titulo: "Eliminar cliente",
      mensaje: `Se eliminará "${cliente.nombre}". Esta acción no se puede deshacer.`,
      textoAceptar: "Eliminar",
      peligroso: true,
    });
    if (!acepto) return;
    try {
      await api.delete(`/api/clientes/${cliente.cliente_id}`);
      await cargar();
      notificar("Cliente eliminado", "exito");
    } catch (err) {
      notificar(mensajeDeError(err, "No se pudo eliminar el cliente"), "error");
    }
  }

  const visibles = filtro ? clientes.filter((c) => c.tipo_negocio === filtro) : clientes;

  return (
    <div style={{ padding: 28, display: "flex", flexDirection: "column", gap: 20, maxWidth: 1440 }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 12 }}>
        <div>
          <h1 style={{ fontFamily: "var(--rz-font-display)", fontSize: 22, margin: "0 0 4px" }}>Clientes</h1>
          <p style={{ margin: 0, fontSize: 13, color: "var(--rz-text-muted)" }}>
            Negocios a los que se entrega, con su horario preferido de recepción.
          </p>
        </div>
        <button type="button" onClick={() => setMostrarFormulario((v) => !v)} style={estiloBotonPrimario}>
          {mostrarFormulario ? "Cancelar" : "Registrar cliente"}
        </button>
      </div>

      {mostrarFormulario && (
        <FormularioCliente
          onGuardado={() => {
            setMostrarFormulario(false);
            void cargar();
            notificar("Cliente registrado", "exito");
          }}
        />
      )}

      {error && <div style={estiloAviso}>{error}</div>}

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        <FiltroChip etiqueta="Todos" activo={filtro === ""} onClick={() => setFiltro("")} />
        {TIPOS.map((tipo) => (
          <FiltroChip key={tipo} etiqueta={tipo} activo={filtro === tipo} onClick={() => setFiltro(tipo)} />
        ))}
      </div>

      <div style={{ borderRadius: 16, border: "1px solid var(--rz-panel-border)", overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13.5 }}>
          <thead>
            <tr style={{ background: "var(--rz-panel-bg)", textAlign: "left" }}>
              <Th>Nombre</Th>
              <Th>Tipo de negocio</Th>
              <Th>Horario de entrega</Th>
              <Th>Punto de referencia</Th>
              <Th>Acciones</Th>
            </tr>
          </thead>
          <tbody>
            {visibles.map((c) => (
              <tr key={c.cliente_id} style={{ borderTop: "1px solid var(--rz-panel-border)" }}>
                <Td>{c.nombre}</Td>
                <Td>{c.tipo_negocio}</Td>
                <Td mono>
                  {hora(c.horario_inicio)}–{hora(c.horario_fin)}
                </Td>
                <Td>{c.referencia ?? "—"}</Td>
                <Td>
                  <AccionesFila
                    nombre={c.nombre}
                    onVer={() => setDetalle(c)}
                    onEditar={() => setEdicion(c)}
                    onEliminar={() => void eliminar(c)}
                  />
                </Td>
              </tr>
            ))}
            {visibles.length === 0 && (
              <tr>
                <td colSpan={5} style={{ padding: 24, textAlign: "center", color: "var(--rz-text-muted)" }}>
                  {filtro ? "No hay clientes de este tipo." : "No hay clientes registrados todavía."}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {detalle && (
        <Modal titulo={detalle.nombre} onCerrar={() => setDetalle(null)}>
          <FilaDetalle etiqueta="Tipo de negocio" valor={detalle.tipo_negocio} />
          <FilaDetalle etiqueta="Horario de entrega" valor={`${hora(detalle.horario_inicio)} – ${hora(detalle.horario_fin)}`} />
          <FilaDetalle etiqueta="Punto de referencia" valor={detalle.referencia ?? "—"} />
          <FilaDetalle etiqueta="Coordenadas" valor={`${detalle.latitud}, ${detalle.longitud}`} />
          <FilaDetalle etiqueta="Registrado" valor={new Date(detalle.creado_en).toLocaleString("es-PE")} />
          <button type="button" onClick={() => setDetalle(null)} style={estiloBotonSecundario}>
            Cerrar
          </button>
        </Modal>
      )}

      {edicion && (
        <Modal titulo={`Editar ${edicion.nombre}`} onCerrar={() => setEdicion(null)} ancho={680}>
          <FormularioCliente
            inicial={edicion}
            onGuardado={() => {
              setEdicion(null);
              void cargar();
              notificar("Cliente actualizado", "exito");
            }}
          />
        </Modal>
      )}
    </div>
  );
}

function FormularioCliente({ inicial, onGuardado }: { inicial?: Cliente; onGuardado: () => void }) {
  const [nombre, setNombre] = useState(inicial?.nombre ?? "");
  const [tipo, setTipo] = useState<TipoNegocio>(inicial?.tipo_negocio ?? "BODEGA");
  const [horarioInicio, setHorarioInicio] = useState(inicial ? hora(inicial.horario_inicio) : "08:00");
  const [horarioFin, setHorarioFin] = useState(inicial ? hora(inicial.horario_fin) : "18:00");
  const [referencia, setReferencia] = useState(inicial?.referencia ?? "");
  const [latitud, setLatitud] = useState(inicial?.latitud ?? "-12.0653");
  const [longitud, setLongitud] = useState(inicial?.longitud ?? "-75.2049");
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function enviar(evento: FormEvent) {
    evento.preventDefault();
    setError(null);
    setEnviando(true);
    try {
      const cuerpo = {
        nombre: nombre.trim(),
        tipo_negocio: tipo,
        referencia: referencia.trim() || null,
        latitud,
        longitud,
        horario_inicio: `${horarioInicio}:00`,
        horario_fin: `${horarioFin}:00`,
      };
      if (inicial) {
        const original = {
          nombre: inicial.nombre,
          tipo_negocio: inicial.tipo_negocio,
          referencia: inicial.referencia,
          latitud: inicial.latitud,
          longitud: inicial.longitud,
          horario_inicio: `${hora(inicial.horario_inicio)}:00`,
          horario_fin: `${hora(inicial.horario_fin)}:00`,
        };
        const cambios = soloCambios(original, cuerpo);
        if (Object.keys(cambios).length === 0) {
          setError("No hay cambios para guardar");
          return;
        }
        await api.put(`/api/clientes/${inicial.cliente_id}`, cambios);
      } else {
        await api.post("/api/clientes", cuerpo);
      }
      onGuardado();
    } catch (err) {
      setError(mensajeDeError(err, inicial ? "No se pudo actualizar el cliente" : "No se pudo registrar el cliente"));
    } finally {
      setEnviando(false);
    }
  }

  return (
    <form
      onSubmit={enviar}
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 200px), 1fr))",
        gap: 14,
        padding: inicial ? 0 : 20,
        borderRadius: 16,
        background: inicial ? "transparent" : "var(--rz-panel-bg)",
        border: inicial ? "none" : "1px solid var(--rz-panel-border)",
      }}
    >
      <CampoTexto
        etiqueta="Nombre del negocio"
        valor={nombre}
        onCambio={(v) => setNombre(filtrarNombreNegocio(v))}
        atributos={{ maxLength: 150 }}
        ayuda="Nombre con el que se conoce al cliente, por ejemplo: Bodega San José. Admite letras, números y . , - & ' ( ). No puede repetirse."
      />
      <CampoSelect
        etiqueta="Tipo de negocio"
        valor={tipo}
        opciones={TIPOS}
        onCambio={(v) => setTipo(v as TipoNegocio)}
        ayuda="Giro del negocio: bodega, restaurante, mercado, comercio u otro."
      />
      <CampoTexto
        etiqueta="Recibe desde"
        valor={horarioInicio}
        onCambio={setHorarioInicio}
        tipo="time"
        ayuda="Hora a partir de la cual el negocio recibe pedidos. El optimizador la usa como ventana de entrega."
      />
      <CampoTexto
        etiqueta="Recibe hasta"
        valor={horarioFin}
        onCambio={setHorarioFin}
        tipo="time"
        ayuda="Hora hasta la que el negocio recibe pedidos. Debe ser posterior a la hora de inicio."
      />
      <CampoTexto
        etiqueta="Punto de referencia"
        valor={referencia}
        onCambio={(v) => setReferencia(filtrarTexto(v))}
        opcional
        atributos={{ maxLength: 2000 }}
        ayuda="Indicación para encontrar el lugar, por ejemplo: frente al Mercado Modelo."
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
      <div style={{ gridColumn: "1 / -1" }}>
        <button type="submit" disabled={enviando} style={estiloBotonPrimario}>
          {enviando ? "Guardando…" : inicial ? "Guardar cambios" : "Guardar cliente"}
        </button>
      </div>
    </form>
  );
}
