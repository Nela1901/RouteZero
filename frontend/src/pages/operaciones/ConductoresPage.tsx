import { useEffect, useState, type FormEvent } from "react";
import { api, mensajeDeError } from "../../api/client";
import { useConfirm } from "../../context/ConfirmContext";
import { useToast } from "../../context/ToastContext";
import { AccionesFila, FilaDetalle, Modal } from "../../components/acciones";
import { estiloBotonSecundario, soloCambios } from "../../components/utilesCrud";
import {
  CampoSelect,
  CampoTexto,
  estiloAviso,
  estiloBotonPrimario,
  EstadoVencimiento,
  FiltroChip,
  Td,
  Th,
} from "../../components/ui";

interface Conductor {
  conductor_id: string;
  nombre: string;
  dni: string;
  categoria_licencia: string;
  telefono: string;
  correo: string | null;
  licencia_vence: string;
  horario_inicio: string;
  horario_fin: string;
  disponible: boolean;
  horas_conducidas_hoy: string;
  consentimiento_en: string;
}

type Filtro = "todos" | "disponibles" | "no_disponibles";

const CATEGORIAS = ["A-I", "A-IIa", "A-IIb", "A-IIIa", "A-IIIb", "A-IIIc", "B-IIa", "B-IIb"];

// La API devuelve HH:MM:SS; en pantalla basta HH:MM.
const hora = (valor: string) => valor.slice(0, 5);

