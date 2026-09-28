import { MapContainer, TileLayer } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { BotonTema } from "../../components/BotonTema";
import { useAuth } from "../../context/AuthContext";

const CENTRO_HUANCAYO: [number, number] = [-12.0653, -75.2049];
const OSM_TILES = "https://tile.openstreetmap.org/{z}/{x}/{y}.png";

export function ConductorPage() {
  const { usuario, cerrarSesion } = useAuth();

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh", background: "var(--rz-bg)", color: "var(--rz-text)" }}>
      <header
        style={{
          flexShrink: 0,
          display: "flex",
          alignItems: "center",
          gap: 10,
          padding: "16px",
          background: "var(--rz-header-bg)",
          borderBottom: "1px solid var(--rz-panel-border)",
        }}
      >
        <div style={{ display: "flex", flexDirection: "column", gap: 2, minWidth: 0 }}>
          <span style={{ fontFamily: "var(--rz-font-display)", fontWeight: 700, fontSize: 16 }}>
            Hola, {usuario?.email.split("@")[0]}
          </span>
          <span style={{ fontSize: 12, color: "var(--rz-text-muted)" }}>Vista de conductor</span>
        </div>
        <div style={{ flexGrow: 1 }} />
        <BotonTema />
      </header>

      <div
        style={{
          margin: 14,
          padding: "10px 14px",
          borderRadius: 12,
          background: "var(--rz-accent-3-soft-bg)",
          color: "var(--rz-accent-3)",
          fontSize: 12.5,
        }}
      >
        Vista previa: la asignación automática de rutas está en construcción. Estos datos son de ejemplo.
      </div>

      <div style={{ flexShrink: 0, height: 220, position: "relative" }}>
        <MapContainer center={CENTRO_HUANCAYO} zoom={14} style={{ height: "100%", width: "100%" }} zoomControl={false}>
          <TileLayer url={OSM_TILES} attribution="&copy; OpenStreetMap contributors" />
        </MapContainer>
      </div>

      <div style={{ flexGrow: 1, overflowY: "auto", padding: 18, display: "flex", flexDirection: "column", gap: 16 }}>
        <div
          style={{
            borderRadius: 20,
            background: "var(--rz-panel-bg)",
            border: "1px solid var(--rz-panel-border)",
            padding: 18,
            display: "flex",
            flexDirection: "column",
            gap: 12,
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <span
              style={{
                fontSize: 11,
                fontWeight: 700,
                textTransform: "uppercase",
                color: "var(--rz-accent)",
                background: "var(--rz-accent-soft-bg)",
                padding: "4px 10px",
                borderRadius: 999,
              }}
            >
              Express
            </span>
            <span style={{ fontFamily: "var(--rz-font-mono)", fontSize: 13, color: "var(--rz-text-muted)" }}>ETA —</span>
          </div>
          <div style={{ fontFamily: "var(--rz-font-display)", fontWeight: 700, fontSize: 19 }}>Sin parada asignada</div>
          <p style={{ margin: 0, fontSize: 13, color: "var(--rz-text-muted)" }}>
            Cuando el motor de optimización asigne tu ruta, tu próxima parada aparecerá aquí.
          </p>
        </div>
      </div>

      <nav
        aria-label="Navegación principal"
        style={{
          flexShrink: 0,
          display: "flex",
          background: "var(--rz-header-bg)",
          borderTop: "1px solid var(--rz-panel-border)",
          padding: "6px 4px",
        }}
      >
        <button type="button" onClick={() => void cerrarSesion()} style={estiloTab}>
          Cerrar sesión
        </button>
      </nav>
    </div>
  );
}

const estiloTab: React.CSSProperties = {
  flexGrow: 1,
  background: "none",
  border: "none",
  color: "var(--rz-text-muted)",
  fontSize: 13,
  padding: "10px 0",
  cursor: "pointer",
};
