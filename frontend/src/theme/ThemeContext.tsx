import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

type Tema = "oscuro" | "claro";

interface ThemeContextValue {
  tema: Tema;
  alternarTema: () => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

const CLAVE_ALMACENAMIENTO = "routezero:tema";

function leerTemaGuardado(): Tema {
  const guardado = window.localStorage.getItem(CLAVE_ALMACENAMIENTO);
  return guardado === "claro" ? "claro" : "oscuro";
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [tema, setTema] = useState<Tema>(leerTemaGuardado);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", tema === "claro" ? "light" : "dark");
    window.localStorage.setItem(CLAVE_ALMACENAMIENTO, tema);
  }, [tema]);

  const valor = useMemo<ThemeContextValue>(
    () => ({
      tema,
      alternarTema: () => setTema((actual) => (actual === "oscuro" ? "claro" : "oscuro")),
    }),
    [tema],
  );

  return <ThemeContext.Provider value={valor}>{children}</ThemeContext.Provider>;
}

export function useTheme(): ThemeContextValue {
  const contexto = useContext(ThemeContext);
  if (!contexto) {
    throw new Error("useTheme debe usarse dentro de ThemeProvider");
  }
  return contexto;
}
