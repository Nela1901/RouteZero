import { useEffect, useState } from "react";
import { bytesTransferidos, emisionG, energiaKwh } from "./huellaDigital";
import { Ayuda } from "./ui";

/** Emisión de la visita promedio calculada en el informe de reducción del impacto ambiental (147.75 KB, 75 % desde celular). */
const REFERENCIA_VISITA_MG = 16.9;

const formato = (valor: number, decimales: number) =>
  valor.toLocaleString("es-PE", { minimumFractionDigits: decimales, maximumFractionDigits: decimales });

/**
 * Huella de carbono de los datos que el navegador descargó desde que se abrió RouteZero, estimada con el modelo SWDM v4.
 * Es la huella de la plataforma misma, distinta de las emisiones de las rutas que muestra el resto de la pantalla.
 */
export function TarjetaHuellaDigital() {
  const [bytes, setBytes] = useState(bytesTransferidos);

  useEffect(() => {
    const id = window.setInterval(() => setBytes(bytesTransferidos()), 5000);
    return () => window.clearInterval(id);
  }, []);

  return (
    <section
      aria-labelledby="sost-huella-digital"
      style={{ background: "var(--rz-panel-bg)", border: "1px solid var(--rz-panel-border)", borderRadius: 14, padding: "16px 18px" }}
    >
      <h2 id="sost-huella-digital" style={{ fontFamily: "var(--rz-font-display)", fontSize: 15, margin: "0 0 12px" }}>
        Huella digital de esta sesión
        <Ayuda
          texto="Estimación con el modelo SWDM v4 de los datos que el navegador descargó desde que abriste RouteZero: los archivos de la aplicación y las respuestas de la API (lo que ya estaba en la caché del navegador no cuenta). Usa 0.300 kWh por GB (0.194 de uso más 0.106 de fabricación del hardware) y 494 g de CO₂e por kWh. No incluye el cómputo del servidor ni del motor de rutas."
        />
      </h2>
      <dl style={{ margin: 0, display: "grid", gridTemplateColumns: "1fr auto", gap: "8px 16px", fontSize: 13.5 }}>
        <dt style={{ color: "var(--rz-text-muted)" }}>Datos descargados</dt>
        <dd style={{ margin: 0, fontFamily: "var(--rz-font-mono)" }}>{formato(bytes / 1024, 1)} KB</dd>
        <dt style={{ color: "var(--rz-text-muted)" }}>Energía estimada</dt>
        <dd style={{ margin: 0, fontFamily: "var(--rz-font-mono)" }}>{formato(energiaKwh(bytes) * 1000, 3)} Wh</dd>
        <dt style={{ color: "var(--rz-text-muted)" }}>Emisión estimada</dt>
        <dd style={{ margin: 0, fontFamily: "var(--rz-font-mono)", color: "var(--rz-accent)" }}>{formato(emisionG(bytes) * 1000, 1)} mg CO₂e</dd>
        <dt style={{ color: "var(--rz-text-muted)" }}>Visita promedio (informe de impacto ambiental)</dt>
        <dd style={{ margin: 0, fontFamily: "var(--rz-font-mono)" }}>{formato(REFERENCIA_VISITA_MG, 1)} mg CO₂e</dd>
      </dl>
    </section>
  );
}
