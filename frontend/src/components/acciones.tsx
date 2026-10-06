import { useEffect, useId, type ReactNode } from "react";
import { IconoCerrar, IconoEditar, IconoEliminar, IconoVer } from "./iconos";

/** Piezas compartidas por los CRUD: botones de acción por fila, ventana modal y fila de detalle. */

const estiloBotonIcono: React.CSSProperties = {
  width: 34,
  height: 34,
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  borderRadius: 9,
  border: "1px solid var(--rz-panel-border)",
  background: "transparent",
  color: "var(--rz-text-muted)",
  cursor: "pointer",
  padding: 0,
  flexShrink: 0,
};

function BotonIcono(props: { etiqueta: string; onClick: () => void; peligro?: boolean; children: ReactNode }) {
  return (
    <button
      type="button"
      title={props.etiqueta}
      aria-label={props.etiqueta}
      onClick={(e) => {
        e.stopPropagation();
        props.onClick();
      }}
      style={{ ...estiloBotonIcono, color: props.peligro ? "var(--rz-danger)" : "var(--rz-text-muted)" }}
    >
      {props.children}
    </button>
  );
}

/**
 * Ver detalle, editar y eliminar de un registro. `nombre` identifica la fila en el nombre
 * accesible de cada botón (por ejemplo "Editar Bodega San José"). Una acción sin manejador no se muestra.
 */
export function AccionesFila(props: {
  nombre: string;
  onVer?: () => void;
  onEditar?: () => void;
  onEliminar?: () => void;
  textoEliminar?: string;
}) {
  return (
    <div style={{ display: "inline-flex", gap: 6 }}>
      {props.onVer && (
        <BotonIcono etiqueta={`Ver detalle de ${props.nombre}`} onClick={props.onVer}>
          <IconoVer />
        </BotonIcono>
      )}
      {props.onEditar && (
        <BotonIcono etiqueta={`Editar ${props.nombre}`} onClick={props.onEditar}>
          <IconoEditar />
        </BotonIcono>
      )}
      {props.onEliminar && (
        <BotonIcono etiqueta={`${props.textoEliminar ?? "Eliminar"} ${props.nombre}`} onClick={props.onEliminar} peligro>
          <IconoEliminar />
        </BotonIcono>
      )}
    </div>
  );
}

/** Ventana modal accesible: se cierra con Escape, con el fondo o con el botón de cierre. */
export function Modal(props: { titulo: string; onCerrar: () => void; ancho?: number; children: ReactNode }) {
  const idTitulo = useId();
  const { onCerrar } = props;

  useEffect(() => {
    function alTeclear(e: KeyboardEvent) {
      if (e.key === "Escape") onCerrar();
    }
    document.addEventListener("keydown", alTeclear);
    return () => document.removeEventListener("keydown", alTeclear);
  }, [onCerrar]);

  return (
    <div
      role="presentation"
      onClick={onCerrar}
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(10, 13, 14, 0.55)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 1500,
        padding: 16,
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby={idTitulo}
        onClick={(e) => e.stopPropagation()}
        style={{
          width: "100%",
          maxWidth: props.ancho ?? 480,
          maxHeight: "calc(100dvh - 32px)",
          overflowY: "auto",
          borderRadius: 18,
          background: "var(--rz-panel-solid-bg)",
          border: "1px solid var(--rz-panel-border)",
          boxShadow: "0 24px 60px rgba(0, 0, 0, 0.35)",
          padding: 22,
          display: "flex",
          flexDirection: "column",
          gap: 14,
        }}
      >
        <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 12 }}>
          <h2 id={idTitulo} style={{ fontFamily: "var(--rz-font-display)", fontSize: 17, margin: 0, minWidth: 0 }}>
            {props.titulo}
          </h2>
          <button
            type="button"
            onClick={onCerrar}
            title="Cerrar"
            aria-label="Cerrar"
            style={{ ...estiloBotonIcono, width: 30, height: 30 }}
          >
            <IconoCerrar />
          </button>
        </div>
        {props.children}
      </div>
    </div>
  );
}

export function FilaDetalle({ etiqueta, valor }: { etiqueta: string; valor: ReactNode }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", gap: 16, fontSize: 13 }}>
      <span style={{ color: "var(--rz-text-muted)" }}>{etiqueta}</span>
      <span style={{ fontWeight: 600, textAlign: "right", minWidth: 0, overflowWrap: "anywhere" }}>{valor}</span>
    </div>
  );
}
