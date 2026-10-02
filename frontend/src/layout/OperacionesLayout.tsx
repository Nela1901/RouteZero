import { useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useConfirm } from "../context/ConfirmContext";
import { BotonTema } from "../components/BotonTema";

const ITEMS_NAV = [
  { a: "/app/mapa", etiqueta: "Mapa", descripcion: "Rutas en vivo", icono: IconoMapa },
  { a: "/app/flota", etiqueta: "Flota", descripcion: "Vehículos", icono: IconoFlota },
  { a: "/app/pedidos", etiqueta: "Pedidos", descripcion: "Registro y estado", icono: IconoPedidos },
  { a: "/app/seguridad", etiqueta: "Seguridad", descripcion: "Verificación en 2 pasos", icono: IconoSeguridad },
];

const CLAVE_ALMACENAMIENTO = "routezero:sidebar-expandido";
const ANCHO_EXPANDIDO = 232;
const ANCHO_COLAPSADO = 84;

export function OperacionesLayout() {
  const { usuario, cerrarSesion } = useAuth();
  const { confirmar } = useConfirm();
  const [expandido, setExpandido] = useState(() => window.localStorage.getItem(CLAVE_ALMACENAMIENTO) !== "no");

  function alternarSidebar() {
    setExpandido((actual) => {
      const nuevo = !actual;
      window.localStorage.setItem(CLAVE_ALMACENAMIENTO, nuevo ? "si" : "no");
      return nuevo;
    });
  }

  return (
    <div style={{ display: "flex", height: "100vh", background: "var(--rz-bg)", color: "var(--rz-text)" }}>
      <nav
        aria-label="Navegación principal"
        style={{
          width: expandido ? ANCHO_EXPANDIDO : ANCHO_COLAPSADO,
          flexShrink: 0,
          background: "var(--rz-header-bg)",
          borderRight: "1px solid var(--rz-panel-border)",
          display: "flex",
          flexDirection: "column",
          padding: "20px 16px",
          gap: 24,
          transition: "width 0.18s ease",
          overflow: "hidden",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 10, minWidth: 0 }}>
          <div
            aria-hidden="true"
            style={{
              width: 40,
              height: 40,
              borderRadius: 11,
              background: "var(--rz-accent)",
              color: "var(--rz-bg)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontFamily: "var(--rz-font-display)",
              fontWeight: 700,
              fontSize: 15,
              flexShrink: 0,
            }}
          >
            R0
          </div>
          {expandido && (
            <div style={{ minWidth: 0 }}>
              <div style={{ fontFamily: "var(--rz-font-display)", fontWeight: 700, fontSize: 14, whiteSpace: "nowrap" }}>
                RouteZero
              </div>
              <div style={{ fontSize: 11, color: "var(--rz-text-muted)", whiteSpace: "nowrap" }}>Andina Reparto</div>
            </div>
          )}
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          {ITEMS_NAV.map(({ a, etiqueta, descripcion, icono: Icono }) => (
            <NavLink
              key={a}
              to={a}
              aria-label={etiqueta}
              title={!expandido ? etiqueta : undefined}
              style={({ isActive }) => ({
                display: "flex",
                alignItems: "center",
                gap: 12,
                padding: expandido ? "10px 12px" : "10px",
                justifyContent: expandido ? "flex-start" : "center",
                borderRadius: 12,
                color: isActive ? "var(--rz-accent)" : "var(--rz-text-muted)",
                background: isActive ? "var(--rz-accent-soft-bg)" : "transparent",
                minWidth: 0,
                textDecoration: "none",
              })}
            >
              <span style={{ flexShrink: 0, display: "flex" }}>
                <Icono />
              </span>
              {expandido && (
                <span style={{ minWidth: 0, overflow: "hidden" }}>
                  <div style={{ fontSize: 13.5, fontWeight: 600, color: "var(--rz-text)", whiteSpace: "nowrap" }}>{etiqueta}</div>
                  <div style={{ fontSize: 11, color: "var(--rz-text-muted)", whiteSpace: "nowrap" }}>{descripcion}</div>
                </span>
              )}
            </NavLink>
          ))}
        </div>

        <div style={{ flexGrow: 1 }} />

        <button
          type="button"
          onClick={alternarSidebar}
          aria-label={expandido ? "Contraer menú" : "Expandir menú"}
          style={{
            display: "flex",
            alignItems: "center",
            gap: 10,
            justifyContent: expandido ? "flex-start" : "center",
            padding: expandido ? "10px 12px" : "10px",
            borderRadius: 12,
            border: "1px solid var(--rz-panel-border)",
            background: "transparent",
            color: "var(--rz-text-muted)",
            cursor: "pointer",
            fontSize: 12.5,
          }}
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            style={{ flexShrink: 0, transform: expandido ? "rotate(180deg)" : "none", transition: "transform 0.18s ease" }}
          >
            <path d="M9 6l6 6-6 6" />
          </svg>
          {expandido && <span>Contraer menú</span>}
        </button>

        <button
          type="button"
          onClick={async () => {
            if (await confirmar({ titulo: "Cerrar sesión", mensaje: "¿Seguro que quieres cerrar tu sesión?", textoAceptar: "Cerrar sesión" })) {
              void cerrarSesion();
            }
          }}
          aria-label="Cerrar sesión"
          title={!expandido ? "Cerrar sesión" : undefined}
          style={{
            display: "flex",
            alignItems: "center",
            gap: 12,
            padding: expandido ? "10px 12px" : "10px",
            justifyContent: expandido ? "flex-start" : "center",
            borderRadius: 12,
            border: "none",
            background: "transparent",
            color: "var(--rz-text-muted)",
            cursor: "pointer",
          }}
        >
          <span style={{ flexShrink: 0, display: "flex" }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
              <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4" />
              <path d="M16 17l5-5-5-5M21 12H9" />
            </svg>
          </span>
          {expandido && <span style={{ fontSize: 13.5 }}>Cerrar sesión</span>}
        </button>

        <div style={{ display: "flex", alignItems: "center", gap: 10, minWidth: 0 }}>
          <div
            aria-hidden="true"
            title={usuario?.email}
            style={{
              width: 32,
              height: 32,
              borderRadius: "50%",
              background: "var(--rz-accent-soft-bg)",
              border: "1.5px solid var(--rz-accent)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontFamily: "var(--rz-font-display)",
              fontSize: 11.5,
              color: "var(--rz-accent)",
              flexShrink: 0,
            }}
          >
            {usuario?.email.slice(0, 2).toUpperCase()}
          </div>
          {expandido && (
            <span style={{ fontSize: 12, color: "var(--rz-text-muted)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
              {usuario?.email}
            </span>
          )}
        </div>
      </nav>

      <div style={{ flexGrow: 1, display: "flex", flexDirection: "column", minWidth: 0 }}>
        <header
          style={{
            height: 76,
            flexShrink: 0,
            display: "flex",
            alignItems: "center",
            padding: "0 28px",
            gap: 20,
            borderBottom: "1px solid var(--rz-panel-border)",
            background: "var(--rz-header-bg)",
          }}
        >
          <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
            <span style={{ fontFamily: "var(--rz-font-display)", fontWeight: 700, fontSize: 18 }}>
              Panel de operaciones
            </span>
            <span style={{ fontSize: 12.5, color: "var(--rz-text-muted)" }}>Andina Reparto S.A.C. · Huancayo</span>
          </div>

          <div style={{ flexGrow: 1 }} />

          <div
            role="status"
            aria-label="CO2 evitado hoy"
            style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
              padding: "10px 18px",
              borderRadius: 999,
              background: "var(--rz-accent-soft-bg)",
              border: "1px solid var(--rz-accent-soft-border)",
            }}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--rz-accent)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M11 20A7 7 0 019.8 6.1C15.5 5 17 3 17 3s.5 3.5 2 6c1.6 2.7 1.5 6-1 8-1 1-2.5 1-3.5 1" />
              <path d="M2 21c0-3.5 2.5-6 5-6" />
            </svg>
            <span style={{ fontFamily: "var(--rz-font-mono)", fontWeight: 600, fontSize: 15, color: "var(--rz-accent)" }}>
              — kg CO₂
            </span>
            <span style={{ fontSize: 12.5, color: "var(--rz-text-muted)" }}>evitados hoy</span>
          </div>

          <BotonTema />
        </header>

        <main style={{ flexGrow: 1, minHeight: 0, overflow: "auto" }}>
          <Outlet />
        </main>
      </div>
    </div>
  );
}

function IconoMapa() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9 20l-5.5 2V6L9 4m0 16l6 2m-6-2V4m6 18l5.5-2V4L15 6m0 16V6m0 0L9 4" />
    </svg>
  );
}

function IconoFlota() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 16V9a1 1 0 011-1h9l4 4h3a1 1 0 011 1v3a1 1 0 01-1 1h-1" />
      <circle cx="7.5" cy="17.5" r="2" />
      <circle cx="17.5" cy="17.5" r="2" />
      <path d="M9.5 17.5h6" />
    </svg>
  );
}

function IconoPedidos() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 7l8-4 8 4-8 4-8-4z" />
      <path d="M4 7v10l8 4 8-4V7" />
      <path d="M12 11v10" />
    </svg>
  );
}

function IconoSeguridad() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 3l7 3v6c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6l7-3z" />
    </svg>
  );
}
