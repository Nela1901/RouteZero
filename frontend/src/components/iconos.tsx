/**
 * Íconos de trazo para las acciones de las tablas (ver, editar, eliminar, cerrar).
 * Son SVG en línea con `currentColor`: toman el color del botón que los contiene y no
 * necesitan una librería externa. Son decorativos (`aria-hidden`); el nombre accesible
 * lo da el botón.
 */

function Trazo({ children }: { children: React.ReactNode }) {
  return (
    <svg
      width="17"
      height="17"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      focusable="false"
    >
      {children}
    </svg>
  );
}

export function IconoVer() {
  return (
    <Trazo>
      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
      <circle cx="12" cy="12" r="3" />
    </Trazo>
  );
}

export function IconoEditar() {
  return (
    <Trazo>
      <path d="M12 20h9" />
      <path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4 12.5-12.5z" />
    </Trazo>
  );
}

export function IconoEliminar() {
  return (
    <Trazo>
      <polyline points="3 6 5 6 21 6" />
      <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6" />
      <path d="M10 11v6" />
      <path d="M14 11v6" />
      <path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2" />
    </Trazo>
  );
}

export function IconoCerrar() {
  return (
    <Trazo>
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </Trazo>
  );
}
