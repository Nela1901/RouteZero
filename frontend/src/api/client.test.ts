import { describe, expect, it } from "vitest";
import { ErrorApi, mensajeDeError } from "./client";

describe("mensajeDeError", () => {
  it("usa el mensaje de texto que devuelve la API", () => {
    expect(mensajeDeError(new ErrorApi(409, "El cliente tiene pedidos"), "por defecto")).toBe("El cliente tiene pedidos");
  });

  it("junta los errores de validación indicando el campo de cada uno", () => {
    const detalle = [
      { loc: ["body", "peso_kg"], msg: "debe ser mayor que 0" },
      { loc: ["body", "latitud"], msg: "fuera de la zona de cobertura" },
    ];
    expect(mensajeDeError(new ErrorApi(422, detalle), "por defecto")).toBe(
      "Datos inválidos — peso_kg: debe ser mayor que 0; latitud: fuera de la zona de cobertura",
    );
  });

  it("si un error de validación no trae campo ni mensaje usa un texto genérico", () => {
    expect(mensajeDeError(new ErrorApi(422, [{}]), "por defecto")).toBe("Datos inválidos — valor inválido");
  });

  it("si el detalle no es texto ni lista usa el mensaje por defecto", () => {
    expect(mensajeDeError(new ErrorApi(500, { otro: true }), "No se pudo guardar")).toBe("No se pudo guardar");
  });

  it("si no es un error de la API usa el mensaje por defecto", () => {
    expect(mensajeDeError(new Error("sin red"), "No se pudo guardar")).toBe("No se pudo guardar");
  });
});
