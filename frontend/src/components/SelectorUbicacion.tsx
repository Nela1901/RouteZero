import { useEffect, useState } from "react";
import { MapContainer, Marker, TileLayer, useMap, useMapEvents } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { useToast } from "../context/ToastContext";

const LAT_MIN = -12.15;
const LAT_MAX = -11.95;
const LON_MIN = -75.3;
const LON_MAX = -75.1;
const CENTRO_HUANCAYO: [number, number] = [-12.0653, -75.2049];

const ICONO_PUNTO = L.divIcon({
  className: "",
  html:
    '<div style="width:18px;height:18px;border-radius:50%;background:#2fe0b8;' +
    'border:3px solid #0b1a16;box-shadow:0 0 0 3px rgba(47,224,184,0.3);"></div>',
  iconSize: [18, 18],
  iconAnchor: [9, 9],
});

interface ResultadoBusqueda {
  display_name: string;
  lat: string;
  lon: string;
}

interface Props {
  latitud: string;
  longitud: string;
  onCambio: (latitud: string, longitud: string) => void;
}

function dentroDeZona(lat: number, lon: number): boolean {
  return lat >= LAT_MIN && lat <= LAT_MAX && lon >= LON_MIN && lon <= LON_MAX;
}

export function SelectorUbicacion({ latitud, longitud, onCambio }: Props) {
  const { notificar } = useToast();
  const [busqueda, setBusqueda] = useState("");
  const [resultados, setResultados] = useState<ResultadoBusqueda[]>([]);
  const [buscando, setBuscando] = useState(false);

  const latNum = Number(latitud);
  const lonNum = Number(longitud);
  const posicion: [number, number] =
    Number.isFinite(latNum) && Number.isFinite(lonNum) ? [latNum, lonNum] : CENTRO_HUANCAYO;

  function aplicarPosicion(lat: number, lon: number, direccionConocida?: string) {
    if (!dentroDeZona(lat, lon)) {
      notificar("Ese punto queda fuera de la zona de cobertura de Huancayo", "error");
      return;
    }
    onCambio(lat.toFixed(6), lon.toFixed(6));
    if (direccionConocida !== undefined) {
      setBusqueda(direccionConocida);
    } else {
      void buscarDireccionDePunto(lat, lon);
    }
  }

  async function buscarDireccionDePunto(lat: number, lon: number) {
    setBusqueda("Buscando dirección…");
    try {
      const params = new URLSearchParams({ format: "json", lat: String(lat), lon: String(lon) });
      const respuesta = await fetch(`https://nominatim.openstreetmap.org/reverse?${params}`);
      const datos = await respuesta.json();
      setBusqueda(datos?.display_name ?? "");
    } catch {
      setBusqueda("");
    }
  }

  async function buscar() {
    if (!busqueda.trim()) return;
    setBuscando(true);
    setResultados([]);
    try {
      const params = new URLSearchParams({
        format: "json",
        q: `${busqueda}, Huancayo, Perú`,
        viewbox: `${LON_MIN},${LAT_MAX},${LON_MAX},${LAT_MIN}`,
        bounded: "1",
        limit: "5",
      });
      const respuesta = await fetch(`https://nominatim.openstreetmap.org/search?${params}`);
      const datos: ResultadoBusqueda[] = await respuesta.json();
      if (datos.length === 0) {
        notificar("No se encontraron direcciones para esa búsqueda dentro de Huancayo", "error");
      }
      setResultados(datos);
    } catch {
      notificar("No se pudo buscar la dirección, inténtalo de nuevo", "error");
    } finally {
      setBuscando(false);
    }
  }

  function elegirResultado(r: ResultadoBusqueda) {
    aplicarPosicion(Number(r.lat), Number(r.lon), r.display_name);
    setResultados([]);
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 8, gridColumn: "1 / -1" }}>
      <label style={estiloEtiqueta}>Ubicación (busca una dirección o ajusta el punto en el mapa)</label>
      <div style={{ display: "flex", gap: 6 }}>
        <input
          value={busqueda}
          onChange={(e) => setBusqueda(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              void buscar();
            }
          }}
          placeholder="Ej: Jirón Puno, Mercado Mayorista..."
          style={estiloInput}
        />
        <button type="button" onClick={() => void buscar()} disabled={buscando} style={estiloBotonSecundario}>
          {buscando ? "Buscando…" : "Buscar"}
        </button>
      </div>

      {resultados.length > 0 && (
        <div style={{ borderRadius: 10, border: "1px solid var(--rz-panel-border)", overflow: "hidden" }}>
          {resultados.map((r, i) => (
            <button key={i} type="button" onClick={() => elegirResultado(r)} style={estiloResultado}>
              {r.display_name}
            </button>
          ))}
        </div>
      )}

      <div style={{ height: 220, borderRadius: 12, overflow: "hidden", border: "1px solid var(--rz-panel-border)" }}>
        <MapContainer center={posicion} zoom={15} style={{ height: "100%", width: "100%" }}>
          <TileLayer url="https://tile.openstreetmap.org/{z}/{x}/{y}.png" attribution="&copy; OpenStreetMap contributors" />
          <Marker
            position={posicion}
            icon={ICONO_PUNTO}
            draggable
            eventHandlers={{
              dragend: (evento) => {
                const { lat, lng } = evento.target.getLatLng();
                aplicarPosicion(lat, lng);
              },
            }}
          />
          <ClicEnMapa onClic={aplicarPosicion} />
          <CentrarMapa posicion={posicion} />
        </MapContainer>
      </div>

      <p style={{ margin: 0, fontSize: 11.5, color: "var(--rz-text-muted)" }}>
        Lat: {latitud} · Lon: {longitud}
      </p>
    </div>
  );
}

function ClicEnMapa({ onClic }: { onClic: (lat: number, lon: number) => void }) {
  useMapEvents({
    click(evento) {
      onClic(evento.latlng.lat, evento.latlng.lng);
    },
  });
  return null;
}

function CentrarMapa({ posicion }: { posicion: [number, number] }) {
  const mapa = useMap();
  useEffect(() => {
    mapa.setView(posicion);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [posicion[0], posicion[1]]);
  return null;
}

const estiloEtiqueta: React.CSSProperties = {
  fontSize: 12.5,
  color: "var(--rz-text-muted)",
};

const estiloInput: React.CSSProperties = {
  flexGrow: 1,
  height: 38,
  borderRadius: 10,
  border: "1px solid var(--rz-panel-border)",
  background: "var(--rz-bg)",
  color: "var(--rz-text)",
  padding: "0 12px",
  fontSize: 13.5,
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
  flexShrink: 0,
};

const estiloResultado: React.CSSProperties = {
  display: "block",
  width: "100%",
  textAlign: "left",
  padding: "10px 12px",
  background: "var(--rz-panel-bg)",
  border: "none",
  borderTop: "1px solid var(--rz-panel-border)",
  color: "var(--rz-text)",
  fontSize: 12.5,
  cursor: "pointer",
};
