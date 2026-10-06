const BASE_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

const CLAVE_ACCESS = "routezero:access_token";
const CLAVE_REFRESH = "routezero:refresh_token";

export function guardarTokens(accessToken: string, refreshToken: string) {
  window.localStorage.setItem(CLAVE_ACCESS, accessToken);
  window.localStorage.setItem(CLAVE_REFRESH, refreshToken);
}

export function limpiarTokens() {
  window.localStorage.removeItem(CLAVE_ACCESS);
  window.localStorage.removeItem(CLAVE_REFRESH);
}

export function obtenerAccessToken(): string | null {
  return window.localStorage.getItem(CLAVE_ACCESS);
}

function obtenerRefreshToken(): string | null {
  return window.localStorage.getItem(CLAVE_REFRESH);
}

export class ErrorApi extends Error {
  status: number;
  detalle: unknown;

  constructor(status: number, detalle: unknown) {
    super(typeof detalle === "string" ? detalle : "Error de la API");
    this.status = status;
    this.detalle = detalle;
  }
}

/** Convierte el `detail` de la API en un texto legible; FastAPI devuelve una lista de objetos en los 422. */
export function mensajeDeError(err: unknown, porDefecto: string): string {
  if (!(err instanceof ErrorApi)) return porDefecto;
  if (typeof err.detalle === "string") return err.detalle;
  if (Array.isArray(err.detalle)) {
    const partes = err.detalle.map((e: { loc?: unknown[]; msg?: string }) => {
      const campo = Array.isArray(e.loc) ? String(e.loc[e.loc.length - 1]) : "";
      return campo ? `${campo}: ${e.msg ?? "valor inválido"}` : (e.msg ?? "valor inválido");
    });
    return `Datos inválidos — ${partes.join("; ")}`;
  }
  return porDefecto;
}

async function solicitud<T>(ruta: string, opciones: RequestInit = {}, reintentar = true): Promise<T> {
  const accessToken = obtenerAccessToken();
  const cabeceras = new Headers(opciones.headers);
  cabeceras.set("Content-Type", "application/json");
  if (accessToken) {
    cabeceras.set("Authorization", `Bearer ${accessToken}`);
  }

  const respuesta = await fetch(`${BASE_URL}${ruta}`, { ...opciones, headers: cabeceras });

  if (respuesta.status === 401 && reintentar && obtenerRefreshToken()) {
    const renovada = await intentarRenovarSesion();
    if (renovada) {
      return solicitud<T>(ruta, opciones, false);
    }
  }

  if (!respuesta.ok) {
    const cuerpo = await respuesta.json().catch(() => null);
    throw new ErrorApi(respuesta.status, cuerpo?.detail ?? cuerpo);
  }

  if (respuesta.status === 204) {
    return undefined as T;
  }
  return (await respuesta.json()) as T;
}

async function intentarRenovarSesion(): Promise<boolean> {
  const accessToken = obtenerAccessToken();
  const refreshToken = obtenerRefreshToken();
  if (!accessToken || !refreshToken) return false;

  const respuesta = await fetch(`${BASE_URL}/api/auth/sesiones/renovar`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ access_token: accessToken, refresh_token: refreshToken }),
  });

  if (!respuesta.ok) {
    limpiarTokens();
    return false;
  }

  const datos = await respuesta.json();
  guardarTokens(datos.access_token, datos.refresh_token);
  return true;
}

export const api = {
  get: <T>(ruta: string) => solicitud<T>(ruta, { method: "GET" }),
  post: <T>(ruta: string, cuerpo?: unknown, opciones: RequestInit = {}) =>
    solicitud<T>(ruta, { ...opciones, method: "POST", body: cuerpo ? JSON.stringify(cuerpo) : undefined }),
  put: <T>(ruta: string, cuerpo?: unknown) =>
    solicitud<T>(ruta, { method: "PUT", body: cuerpo ? JSON.stringify(cuerpo) : undefined }),
  delete: <T>(ruta: string) => solicitud<T>(ruta, { method: "DELETE" }),
};
