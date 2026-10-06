import { useTheme } from "../theme/ThemeContext";

export function BotonTema() {
  const { tema, alternarTema } = useTheme();
  const esOscuro = tema === "oscuro";

  return (
    <button
      type="button"
      onClick={alternarTema}
      aria-pressed={esOscuro}
      aria-label={esOscuro ? "Cambiar a tema claro" : "Cambiar a tema oscuro"}
      style={{
        width: 40,
        flexShrink: 0,
        height: 40,
        borderRadius: 10,
        border: "1px solid var(--rz-panel-border)",
        background: "var(--rz-panel-bg)",
        color: "var(--rz-text)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        cursor: "pointer",
      }}
    >
      {esOscuro ? (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="4" />
          <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
        </svg>
      ) : (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21 12.8A9 9 0 1111.2 3a7 7 0 009.8 9.8z" />
        </svg>
      )}
    </button>
  );
}
