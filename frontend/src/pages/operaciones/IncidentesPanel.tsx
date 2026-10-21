import { useEffect, useState } from "react";
import { api, mensajeDeError } from "../../api/client";
import { useToast } from "../../context/ToastContext";
import { Ayuda, CampoSelect, estiloAviso, estiloBotonPrimario } from "../../components/ui";

interface Incidente {
  incidente_id: string;
  calle: string;
  factor: number;
  descripcion: string | null;
  activo: boolean;
  creado_en: string;
}

// Las tres vías que la RN-012 permite reportar
const CALLES = ["Av. Ferrocarril", "Av. Giráldez", "Calle Real"];
const FACTORES: Record<string, number> = { "1.5 veces más lento": 1.5, "2 veces más lento": 2, "3 veces más lento": 3, "5 veces más lento": 5 };

/** Alertas de congestión activas. Cada re-optimización las aplica; solo el Administrador las registra y resuelve. */
export function IncidentesPanel({ esAdministrador }: { esAdministrador: boolean }) {
  const { notificar } = useToast();
  const [incidentes, setIncidentes] = useState<Incidente[]>([]);
  const [calle, setCalle] = useState(CALLES[0]);
  const [factor, setFactor] = useState("2 veces más lento");
  const [error, setError] = useState<string | null>(null);

  async function cargar() {
    try {
      setIncidentes(await api.get<Incidente[]>("/api/rutas/incidentes"));
    } catch (err) {
      setError(mensajeDeError(err, "No se pudieron cargar los incidentes de tráfico"));
    }
  }

  useEffect(() => {
    void cargar();
  }, []);

  async function registrar() {
    setError(null);
    try {
      await api.post("/api/rutas/incidentes", { calle, factor: FACTORES[factor] });
      notificar(`Incidente registrado en ${calle}: se aplicará en la próxima re-optimización`, "exito");
      await cargar();
    } catch (err) {
      const mensaje = mensajeDeError(err, "No se pudo registrar el incidente");
      setError(mensaje);
      notificar(mensaje, "error");
    }
  }

  async function resolver(i: Incidente) {
    setError(null);
    try {
      await api.delete(`/api/rutas/incidentes/${i.incidente_id}`);
      notificar(`Incidente de ${i.calle} resuelto`, "exito");
      await cargar();
    } catch (err) {
      const mensaje = mensajeDeError(err, "No se pudo resolver el incidente");
      setError(mensaje);
      notificar(mensaje, "error");
    }
  }

  return (
    <section
      aria-labelledby="incidentes-titulo"
      style={{ borderRadius: 14, border: "1px solid var(--rz-panel-border)", background: "var(--rz-panel-bg)", padding: 16, display: "flex", flexDirection: "column", gap: 12 }}
    >
      <h2 id="incidentes-titulo" style={{ margin: 0, fontSize: 15, fontFamily: "var(--rz-font-display)" }}>
        Incidentes de tráfico
        <Ayuda texto="Una vía congestionada hace más lento el tiempo de viaje por ella. Al re-optimizar, las rutas en curso la rodean si conviene. Solo se pueden reportar Av. Ferrocarril, Av. Giráldez y Calle Real." />
      </h2>
      {error && <div style={estiloAviso}>{error}</div>}

      {esAdministrador && (
        <div style={{ display: "flex", alignItems: "flex-end", gap: 10, flexWrap: "wrap" }}>
          <CampoSelect etiqueta="Vía" valor={calle} opciones={CALLES} onCambio={setCalle} />
          <CampoSelect etiqueta="Congestión" valor={factor} opciones={Object.keys(FACTORES)} onCambio={setFactor} />
          <button type="button" onClick={() => void registrar()} style={estiloBotonPrimario}>
            Registrar incidente
          </button>
        </div>
      )}

      {incidentes.length === 0 ? (
        <div style={{ fontSize: 13, color: "var(--rz-text-muted)" }}>No hay incidentes de tráfico activos.</div>
      ) : (
        <ul style={{ margin: 0, padding: 0, listStyle: "none", display: "flex", flexDirection: "column", gap: 8 }}>
          {incidentes.map((i) => (
            <li key={i.incidente_id} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 10, flexWrap: "wrap", fontSize: 13 }}>
              <span>
                <strong>{i.calle}</strong> · {i.factor} veces más lento
                {i.descripcion && <span style={{ color: "var(--rz-text-muted)" }}> · {i.descripcion}</span>}
              </span>
              {esAdministrador && (
                <button
                  type="button"
                  onClick={() => void resolver(i)}
                  aria-label={`Resolver incidente de ${i.calle}`}
                  style={{ height: 32, padding: "0 12px", borderRadius: 10, border: "1px solid var(--rz-panel-border)", background: "transparent", color: "var(--rz-text)", fontSize: 12.5, cursor: "pointer" }}
                >
                  Resolver
                </button>
              )}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
