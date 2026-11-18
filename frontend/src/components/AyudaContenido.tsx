import { Fragment, type CSSProperties, type ReactNode } from "react";
import { ETIQUETA_ROL, GUIAS, LEYENDA_MAPA, PREGUNTAS, TEXTO_VERIFICACION, type RolAyuda } from "./contenidoAyuda";

/** Convierte los fragmentos entre **dobles asteriscos** en negrita. */
export function TextoConNegrita({ texto }: Readonly<{ texto: string }>) {
  return (
    <>
      {texto.split("**").map((trozo, i) =>
        i % 2 === 1 ? <strong key={`${i}-${trozo}`}>{trozo}</strong> : <Fragment key={`${i}-${trozo}`}>{trozo}</Fragment>,
      )}
    </>
  );
}

const estiloPanel: CSSProperties = {
  background: "var(--rz-panel-bg)",
  border: "1px solid var(--rz-panel-border)",
  borderRadius: 14,
  padding: 16,
};
const estiloTitulo: CSSProperties = { fontFamily: "var(--rz-font-display)", fontSize: 17, margin: "0 0 10px" };
const estiloTexto: CSSProperties = { margin: 0, fontSize: 14, lineHeight: 1.6, color: "var(--rz-text)" };

function Seccion({ id, titulo, children }: Readonly<{ id: string; titulo: string; children: ReactNode }>) {
  return (
    <section id={id} aria-labelledby={`${id}-titulo`} style={{ ...estiloPanel, scrollMarginTop: 12 }}>
      <h2 id={`${id}-titulo`} style={estiloTitulo}>
        {titulo}
      </h2>
      {children}
    </section>
  );
}

/**
 * Guía de primeros pasos, cómo leer el mapa, verificación en dos pasos y preguntas frecuentes, adaptada al rol. Lo usan la pantalla
 * Ayuda del panel de operaciones (administrador y operador) y la vista del conductor. No lleva título principal: lo pone quien la usa.
 */
export function AyudaContenido({ rol }: Readonly<{ rol: RolAyuda }>) {
  const guia = GUIAS[rol];
  const preguntas = PREGUNTAS.filter((p) => p.roles.includes(rol));
  const conMapa = rol !== "CONDUCTOR";

  const enlaces = [
    { href: "#ayuda-primeros-pasos", texto: "Primeros pasos" },
    ...(conMapa ? [{ href: "#ayuda-mapa", texto: "Cómo leer el mapa" }] : []),
    { href: "#ayuda-verificacion", texto: "Verificación en dos pasos" },
    { href: "#ayuda-preguntas", texto: "Preguntas frecuentes" },
  ];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <nav aria-label="Contenido de la ayuda" style={{ display: "flex", flexWrap: "wrap", gap: "6px 8px" }}>
        {enlaces.map((e) => (
          <a
            key={e.href}
            href={e.href}
            style={{
              padding: "6px 12px",
              borderRadius: 999,
              border: "1px solid var(--rz-panel-border)",
              color: "var(--rz-text)",
              fontSize: 13,
              textDecoration: "none",
            }}
          >
            {e.texto}
          </a>
        ))}
      </nav>

      <Seccion id="ayuda-primeros-pasos" titulo={`Primeros pasos como ${ETIQUETA_ROL[rol]}`}>
        <p style={{ ...estiloTexto, marginBottom: 10 }}>{guia.introduccion}</p>
        <ol style={{ ...estiloTexto, margin: 0, paddingLeft: 22, display: "flex", flexDirection: "column", gap: 8 }}>
          {guia.pasos.map((paso) => (
            <li key={paso}>
              <TextoConNegrita texto={paso} />
            </li>
          ))}
        </ol>
      </Seccion>

      {conMapa && (
        <Seccion id="ayuda-mapa" titulo="Cómo leer el mapa">
          <ul style={{ ...estiloTexto, margin: 0, paddingLeft: 20, display: "flex", flexDirection: "column", gap: 6 }}>
            {LEYENDA_MAPA.map((e) => (
              <li key={e.etiqueta}>
                <strong>{e.etiqueta}:</strong> {e.detalle}
              </li>
            ))}
          </ul>
        </Seccion>
      )}

      <Seccion id="ayuda-verificacion" titulo="Verificación en dos pasos">
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {TEXTO_VERIFICACION.map((parrafo) => (
            <p key={parrafo} style={estiloTexto}>
              <TextoConNegrita texto={parrafo} />
            </p>
          ))}
        </div>
      </Seccion>

      <Seccion id="ayuda-preguntas" titulo="Preguntas frecuentes">
        <div style={{ display: "flex", flexDirection: "column" }}>
          {preguntas.map((p) => (
            <details key={p.pregunta} style={{ borderTop: "1px solid var(--rz-panel-border)", padding: "2px 0" }}>
              <summary style={{ cursor: "pointer", fontSize: 14, fontWeight: 600, padding: "10px 0", lineHeight: 1.4 }}>{p.pregunta}</summary>
              <p style={{ ...estiloTexto, padding: "0 0 12px" }}>
                <TextoConNegrita texto={p.respuesta} />
              </p>
            </details>
          ))}
        </div>
      </Seccion>
    </div>
  );
}
