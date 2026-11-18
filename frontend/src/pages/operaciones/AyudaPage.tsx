import { AyudaContenido } from "../../components/AyudaContenido";
import { useAuth } from "../../context/AuthContext";

/** Ayuda del panel de operaciones: primeros pasos, cómo leer el mapa, verificación en dos pasos y preguntas frecuentes. */
export function AyudaPage() {
  const { usuario } = useAuth();
  const rol = usuario?.rolNombre === "ADMINISTRADOR" ? "ADMINISTRADOR" : "OPERADOR";

  return (
    <div style={{ padding: 28, display: "flex", flexDirection: "column", gap: 20, maxWidth: 880 }}>
      <div>
        <h1 style={{ fontFamily: "var(--rz-font-display)", fontSize: 22, margin: "0 0 4px" }}>Ayuda y primeros pasos</h1>
        <p style={{ margin: 0, fontSize: 13, color: "var(--rz-text-muted)" }}>
          Qué hacer primero, cómo leer el mapa y respuestas a las dudas más comunes, según tu rol.
        </p>
      </div>
      <AyudaContenido rol={rol} />
    </div>
  );
}
