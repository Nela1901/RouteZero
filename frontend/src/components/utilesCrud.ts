import type { CSSProperties } from "react";

/** Devuelve solo los campos que cambiaron respecto al valor inicial: a la API se envía lo que el usuario tocó. */
export function soloCambios<T extends Record<string, unknown>>(inicial: T, nuevo: T): Partial<T> {
  const cambios: Partial<T> = {};
  for (const clave of Object.keys(nuevo) as (keyof T)[]) {
    if (nuevo[clave] !== inicial[clave]) cambios[clave] = nuevo[clave];
  }
  return cambios;
}

export const estiloBotonSecundario: CSSProperties = {
  height: 38,
  padding: "0 14px",
  borderRadius: 10,
  border: "1px solid var(--rz-panel-border)",
  background: "transparent",
  color: "var(--rz-text)",
  fontSize: 12.5,
  cursor: "pointer",
};
