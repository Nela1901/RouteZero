import { describe, expect, it } from "vitest";
import { render, screen, within } from "@testing-library/react";
import { AyudaContenido, TextoConNegrita } from "./AyudaContenido";
import { GUIAS, LEYENDA_MAPA, PREGUNTAS } from "./contenidoAyuda";

describe("TextoConNegrita", () => {
  it("pone en negrita lo que va entre dobles asteriscos y deja el resto igual", () => {
    render(<p data-testid="p"><TextoConNegrita texto="Pulsa **Generar rutas** y espera." /></p>);
    const p = screen.getByTestId("p");
    expect(p).toHaveTextContent("Pulsa Generar rutas y espera.");
    expect(within(p).getByText("Generar rutas").tagName).toBe("STRONG");
  });
});

describe("AyudaContenido: guía por rol", () => {
  it("el administrador ve sus primeros pasos, el mapa, la verificación y las preguntas de su rol", () => {
    render(<AyudaContenido rol="ADMINISTRADOR" />);

    expect(screen.getByRole("heading", { name: "Primeros pasos como administrador", level: 2 })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Cómo leer el mapa", level: 2 })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Verificación en dos pasos", level: 2 })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Preguntas frecuentes", level: 2 })).toBeInTheDocument();

    expect(screen.getAllByRole("listitem").length).toBeGreaterThanOrEqual(GUIAS.ADMINISTRADOR.pasos.length);
    expect(screen.getByText("¿Cuánto tarda en generar las rutas?")).toBeInTheDocument();
    expect(screen.getByText("¿Cómo registro un incidente de tráfico?")).toBeInTheDocument();
  });

  it("el operador ve cómo cancelar pedidos y no las preguntas que solo son del administrador", () => {
    render(<AyudaContenido rol="OPERADOR" />);

    expect(screen.getByRole("heading", { name: "Primeros pasos como operador", level: 2 })).toBeInTheDocument();
    expect(screen.getByText(/Cancelar pedido/)).toBeInTheDocument();
    expect(screen.queryByText("¿Cuánto tarda en generar las rutas?")).not.toBeInTheDocument();
    expect(screen.queryByText("¿Cómo registro un incidente de tráfico?")).not.toBeInTheDocument();
    expect(screen.getByText("¿Qué puede ver cada rol?")).toBeInTheDocument();
  });

  it("el conductor ve su guía y sus preguntas, sin la sección del mapa del panel", () => {
    render(<AyudaContenido rol="CONDUCTOR" />);

    expect(screen.getByRole("heading", { name: "Primeros pasos como conductor", level: 2 })).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "Cómo leer el mapa" })).not.toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Cómo leer el mapa" })).not.toBeInTheDocument();
    expect(screen.getByText(/Cuenta sin vincular/)).toBeInTheDocument();
    expect(screen.getByText("¿Puedo deshacer una entrega que ya registré?")).toBeInTheDocument();
    expect(screen.queryByText("¿Qué puede ver cada rol?")).not.toBeInTheDocument();
  });

  it("el índice enlaza a cada sección que existe", () => {
    render(<AyudaContenido rol="ADMINISTRADOR" />);
    const indice = screen.getByRole("navigation", { name: "Contenido de la ayuda" });
    for (const enlace of within(indice).getAllByRole("link")) {
      const id = enlace.getAttribute("href")!.slice(1);
      expect(document.getElementById(id), `la sección ${id} debe existir`).not.toBeNull();
    }
  });

  it("explica la verificación en dos pasos con el nombre del botón real", () => {
    render(<AyudaContenido rol="OPERADOR" />);
    expect(screen.getByText(/Activar verificación en dos pasos/)).toBeInTheDocument();
    expect(screen.getByText(/código de 6 dígitos/)).toBeInTheDocument();
  });
});

describe("contenido de la ayuda", () => {
  it("cada rol tiene pasos y ninguna pregunta se repite", () => {
    for (const rol of ["ADMINISTRADOR", "OPERADOR", "CONDUCTOR"] as const) {
      expect(GUIAS[rol].pasos.length).toBeGreaterThan(0);
    }
    const textos = PREGUNTAS.map((p) => p.pregunta);
    expect(new Set(textos).size).toBe(textos.length);
    expect(PREGUNTAS.every((p) => p.roles.length > 0 && p.respuesta.length > 0)).toBe(true);
  });

  it("la guía de cómo leer el mapa cubre los estados de la leyenda", () => {
    const etiquetas = LEYENDA_MAPA.map((e) => e.etiqueta).join(" ");
    for (const clave of ["entregada", "fallida", "cancelada", "pendiente", "discontinua", "Congestión"]) {
      expect(etiquetas.toLowerCase()).toContain(clave.toLowerCase());
    }
  });
});
