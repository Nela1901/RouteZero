import { useEffect, useState } from "react";
import { api } from "../api/client";

const formato = (kg: number) => kg.toLocaleString("es-PE", { minimumFractionDigits: 1, maximumFractionDigits: 1 });

/** undefined: cargando; null: no se pudo cargar. */
function textoDelValor(kg: number | null | undefined): string {
  if (kg === undefined) return "…";
  if (kg === null) return "—";
  return formato(kg);
}

/**
 * CO₂ que emitieron hoy las rutas confirmadas, en el encabezado. Solo lo ve el administrador (el dashboard de
 * sostenibilidad es suyo). Se consulta una vez al abrir el panel, sin sondeos: cada consulta cuesta energía.
 * Es emisión, no «evitado»: el módulo calcula lo que se emite y el combustible que se ahorra, no un CO₂ evitado.
 */
export function PastillaCo2() {
  // undefined: cargando; null: no se pudo cargar
  const [kg, setKg] = useState<number | null | undefined>(undefined);

  useEffect(() => {
    let activo = true;
    // Fecha de hoy en Perú (formato AAAA-MM-DD), sin importar la zona horaria del equipo
    const hoy = new Date().toLocaleDateString("en-CA", { timeZone: "America/Lima" });
    api
      .get<{ totales: { emision_co2_kg: number } }>(`/api/sostenibilidad/dashboard?desde=${hoy}&hasta=${hoy}`)
      .then((dashboard) => {
        if (activo) setKg(dashboard.totales.emision_co2_kg);
      })
      .catch(() => {
        if (activo) setKg(null);
      });
    return () => {
      activo = false;
    };
  }, []);

  const valor = textoDelValor(kg);
  return (
    <output
      aria-label={typeof kg === "number" ? `CO2 emitido hoy: ${formato(kg)} kilogramos` : "CO2 emitido hoy: sin dato"}
      title={kg === null ? "No se pudo cargar el dato de hoy" : undefined}
      className="rz-pastilla-co2"
      style={{
        display: "flex",
        alignItems: "center",
        gap: 10,
        padding: "10px 18px",
        borderRadius: 999,
        background: "var(--rz-accent-soft-bg)",
        border: "1px solid var(--rz-accent-soft-border)",
      }}
    >
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--rz-accent)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M11 20A7 7 0 019.8 6.1C15.5 5 17 3 17 3s.5 3.5 2 6c1.6 2.7 1.5 6-1 8-1 1-2.5 1-3.5 1" />
        <path d="M2 21c0-3.5 2.5-6 5-6" />
      </svg>
      <span style={{ fontFamily: "var(--rz-font-mono)", fontWeight: 600, fontSize: 15, color: "var(--rz-accent)" }}>{valor} kg CO₂</span>
      <span className="rz-pastilla-co2-texto" style={{ fontSize: 12.5, color: "var(--rz-text-muted)" }}>
        emitidos hoy
      </span>
    </output>
  );
}
