import { useId, useState } from "react";
import { limitarDecimales } from "./utilesCrud";

/** Piezas de interfaz compartidas por las pantallas de gestión (flota, conductores, ...). */

/**
 * Ícono "i" con una explicación breve. Se abre al pasar el mouse, al enfocarlo con el teclado
 * o al tocarlo (móvil); se cierra al salir, al perder el foco o con Escape.
 */
export function Ayuda({ texto }: { texto: string }) {
  const [abierta, setAbierta] = useState(false);
  const id = useId();
  return (
    <span
      style={{ position: "relative", display: "inline-flex", verticalAlign: "middle", marginLeft: 6 }}
      onMouseEnter={() => setAbierta(true)}
      onMouseLeave={() => setAbierta(false)}
    >
      <button
        type="button"
        aria-label="Más información"
        aria-expanded={abierta}
        aria-describedby={abierta ? id : undefined}
        onClick={() => setAbierta(true)}
        onFocus={() => setAbierta(true)}
        onBlur={() => setAbierta(false)}
        onKeyDown={(e) => e.key === "Escape" && setAbierta(false)}
        style={{
          width: 16,
          height: 16,
          borderRadius: "50%",
          border: "1px solid var(--rz-panel-border)",
          background: "transparent",
          color: "var(--rz-text-muted)",
          fontSize: 10.5,
          fontWeight: 700,
          fontStyle: "italic",
          lineHeight: 1,
          padding: 0,
          cursor: "help",
        }}
      >
        i
      </button>
      {abierta && (
        <span
          role="tooltip"
          id={id}
          style={{
            position: "absolute",
            top: "calc(100% + 6px)",
            left: -8,
            zIndex: 20,
            width: "max-content",
            maxWidth: "min(260px, calc(100vw - 64px))",
            padding: "8px 10px",
            borderRadius: 10,
            background: "var(--rz-panel-solid-bg)",
            border: "1px solid var(--rz-panel-border)",
            boxShadow: "0 8px 24px rgba(0, 0, 0, 0.25)",
            color: "var(--rz-text)",
            fontSize: 12,
            fontWeight: 400,
            lineHeight: 1.45,
            whiteSpace: "normal",
          }}
        >
          {texto}
        </span>
      )}
    </span>
  );
}

export function CampoTexto(props: { etiqueta: string; valor: string; onCambio: (v: string) => void; tipo?: string; paso?: string; opcional?: boolean; ayuda?: string; atributos?: React.InputHTMLAttributes<HTMLInputElement> }) {
  const id = useId();
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: 12.5, color: "var(--rz-text-muted)" }}>
      <span>
        <label htmlFor={id}>
          {props.etiqueta}
          {props.opcional && <span style={{ fontWeight: 400 }}> (opcional)</span>}
        </label>
        {props.ayuda && <Ayuda texto={props.ayuda} />}
      </span>
      <input
        id={id}
        required={!props.opcional}
        type={props.tipo ?? "text"}
        step={props.paso}
        value={props.valor}
        onChange={(e) =>
          props.onCambio(props.tipo === "number" ? limitarDecimales(e.target.value, props.paso) : e.target.value)
        }
        // Un número de negocio (peso, capacidad, año) es siempre positivo y sin notación científica.
        onKeyDown={props.tipo === "number" ? (e) => ["e", "E", "+", "-"].includes(e.key) && e.preventDefault() : undefined}
        min={props.tipo === "number" ? (props.paso ?? "1") : undefined}
        style={estiloInput}
        {...props.atributos}
      />
    </div>
  );
}

export function CampoSelect(props: { etiqueta: string; valor: string; opciones: string[]; onCambio: (v: string) => void; ayuda?: string }) {
  const id = useId();
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: 12.5, color: "var(--rz-text-muted)" }}>
      <span>
        <label htmlFor={id}>{props.etiqueta}</label>
        {props.ayuda && <Ayuda texto={props.ayuda} />}
      </span>
      <select id={id} value={props.valor} onChange={(e) => props.onCambio(e.target.value)} style={estiloInput}>
        {props.opciones.map((o) => (
          <option key={o} value={o}>
            {o}
          </option>
        ))}
      </select>
    </div>
  );
}

export function FiltroChip({ etiqueta, activo, onClick }: { etiqueta: string; activo: boolean; onClick: () => void }) {
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

export function Th({ children }: { children: React.ReactNode }) {
  return <th style={{ padding: "10px 16px", fontWeight: 600, color: "var(--rz-text-muted)", fontSize: 12 }}>{children}</th>;
}

export function Td({ children, mono }: { children: React.ReactNode; mono?: boolean }) {
  return (
    <td style={{ padding: "10px 16px", fontFamily: mono ? "var(--rz-font-mono)" : "inherit" }}>{children}</td>
  );
}

export const estiloBotonPrimario: React.CSSProperties = {
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

export const estiloInput: React.CSSProperties = {
  height: 38,
  borderRadius: 10,
  border: "1px solid var(--rz-panel-border)",
  background: "var(--rz-bg)",
  color: "var(--rz-text)",
  padding: "0 12px",
  fontSize: 13.5,
};

export const estiloAviso: React.CSSProperties = {
  borderRadius: 10,
  background: "var(--rz-danger-soft-bg)",
  color: "var(--rz-danger)",
  padding: "10px 12px",
  fontSize: 13,
};

/** Fecha de vencimiento de un documento (licencia, SOAT, revisión técnica) con aviso a 30 días o menos. */
const DIAS_AVISO_VENCIMIENTO = 30;

// Días que faltan para que venza un documento (negativo si ya venció).
export function diasParaVencer(fecha: string): number {
  const vence = new Date(`${fecha}T00:00:00`);
  const hoy = new Date();
  hoy.setHours(0, 0, 0, 0);
  return Math.round((vence.getTime() - hoy.getTime()) / 86_400_000);
}

export function EstadoVencimiento({ fecha }: { fecha: string | null }) {
  if (!fecha) return <span style={{ color: "var(--rz-text-muted)" }}>—</span>;
  const dias = diasParaVencer(fecha);
  const [aviso, color] =
    dias < 0
      ? ["Vencida", "var(--rz-danger)"]
      : dias <= DIAS_AVISO_VENCIMIENTO
        ? [`Vence en ${dias} d`, "var(--rz-warning, #b7791f)"]
        : [null, ""];
  return (
    <span style={{ display: "inline-flex", flexDirection: "column", gap: 2 }}>
      <span>{fecha}</span>
      {aviso && <span style={{ fontSize: 11.5, fontWeight: 600, color }}>{aviso}</span>}
    </span>
  );
}