export function ConductoresPage() {
  const { notificar } = useToast();
  const { confirmar } = useConfirm();
  const [conductores, setConductores] = useState<Conductor[]>([]);
  const [filtro, setFiltro] = useState<Filtro>("todos");
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [detalle, setDetalle] = useState<Conductor | null>(null);
  const [edicion, setEdicion] = useState<Conductor | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Misma estrategia que Flota: una sola carga y el filtro se aplica en el navegador.
  async function cargar() {
    try {
      setConductores(await api.get<Conductor[]>("/api/conductores"));
    } catch (err) {
      setError(mensajeDeError(err, "No se pudieron cargar los conductores"));
    }
  }

  useEffect(() => {
    void cargar();
  }, []);

  const visibles = conductores.filter((c) =>
    filtro === "todos" ? true : filtro === "disponibles" ? c.disponible : !c.disponible,
  );

  async function cambiarDisponibilidad(conductorId: string, disponible: boolean) {
    setError(null);
    try {
      await api.put(`/api/conductores/${conductorId}`, { disponible });
      await cargar();
      notificar(disponible ? "Conductor marcado como disponible" : "Conductor marcado como no disponible", "exito");
    } catch (err) {
      const mensaje = mensajeDeError(err, "No se pudo actualizar el conductor");
      setError(mensaje);
      notificar(mensaje, "error");
    }
  }

  async function eliminar(conductor: Conductor) {
    const acepto = await confirmar({
      titulo: "Eliminar conductor",
      mensaje: `Se eliminará a ${conductor.nombre} y sus datos personales. Esta acción no se puede deshacer.`,
      textoAceptar: "Eliminar",
      peligroso: true,
    });
    if (!acepto) return;
    try {
      await api.delete(`/api/conductores/${conductor.conductor_id}`);
      await cargar();
      notificar("Conductor eliminado", "exito");
    } catch (err) {
      notificar(mensajeDeError(err, "No se pudo eliminar el conductor"), "error");
    }
  }

  return (
    <div style={{ padding: 28, display: "flex", flexDirection: "column", gap: 20, maxWidth: 1440 }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 12 }}>
        <div>
          <h1 style={{ fontFamily: "var(--rz-font-display)", fontSize: 22, margin: "0 0 4px" }}>Conductores</h1>
          <p style={{ margin: 0, fontSize: 13, color: "var(--rz-text-muted)" }}>
            Registro de conductores, licencia y disponibilidad horaria.
          </p>
        </div>
        <button type="button" onClick={() => setMostrarFormulario((v) => !v)} style={estiloBotonPrimario}>
          {mostrarFormulario ? "Cancelar" : "Registrar conductor"}
        </button>
      </div>

      {mostrarFormulario && (
        <FormularioConductor
          onGuardado={() => {
            setMostrarFormulario(false);
            void cargar();
            notificar("Conductor registrado", "exito");
          }}
        />
      )}

      {error && <div style={estiloAviso}>{error}</div>}

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        <FiltroChip etiqueta="Todos" activo={filtro === "todos"} onClick={() => setFiltro("todos")} />
        <FiltroChip etiqueta="Disponibles" activo={filtro === "disponibles"} onClick={() => setFiltro("disponibles")} />
        <FiltroChip
          etiqueta="No disponibles"
          activo={filtro === "no_disponibles"}
          onClick={() => setFiltro("no_disponibles")}
        />
      </div>

      <div style={{ borderRadius: 16, border: "1px solid var(--rz-panel-border)", overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13.5 }}>
          <thead>
            <tr style={{ background: "var(--rz-panel-bg)", textAlign: "left" }}>
              <Th>Nombre</Th>
              <Th>DNI</Th>
              <Th>Licencia</Th>
              <Th>Contacto</Th>
              <Th>Licencia vence</Th>
              <Th>Horario</Th>
              <Th>Disponibilidad</Th>
              <Th>Acciones</Th>
            </tr>
          </thead>
          <tbody>
            {visibles.map((c) => (
              <tr key={c.conductor_id} style={{ borderTop: "1px solid var(--rz-panel-border)" }}>
                <Td>{c.nombre}</Td>
                <Td mono>{c.dni}</Td>
                <Td mono>{c.categoria_licencia}</Td>
                <Td mono>
                  {c.telefono}
                  {c.correo && <div style={{ fontSize: 11.5, color: "var(--rz-text-muted)" }}>{c.correo}</div>}
                </Td>
                <Td mono>
                  <EstadoVencimiento fecha={c.licencia_vence} />
                </Td>
                <Td mono>
                  {hora(c.horario_inicio)}–{hora(c.horario_fin)}
                </Td>
                <Td>
                  <select
                    aria-label={`Disponibilidad de ${c.nombre}`}
                    value={c.disponible ? "si" : "no"}
                    onChange={(e) => void cambiarDisponibilidad(c.conductor_id, e.target.value === "si")}
                    style={{
                      background: "var(--rz-bg)",
                      color: "var(--rz-text)",
                      border: "1px solid var(--rz-panel-border)",
                      borderRadius: 8,
                      padding: "4px 8px",
                      fontSize: 12.5,
                    }}
                  >
                    <option value="si">Disponible</option>
                    <option value="no">No disponible</option>
                  </select>
                </Td>
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
                <td colSpan={8} style={{ padding: 24, textAlign: "center", color: "var(--rz-text-muted)" }}>
                  {filtro === "todos" ? "No hay conductores registrados todavía." : "No hay conductores en esta categoría."}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {detalle && (
        <Modal titulo={detalle.nombre} onCerrar={() => setDetalle(null)}>
          <FilaDetalle etiqueta="DNI" valor={detalle.dni} />
          <FilaDetalle etiqueta="Categoría de licencia" valor={detalle.categoria_licencia} />
          <FilaDetalle etiqueta="Licencia vence" valor={<EstadoVencimiento fecha={detalle.licencia_vence} />} />
          <FilaDetalle etiqueta="Teléfono" valor={detalle.telefono} />
          <FilaDetalle etiqueta="Correo" valor={detalle.correo ?? "—"} />
          <FilaDetalle
            etiqueta="Disponible"
            valor={`${hora(detalle.horario_inicio)} – ${hora(detalle.horario_fin)}`}
          />
          <FilaDetalle etiqueta="Estado" valor={detalle.disponible ? "Disponible" : "No disponible"} />
          <FilaDetalle etiqueta="Horas conducidas hoy" valor={`${detalle.horas_conducidas_hoy} h`} />
          <FilaDetalle
            etiqueta="Consentimiento de datos"
            valor={new Date(detalle.consentimiento_en).toLocaleDateString("es-PE")}
          />
          <button type="button" onClick={() => setDetalle(null)} style={estiloBotonSecundario}>
            Cerrar
          </button>
        </Modal>
      )}

      {edicion && (
        <Modal titulo={`Editar a ${edicion.nombre}`} onCerrar={() => setEdicion(null)} ancho={680}>
          <FormularioConductor
            inicial={edicion}
            onGuardado={() => {
              setEdicion(null);
              void cargar();
              notificar("Conductor actualizado", "exito");
            }}
          />
        </Modal>
      )}
    </div>
  );
}

// Fecha de mañana en formato AAAA-MM-DD: la licencia debe vencer después de hoy.
function mañana(): string {
  const d = new Date();
  d.setDate(d.getDate() + 1);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

function FormularioConductor({ inicial, onGuardado }: { inicial?: Conductor; onGuardado: () => void }) {
  const [nombre, setNombre] = useState(inicial?.nombre ?? "");
  const [dni, setDni] = useState(inicial?.dni ?? "");
  const [categoria, setCategoria] = useState(inicial?.categoria_licencia ?? "A-IIb");
  const [telefono, setTelefono] = useState(inicial?.telefono ?? "");
  const [correo, setCorreo] = useState(inicial?.correo ?? "");
  const [licenciaVence, setLicenciaVence] = useState(inicial?.licencia_vence ?? "");
  const [horarioInicio, setHorarioInicio] = useState(inicial ? hora(inicial.horario_inicio) : "06:00");
  const [horarioFin, setHorarioFin] = useState(inicial ? hora(inicial.horario_fin) : "14:00");
  const [consentimiento, setConsentimiento] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function enviar(evento: FormEvent) {
    evento.preventDefault();
    setError(null);
    setEnviando(true);
    try {
      const cuerpo = {
        nombre: nombre.trim(),
        dni,
        categoria_licencia: categoria,
        telefono: telefono.replace(/\s/g, ""),
        correo: correo.trim() || null,
        licencia_vence: licenciaVence,
        horario_inicio: `${horarioInicio}:00`,
        horario_fin: `${horarioFin}:00`,
      };
      if (inicial) {
        const original = {
          nombre: inicial.nombre,
          dni: inicial.dni,
          categoria_licencia: inicial.categoria_licencia,
          telefono: inicial.telefono,
          correo: inicial.correo,
          licencia_vence: inicial.licencia_vence,
          horario_inicio: `${hora(inicial.horario_inicio)}:00`,
          horario_fin: `${hora(inicial.horario_fin)}:00`,
        };
        const cambios = soloCambios(original, cuerpo);
        if (Object.keys(cambios).length === 0) {
          setError("No hay cambios para guardar");
          return;
        }
        await api.put(`/api/conductores/${inicial.conductor_id}`, cambios);
      } else {
        await api.post("/api/conductores", { ...cuerpo, consentimiento_datos: consentimiento });
      }
      onGuardado();
    } catch (err) {
      setError(mensajeDeError(err, inicial ? "No se pudo actualizar el conductor" : "No se pudo registrar el conductor"));
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
      <CampoTexto etiqueta="Nombre completo" valor={nombre} onCambio={setNombre} atributos={{ maxLength: 100 }} />
      <CampoTexto
        etiqueta="DNI"
        valor={dni}
        onCambio={(v) => setDni(v.replace(/\D/g, "").slice(0, 8))}
        atributos={{ inputMode: "numeric", pattern: "[0-9]{8}", title: "8 dígitos", maxLength: 8 }}
      />
      <CampoSelect
        etiqueta="Categoría de licencia"
        valor={categoria}
        opciones={CATEGORIAS}
        onCambio={setCategoria}
        ayuda="Categoría que figura en su licencia de conducir. Debe corresponder al tipo de vehículo que va a manejar."
      />
      <CampoTexto
        etiqueta="Teléfono de contacto"
        valor={telefono}
        onCambio={setTelefono}
        tipo="tel"
        atributos={{ pattern: "\\+?[0-9 ]{7,17}", title: "Solo dígitos, entre 7 y 15", maxLength: 17 }}
      />
      <CampoTexto
        etiqueta="Correo electrónico"
        valor={correo}
        onCambio={setCorreo}
        tipo="email"
        opcional
        ayuda="Para contactarlo o, más adelante, vincular su cuenta de acceso. Puedes dejarlo en blanco."
      />
      <CampoTexto
        etiqueta="Vencimiento de la licencia"
        ayuda="Fecha de revalidación que figura en su licencia. Debe ser posterior a hoy: con la licencia vencida no puede recibir rutas."
        valor={licenciaVence}
        onCambio={setLicenciaVence}
        tipo="date"
        atributos={inicial ? undefined : { min: mañana() }}
      />
      <CampoTexto
        etiqueta="Disponible desde"
        valor={horarioInicio}
        onCambio={setHorarioInicio}
        tipo="time"
        ayuda="Hora desde la que puede recibir rutas. Entre el inicio y el fin no pueden pasar más de 8 horas (jornada máxima)."
      />
      <CampoTexto
        etiqueta="Disponible hasta"
        valor={horarioFin}
        onCambio={setHorarioFin}
        tipo="time"
        ayuda="Hora hasta la que puede recibir rutas. Debe ser posterior a la hora de inicio."
      />

      {!inicial && (
        <label
          style={{
            gridColumn: "1 / -1",
            display: "flex",
            gap: 10,
            alignItems: "flex-start",
            fontSize: 13,
            color: "var(--rz-text-muted)",
            lineHeight: 1.5,
          }}
        >
          <input
            type="checkbox"
            required
            checked={consentimiento}
            onChange={(e) => setConsentimiento(e.target.checked)}
            style={{ marginTop: 3 }}
          />
          El conductor autoriza de forma expresa el tratamiento de sus datos personales (nombre, DNI, licencia y contacto)
          para la asignación de rutas, conforme a la Ley N° 29733.
        </label>
      )}

      {error && <div style={{ ...estiloAviso, gridColumn: "1 / -1" }}>{error}</div>}
      <div style={{ gridColumn: "1 / -1" }}>
        <button type="submit" disabled={enviando} style={estiloBotonPrimario}>
          {enviando ? "Guardando…" : inicial ? "Guardar cambios" : "Guardar conductor"}
        </button>
      </div>
    </form>
  );
}
