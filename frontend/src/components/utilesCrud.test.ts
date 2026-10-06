import { describe, expect, it } from "vitest";
import {
  filtrarNombreNegocio,
  filtrarNombrePersona,
  filtrarPlaca,
  filtrarTexto,
  limitarDecimales,
  soloCambios,
} from "./utilesCrud";

describe("filtros de escritura", () => {
  it("el nombre de una persona solo conserva letras y espacios", () => {
    expect(filtrarNombrePersona("Sara Hernán Cañari")).toBe("Sara Hernán Cañari");
    expect(filtrarNombrePersona("Sara 123 <b>Caso</b>_@")).toBe("Sara  bCasob");
    expect(filtrarNombrePersona("O'Brien-Ana.")).toBe("OBrienAna");
  });

  it("el nombre de un negocio conserva números y los signos de una razón social", () => {
    expect(filtrarNombreNegocio("Mercado Modelo - Puesto 14")).toBe("Mercado Modelo - Puesto 14");
    expect(filtrarNombreNegocio("Distribuidora S.A.C. & Hnos (Centro)")).toBe("Distribuidora S.A.C. & Hnos (Centro)");
    expect(filtrarNombreNegocio("Bodega <script>$%*=;_")).toBe("Bodega script");
  });

  it("una descripción conserva la puntuación básica y descarta los caracteres especiales", () => {
    expect(filtrarTexto("Av. Real #123 (frente al parque), Piso 2 - Of. 5/6")).toBe("Av. Real #123 (frente al parque), Piso 2 - Of. 5/6");
    expect(filtrarTexto("¿Atiende? ¡Sí! N° 45; frágil: sí")).toBe("¿Atiende? ¡Sí! N° 45; frágil: sí");
    expect(filtrarTexto("precio $10")).toBe("precio 10");
    expect(filtrarTexto("100% x=1")).toBe("100 x1");
    expect(filtrarTexto("{a}[b]a|b")).toBe("abab");
    expect(filtrarTexto("~`^*_+@<>")).toBe("");
  });

  it("la placa queda en mayúsculas, con letras, números y guion", () => {
    expect(filtrarPlaca("abc-123")).toBe("ABC-123");
    expect(filtrarPlaca("ab c_1·2*3")).toBe("ABC123");
  });
});

describe("limitarDecimales", () => {
  it("recorta los decimales que sobran según el paso", () => {
    expect(limitarDecimales("12.3456", "0.01")).toBe("12.34");
    expect(limitarDecimales("0.123456", "0.0001")).toBe("0.1234");
    expect(limitarDecimales("12.5", "0.01")).toBe("12.5");
  });

  it("con paso entero no admite decimales", () => {
    expect(limitarDecimales("2021.5", "1")).toBe("2021");
  });

  it("sin paso deja el valor como está", () => {
    expect(limitarDecimales("1.2345")).toBe("1.2345");
  });
});

describe("soloCambios", () => {
  it("devuelve solo lo que cambió", () => {
    expect(soloCambios({ a: "1", b: "2", c: null }, { a: "1", b: "9", c: null })).toEqual({ b: "9" });
  });
});
