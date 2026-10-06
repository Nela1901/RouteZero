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
  estiloInput,
  EstadoVencimiento,
  FiltroChip,
  Td,
  Th,
} from "../../components/ui";

type EstadoVehiculo = "DISPONIBLE" | "EN_RUTA" | "MANTENIMIENTO" | "INACTIVO";
type TipoVehiculo = "CAMIONETA" | "FURGON" | "MOTO";

interface Vehiculo {
  vehiculo_id: string;
  placa: string;
  tipo: TipoVehiculo;
  capacidad_kg: string;
  consumo_km_l: string;
  factor_emision_co2: string;
  anio_fabricacion: number;
  estado: EstadoVehiculo;
  soat_vence: string | null;
  revision_tecnica_vence: string | null;
}

const ESTADOS: EstadoVehiculo[] = ["DISPONIBLE", "EN_RUTA", "MANTENIMIENTO", "INACTIVO"];
const TIPOS: TipoVehiculo[] = ["CAMIONETA", "FURGON", "MOTO"];

export function FlotaPage() {
  const { notificar } = useToast();
  const { confirmar } = useConfirm();
  const [vehiculos, setVehiculos] = useState<Vehiculo[]>([]);
  const [filtroEstado, setFiltroEstado] = useState<EstadoVehiculo | "">("");
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [detalle, setDetalle] = useState<Vehiculo | null>(null);
  const [edicion, setEdicion] = useState<Vehiculo | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Se carga la flota completa una sola vez y el filtro se aplica en el navegador: la flota es
  // pequeña y así cambiar de filtro es instantáneo en vez de costar un viaje a la base remota.
  async function cargar() {
    try {
      setVehiculos(await api.get<Vehiculo[]>("/api/vehiculos"));
    } catch (err) {
      setError(mensajeDeError(err, "No se pudo cargar la flota"));
    }
  }

  const visibles = filtroEstado ? vehiculos.filter((v) => v.estado === filtroEstado) : vehiculos;

  useEffect(() => {
    void cargar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function cambiarEstado(vehiculoId: string, estado: EstadoVehiculo) {
    await actualizar(vehiculoId, { estado }, `Vehículo actualizado a ${estado.replace("_", " ")}`);
  }

  async function renovarDocumento(
    vehiculoId: string,
    campo: "soat_vence" | "revision_tecnica_vence",
    fecha: string,
  ) {
    if (!fecha) return;
    await actualizar(vehiculoId, { [campo]: fecha }, "Fecha de vencimiento actualizada");
  }

  async function actualizar(vehiculoId: string, cambios: Record<string, string>, exito: string) {
    setError(null);
    try {
      await api.put(`/api/vehiculos/${vehiculoId}`, cambios);
      await cargar();
      notificar(exito, "exito");
    } catch (err) {
      const mensaje = mensajeDeError(err, "No se pudo actualizar el vehículo");
      setError(mensaje);
      notificar(mensaje, "error");
    }
  }

  async function eliminar(vehiculo: Vehiculo) {
    const acepto = await confirmar({
      titulo: "Eliminar vehículo",
      mensaje: `Se eliminará el vehículo ${vehiculo.placa}. Esta acción no se puede deshacer.`,
      textoAceptar: "Eliminar",
      peligroso: true,
    });
    if (!acepto) return;
    try {
      await api.delete(`/api/vehiculos/${vehiculo.vehiculo_id}`);
      await cargar();
      notificar("Vehículo eliminado", "exito");
    } catch (err) {
      notificar(mensajeDeError(err, "No se pudo eliminar el vehículo"), "error");
    }
  }

  return (
    <div style={{ padding: 28, display: "flex", flexDirection: "column", gap: 20, maxWidth: 1440 }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div>
          <h1 style={{ fontFamily: "var(--rz-font-display)", fontSize: 22, margin: "0 0 4px" }}>Flota de vehículos</h1>
          <p style={{ margin: 0, fontSize: 13, color: "var(--rz-text-muted)" }}>
            Registro, edición de estado y disponibilidad de la flota.
          </p>
        </div>
        <button type="button" onClick={() => setMostrarFormulario((v) => !v)} style={estiloBotonPrimario}>
          {mostrarFormulario ? "Cancelar" : "Registrar vehículo"}
        </button>
      </div>

      {mostrarFormulario && (
        <FormularioVehiculo
          onGuardado={() => {
            setMostrarFormulario(false);
            void cargar();
            notificar("Vehículo registrado", "exito");
          }}
        />
      )}

      {error && <div style={estiloAviso}>{error}</div>}

      <div style={{ display: "flex", gap: 8 }}>
        <FiltroChip etiqueta="Todos" activo={filtroEstado === ""} onClick={() => setFiltroEstado("")} />
        {ESTADOS.map((estado) => (
          <FiltroChip
            key={estado}
            etiqueta={estado.replace("_", " ")}
            activo={filtroEstado === estado}
            onClick={() => setFiltroEstado(estado)}
          />
        ))}
      </div>

      <div style={{ borderRadius: 16, border: "1px solid var(--rz-panel-border)", overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13.5 }}>
          <thead>
            <tr style={{ background: "var(--rz-panel-bg)", textAlign: "left" }}>
              <Th>Placa</Th>
              <Th>Tipo</Th>
              <Th>Capacidad (kg)</Th>
              <Th>Año</Th>
              <Th>SOAT vence</Th>
              <Th>Rev. técnica vence</Th>
              <Th>Estado</Th>
              <Th>Acciones</Th>
            </tr>
          </thead>
          <tbody>
            {visibles.map((v) => (
              <tr key={v.vehiculo_id} style={{ borderTop: "1px solid var(--rz-panel-border)" }}>
                <Td mono>{v.placa}</Td>
                <Td>{v.tipo}</Td>
                <Td mono>{v.capacidad_kg}</Td>
                <Td mono>{v.anio_fabricacion}</Td>
                <Td mono>
                  <CeldaDocumento
                    etiqueta={`SOAT de ${v.placa}`}
                    fecha={v.soat_vence}
                    onCambio={(f) => void renovarDocumento(v.vehiculo_id, "soat_vence", f)}
                  />
                </Td>
                <Td mono>
                  <CeldaDocumento
                    etiqueta={`Revisión técnica de ${v.placa}`}
                    fecha={v.revision_tecnica_vence}
                    onCambio={(f) => void renovarDocumento(v.vehiculo_id, "revision_tecnica_vence", f)}
                  />
                </Td>
                <Td>
                  <select
                    aria-label={`Estado del vehículo ${v.placa}`}
                    value={v.estado}
                    onChange={(e) => void cambiarEstado(v.vehiculo_id, e.target.value as EstadoVehiculo)}
                    style={{
                      background: "var(--rz-bg)",
                      color: "var(--rz-text)",
                      border: "1px solid var(--rz-panel-border)",
                      borderRadius: 8,
                      padding: "4px 8px",
                      fontSize: 12.5,
                    }}
                  >
                    {ESTADOS.map((estado) => (
                      <option key={estado} value={estado}>
                        {estado.replace("_", " ")}
                      </option>
                    ))}
                  </select>
                </Td>
                <Td>
                  <AccionesFila
                    nombre={v.placa}
                    onVer={() => setDetalle(v)}
                    onEditar={() => setEdicion(v)}
                    onEliminar={() => void eliminar(v)}
                  />
                </Td>
              </tr>
            ))}
            {visibles.length === 0 && (
              <tr>
                <td colSpan={8} style={{ padding: 24, textAlign: "center", color: "var(--rz-text-muted)" }}>
                  {filtroEstado ? "No hay vehículos con ese estado." : "No hay vehículos registrados todavía."}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {detalle && (
        <Modal titulo={`Vehículo ${detalle.placa}`} onCerrar={() => setDetalle(null)}>
          <FilaDetalle etiqueta="Tipo" valor={detalle.tipo} />
          <FilaDetalle etiqueta="Estado" valor={detalle.estado.replace("_", " ")} />
          <FilaDetalle etiqueta="Capacidad" valor={`${detalle.capacidad_kg} kg`} />
          <FilaDetalle etiqueta="Consumo" valor={`${detalle.consumo_km_l} km/L`} />
          <FilaDetalle etiqueta="Factor de CO₂" valor={`${detalle.factor_emision_co2} kg/km`} />
          <FilaDetalle etiqueta="Año de fabricación" valor={detalle.anio_fabricacion} />
          <FilaDetalle etiqueta="SOAT vence" valor={<EstadoVencimiento fecha={detalle.soat_vence} />} />
          <FilaDetalle
            etiqueta="Revisión técnica vence"
            valor={<EstadoVencimiento fecha={detalle.revision_tecnica_vence} />}
          />
          <button type="button" onClick={() => setDetalle(null)} style={estiloBotonSecundario}>
            Cerrar
          </button>
        </Modal>
      )}

      {edicion && (
        <Modal titulo={`Editar vehículo ${edicion.placa}`} onCerrar={() => setEdicion(null)} ancho={680}>
          <FormularioVehiculo
            inicial={edicion}
            onGuardado={() => {
              setEdicion(null);
              void cargar();
              notificar("Vehículo actualizado", "exito");
            }}
          />
        </Modal>
      )}
    </div>
  );
}

function CeldaDocumento(props: { etiqueta: string; fecha: string | null; onCambio: (fecha: string) => void }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
      <input
        type="date"
        aria-label={props.etiqueta}
        value={props.fecha ?? ""}
        onChange={(e) => props.onCambio(e.target.value)}
        style={{ ...estiloInput, height: 30, fontSize: 12.5, padding: "0 8px" }}
      />
      <EstadoVencimiento fecha={props.fecha} />
    </div>
  );
}

function FormularioVehiculo({ inicial, onGuardado }: { inicial?: Vehiculo; onGuardado: () => void }) {
  const [placa, setPlaca] = useState(inicial?.placa ?? "");
  const [tipo, setTipo] = useState<TipoVehiculo>(inicial?.tipo ?? "CAMIONETA");
  const [capacidadKg, setCapacidadKg] = useState(inicial?.capacidad_kg ?? "");
  const [consumoKmL, setConsumoKmL] = useState(inicial?.consumo_km_l ?? "");
  const [factorEmision, setFactorEmision] = useState(inicial?.factor_emision_co2 ?? "");
  const [anio, setAnio] = useState(inicial ? String(inicial.anio_fabricacion) : String(new Date().getFullYear()));
  const [soatVence, setSoatVence] = useState(inicial?.soat_vence ?? "");
  const [revisionVence, setRevisionVence] = useState(inicial?.revision_tecnica_vence ?? "");
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function enviar(evento: FormEvent) {
    evento.preventDefault();
    setError(null);
    setEnviando(true);
    try {
      const cuerpo = {
        placa: placa.trim().toUpperCase(),
        tipo,
        capacidad_kg: capacidadKg,
        consumo_km_l: consumoKmL,
        factor_emision_co2: factorEmision,
        anio_fabricacion: Number(anio),
        soat_vence: soatVence || null,
        revision_tecnica_vence: revisionVence || null,
      };
      if (inicial) {
        const original = {
          placa: inicial.placa,
          tipo: inicial.tipo,
          capacidad_kg: inicial.capacidad_kg,
          consumo_km_l: inicial.consumo_km_l,
          factor_emision_co2: inicial.factor_emision_co2,
          anio_fabricacion: inicial.anio_fabricacion,
          soat_vence: inicial.soat_vence,
          revision_tecnica_vence: inicial.revision_tecnica_vence,
        };
        const cambios = soloCambios(original, cuerpo);
        if (Object.keys(cambios).length === 0) {
          setError("No hay cambios para guardar");
          return;
        }
        await api.put(`/api/vehiculos/${inicial.vehiculo_id}`, cambios);
      } else {
        await api.post("/api/vehiculos", cuerpo);
      }
      onGuardado();
    } catch (err) {
      setError(mensajeDeError(err, inicial ? "No se pudo actualizar el vehículo" : "No se pudo registrar el vehículo"));
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
        etiqueta="Placa"
        valor={placa}
        onCambio={setPlaca}
        ayuda="Matrícula del vehículo, por ejemplo ABC-123. Se guarda en mayúsculas y debe ser única en la flota."
      />
      <CampoSelect
        etiqueta="Tipo"
        valor={tipo}
        opciones={TIPOS}
        onCambio={(v) => setTipo(v as TipoVehiculo)}
        ayuda="Clase del vehículo: camioneta, furgón o moto. Sirve para repartir los pedidos según su tamaño."
      />
      <CampoTexto
        etiqueta="Capacidad (kg)"
        valor={capacidadKg}
        onCambio={setCapacidadKg}
        tipo="number"
        paso="0.01"
        ayuda="Peso máximo de carga que puede llevar, en kilogramos (figura en la tarjeta de propiedad). Ejemplo: 1500. El optimizador no le asigna más peso que este valor."
      />
      <CampoTexto
        etiqueta="Consumo (km/L)"
        valor={consumoKmL}
        onCambio={setConsumoKmL}
        tipo="number"
        paso="0.01"
        ayuda="Kilómetros que recorre con un litro de combustible. Ejemplo: 10.5. Cuanto más alto, menos combustible gasta."
      />
      <CampoTexto
        etiqueta="Factor CO₂ (kg/km)"
        valor={factorEmision}
        onCambio={setFactorEmision}
        tipo="number"
        paso="0.0001"
        ayuda="Kilogramos de CO₂ que emite por cada kilómetro. Ejemplo: 0.25. Si no lo conoces, una referencia aproximada es dividir 2.3 (gasolina) o 2.7 (diésel) entre el consumo en km/L."
      />
      <CampoTexto
        etiqueta="Año de fabricación"
        valor={anio}
        onCambio={setAnio}
        tipo="number"
        paso="1"
        ayuda="Año de fabricación que figura en la tarjeta de propiedad."
      />
      <CampoTexto
        etiqueta="Vencimiento del SOAT"
        valor={soatVence}
        onCambio={setSoatVence}
        tipo="date"
        opcional={Boolean(inicial)}
        ayuda="Fecha hasta la que está vigente el Seguro Obligatorio de Accidentes de Tránsito (figura en el certificado). Se avisa 30 días antes de que venza."
      />
      <CampoTexto
        etiqueta="Vencimiento de la revisión técnica"
        valor={revisionVence}
        onCambio={setRevisionVence}
        tipo="date"
        opcional={Boolean(inicial)}
        ayuda="Fecha hasta la que es válido el certificado de inspección técnica vehicular. Se avisa 30 días antes de que venza."
      />
      {error && <div style={{ ...estiloAviso, gridColumn: "1 / -1" }}>{error}</div>}
      <div style={{ gridColumn: "1 / -1" }}>
        <button type="submit" disabled={enviando} style={estiloBotonPrimario}>
          {enviando ? "Guardando…" : inicial ? "Guardar cambios" : "Guardar vehículo"}
        </button>
      </div>
    </form>
  );
}
