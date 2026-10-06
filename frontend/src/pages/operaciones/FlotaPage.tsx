import { useEffect, useState, type FormEvent } from "react";
import { api, mensajeDeError } from "../../api/client";
import { useToast } from "../../context/ToastContext";

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
}

const ESTADOS: EstadoVehiculo[] = ["DISPONIBLE", "EN_RUTA", "MANTENIMIENTO", "INACTIVO"];
const TIPOS: TipoVehiculo[] = ["CAMIONETA", "FURGON", "MOTO"];

export function FlotaPage() {
  const { notificar } = useToast();
  const [vehiculos, setVehiculos] = useState<Vehiculo[]>([]);
  const [filtroEstado, setFiltroEstado] = useState<EstadoVehiculo | "">("");
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
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
    setError(null);
    try {
      await api.put(`/api/vehiculos/${vehiculoId}`, { estado });
      await cargar();
      notificar(`Vehículo actualizado a ${estado.replace("_", " ")}`, "exito");
    } catch (err) {
      const mensaje = mensajeDeError(err, "No se pudo actualizar el vehículo");
      setError(mensaje);
      notificar(mensaje, "error");
    }
  }

  return (
    <div style={{ padding: 28, display: "flex", flexDirection: "column", gap: 20, maxWidth: 1040 }}>
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
          onCreado={() => {
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
              <Th>Estado</Th>
            </tr>
          </thead>
          <tbody>
            {visibles.map((v) => (
              <tr key={v.vehiculo_id} style={{ borderTop: "1px solid var(--rz-panel-border)" }}>
                <Td mono>{v.placa}</Td>
                <Td>{v.tipo}</Td>
                <Td mono>{v.capacidad_kg}</Td>
                <Td mono>{v.anio_fabricacion}</Td>
                <Td>
                  <select
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
              </tr>
            ))}
            {visibles.length === 0 && (
              <tr>
                <td colSpan={5} style={{ padding: 24, textAlign: "center", color: "var(--rz-text-muted)" }}>
                  {filtroEstado ? "No hay vehículos con ese estado." : "No hay vehículos registrados todavía."}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function FormularioVehiculo({ onCreado }: { onCreado: () => void }) {
  const [placa, setPlaca] = useState("");
  const [tipo, setTipo] = useState<TipoVehiculo>("CAMIONETA");
  const [capacidadKg, setCapacidadKg] = useState("");
  const [consumoKmL, setConsumoKmL] = useState("");
  const [factorEmision, setFactorEmision] = useState("");
  const [anio, setAnio] = useState(String(new Date().getFullYear()));
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function enviar(evento: FormEvent) {
    evento.preventDefault();
    setError(null);
    setEnviando(true);
    try {
      await api.post("/api/vehiculos", {
        placa: placa.trim().toUpperCase(),
        tipo,
        capacidad_kg: capacidadKg,
        consumo_km_l: consumoKmL,
        factor_emision_co2: factorEmision,
        anio_fabricacion: Number(anio),
      });
      onCreado();
    } catch (err) {
      setError(mensajeDeError(err, "No se pudo registrar el vehículo"));
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
        padding: 20,
        borderRadius: 16,
        background: "var(--rz-panel-bg)",
        border: "1px solid var(--rz-panel-border)",
      }}
    >
      <CampoTexto etiqueta="Placa" valor={placa} onCambio={setPlaca} />
      <CampoSelect etiqueta="Tipo" valor={tipo} opciones={TIPOS} onCambio={(v) => setTipo(v as TipoVehiculo)} />
      <CampoTexto etiqueta="Capacidad (kg)" valor={capacidadKg} onCambio={setCapacidadKg} tipo="number" paso="0.01" />
      <CampoTexto etiqueta="Consumo (km/L)" valor={consumoKmL} onCambio={setConsumoKmL} tipo="number" paso="0.01" />
      <CampoTexto etiqueta="Factor CO₂ (kg/km)" valor={factorEmision} onCambio={setFactorEmision} tipo="number" paso="0.0001" />
      <CampoTexto etiqueta="Año de fabricación" valor={anio} onCambio={setAnio} tipo="number" paso="1" />
      {error && <div style={{ ...estiloAviso, gridColumn: "1 / -1" }}>{error}</div>}
      <div style={{ gridColumn: "1 / -1" }}>
        <button type="submit" disabled={enviando} style={estiloBotonPrimario}>
          {enviando ? "Registrando…" : "Guardar vehículo"}
        </button>
      </div>
    </form>
  );
}

function CampoTexto(props: { etiqueta: string; valor: string; onCambio: (v: string) => void; tipo?: string; paso?: string }) {
  return (
    <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: 12.5, color: "var(--rz-text-muted)" }}>
      {props.etiqueta}
      <input
        required
        type={props.tipo ?? "text"}
        step={props.paso}
        value={props.valor}
        onChange={(e) => props.onCambio(e.target.value)}
        style={estiloInput}
      />
    </label>
  );
}

function CampoSelect(props: { etiqueta: string; valor: string; opciones: string[]; onCambio: (v: string) => void }) {
  return (
    <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: 12.5, color: "var(--rz-text-muted)" }}>
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

function FiltroChip({ etiqueta, activo, onClick }: { etiqueta: string; activo: boolean; onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      style={{
        padding: "6px 14px",
        borderRadius: 999,
        border: "1px solid " + (activo ? "var(--rz-accent-soft-border)" : "var(--rz-panel-border)"),
        background: activo ? "var(--rz-accent-soft-bg)" : "transparent",
        color: activo ? "var(--rz-accent)" : "var(--rz-text-muted)",
        fontSize: 12.5,
        cursor: "pointer",
      }}
    >
      {etiqueta}
    </button>
  );
}

function Th({ children }: { children: React.ReactNode }) {
  return <th style={{ padding: "10px 16px", fontWeight: 600, color: "var(--rz-text-muted)", fontSize: 12 }}>{children}</th>;
}

function Td({ children, mono }: { children: React.ReactNode; mono?: boolean }) {
  return (
    <td style={{ padding: "10px 16px", fontFamily: mono ? "var(--rz-font-mono)" : "inherit" }}>{children}</td>
  );
}

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
