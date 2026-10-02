import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { api, ErrorApi, guardarTokens, limpiarTokens, obtenerAccessToken } from "../api/client";
import { useToast } from "./ToastContext";

export type RolNombre = "ADMINISTRADOR" | "OPERADOR" | "CONDUCTOR" | "GERENTE";

interface Usuario {
  usuarioId: string;
  email: string;
  rolNombre: RolNombre;
  mfaActivo: boolean;
}

interface MfaPendiente {
  mfaToken: string;
  factorId: string;
}

interface LoginResponse {
  estado: "ok" | "mfa_required";
  access_token: string | null;
  refresh_token: string | null;
  mfa_token: string | null;
  factor_id: string | null;
}

interface MeResponse {
  usuario_id: string;
  email: string;
  rol_id: string;
  rol_nombre: RolNombre;
  mfa_activo: boolean;
}

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

interface AuthContextValue {
  usuario: Usuario | null;
  cargando: boolean;
  mfaPendiente: MfaPendiente | null;
  iniciarSesion: (email: string, password: string) => Promise<void>;
  confirmarMfa: (codigo: string) => Promise<void>;
  cerrarSesion: () => Promise<void>;
  cancelarMfa: () => void;
  recargarUsuario: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const { notificar } = useToast();
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [cargando, setCargando] = useState(true);
  const [mfaPendiente, setMfaPendiente] = useState<MfaPendiente | null>(null);

  async function cargarUsuarioActual() {
    try {
      const datos = await api.get<MeResponse>("/api/auth/me");
      setUsuario({
        usuarioId: datos.usuario_id,
        email: datos.email,
        rolNombre: datos.rol_nombre,
        mfaActivo: datos.mfa_activo,
      });
    } catch {
      limpiarTokens();
      setUsuario(null);
    } finally {
      setCargando(false);
    }
  }

  useEffect(() => {
    if (obtenerAccessToken()) {
      void cargarUsuarioActual();
    } else {
      setCargando(false);
    }
  }, []);

  async function iniciarSesion(email: string, password: string) {
    const respuesta = await api.post<LoginResponse>("/api/auth/login", { email, password });

    if (respuesta.estado === "mfa_required") {
      setMfaPendiente({ mfaToken: respuesta.mfa_token!, factorId: respuesta.factor_id! });
      return;
    }

    guardarTokens(respuesta.access_token!, respuesta.refresh_token!);
    await cargarUsuarioActual();
  }

  async function confirmarMfa(codigo: string) {
    if (!mfaPendiente) return;

    const respuesta = await fetch(`${BASE_URL}/api/auth/login/mfa`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${mfaPendiente.mfaToken}`,
      },
      body: JSON.stringify({ factor_id: mfaPendiente.factorId, codigo }),
    });

    if (!respuesta.ok) {
      const cuerpo = await respuesta.json().catch(() => null);
      throw new ErrorApi(respuesta.status, cuerpo?.detail ?? "Código incorrecto");
    }

    const datos: LoginResponse = await respuesta.json();
    guardarTokens(datos.access_token!, datos.refresh_token!);
    setMfaPendiente(null);
    await cargarUsuarioActual();
  }

  function cancelarMfa() {
    setMfaPendiente(null);
  }

  async function cerrarSesion() {
    notificar("Cerrando sesión…", "info");
    try {
      await api.delete("/api/auth/sesiones");
    } catch {
      // La sesión igual se limpia localmente aunque la llamada falle.
    }
    limpiarTokens();
    setUsuario(null);
  }

  const valor = useMemo<AuthContextValue>(
    () => ({
      usuario,
      cargando,
      mfaPendiente,
      iniciarSesion,
      confirmarMfa,
      cerrarSesion,
      cancelarMfa,
      recargarUsuario: cargarUsuarioActual,
    }),
    [usuario, cargando, mfaPendiente],
  );

  return <AuthContext.Provider value={valor}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const contexto = useContext(AuthContext);
  if (!contexto) {
    throw new Error("useAuth debe usarse dentro de AuthProvider");
  }
  return contexto;
}
