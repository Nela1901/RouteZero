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

/**
 * Filtros de escritura: se aplican mientras el usuario teclea, así un carácter no permitido simplemente no aparece.
 * Son las mismas reglas que valida la API (backend/src/core/texto.py), que las vuelve a exigir.
 */

/** Nombre de una persona: solo letras (con tildes y ñ) y espacios. */
export const filtrarNombrePersona = (valor: string) => valor.replace(/[^\p{L} ]/gu, "");

/** Nombre de un negocio: letras, números y los signos de una razón social (. , - & ' ( )). */
export const filtrarNombreNegocio = (valor: string) => valor.replace(/[^\p{L}\p{N} .,\-&'()]/gu, "");

/** Descripciones y puntos de referencia: letras, números y puntuación básica (. , ; : - ( ) # / ° ¿ ? ¡ ! & '). */
export const filtrarTexto = (valor: string) => valor.replace(/[^\p{L}\p{N} .,;:\-()#/°¿?¡!&']/gu, "");

/** Placa: letras, números y guion, en mayúsculas. */
export const filtrarPlaca = (valor: string) => valor.toUpperCase().replace(/[^A-Z0-9-]/g, "");

/** Recorta los decimales que sobran según el paso del campo numérico (paso 0.01 admite 2 decimales; paso 1 ninguno). */
export function limitarDecimales(valor: string, paso?: string): string {
  if (!paso) return valor;
  const decimales = paso.includes(".") ? paso.split(".")[1].length : 0;
  const [entera, fraccion] = valor.split(".");
  if (decimales === 0) return entera;
  return fraccion !== undefined && fraccion.length > decimales ? `${entera}.${fraccion.slice(0, decimales)}` : valor;
}
