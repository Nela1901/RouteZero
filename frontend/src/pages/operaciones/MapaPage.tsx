import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { useEffect, useState } from "react";
import { api } from "../../api/client";

const CENTRO_HUANCAYO: [number, number] = [-12.0653, -75.2049];
const OSM_TILES = "https://tile.openstreetmap.org/{z}/{x}/{y}.png";

const COLOR_PRIORIDAD: Record<string, string> = {
  EXPRESS: "var(--rz-accent)",
  ESTANDAR: "var(--rz-accent-2)",
  ECONOMICO: "var(--rz-accent-3)",
};

interface Pedido {
  pedido_id: string;
  prioridad: string;
  estado: string;
  latitud: number;
  longitud: number;
  descripcion: string | null;
}

export function MapaPage() {
  const [pedidos, setPedidos] = useState<Pedido[]>([]);

  useEffect(() => {
    api
      .get<Pedido[]>("/api/pedidos")
      .then(setPedidos)
      .catch(() => setPedidos([]));
  }, []);

  return (
    <div style={{ position: "relative", height: "100%" }}>
      <MapContainer center={CENTRO_HUANCAYO} zoom={14} style={{ height: "100%", width: "100%" }}>
        <TileLayer url={OSM_TILES} attribution="&copy; OpenStreetMap contributors" />
        {pedidos.map((pedido) => (
          <CircleMarker
            key={pedido.pedido_id}
            center={[Number(pedido.latitud), Number(pedido.longitud)]}
            radius={7}
            pathOptions={{
              color: COLOR_PRIORIDAD[pedido.prioridad] ?? "var(--rz-accent-2)",
              fillColor: COLOR_PRIORIDAD[pedido.prioridad] ?? "var(--rz-accent-2)",
              fillOpacity: 0.85,
            }}
          >
            <Popup>
              <strong>{pedido.descripcion ?? "Pedido"}</strong>
              <br />
              Prioridad: {pedido.prioridad} · Estado: {pedido.estado}
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>

      <div
        style={{
          position: "absolute",
          right: 24,
          bottom: 24,
          display: "flex",
          gap: 16,
          padding: "10px 16px",
          borderRadius: 12,
          background: "var(--rz-panel-solid-bg)",
          backdropFilter: "blur(10px)",
          border: "1px solid var(--rz-panel-border)",
          zIndex: 1000,
        }}
      >
        <Leyenda color="var(--rz-accent)" etiqueta="Express" />
        <Leyenda color="var(--rz-accent-2)" etiqueta="Estándar" />
        <Leyenda color="var(--rz-accent-3)" etiqueta="Económico" />
      </div>

      {pedidos.length === 0 && (
        <div
          style={{
            position: "absolute",
            left: 24,
            top: 20,
            padding: "10px 16px",
            borderRadius: 12,
            background: "var(--rz-panel-solid-bg)",
            border: "1px solid var(--rz-panel-border)",
            fontSize: 13,
            color: "var(--rz-text-muted)",
            zIndex: 1000,
          }}
        >
          Aún no hay pedidos pendientes de ubicar en el mapa.
        </div>
      )}
    </div>
  );
}

function Leyenda({ color, etiqueta }: { color: string; etiqueta: string }) {
  return (
    <span style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 12, color: "var(--rz-text-muted)" }}>
      <span aria-hidden="true" style={{ width: 8, height: 8, borderRadius: "50%", background: color }} />
      {etiqueta}
    </span>
  );
}
