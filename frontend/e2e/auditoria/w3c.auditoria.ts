import { expect, test } from "@playwright/test";
import { PANTALLAS, abrir } from "./pantallas";

// Validación del HTML renderizado con el validador Nu del W3C (el mismo del Sprint 2). Se envía el DOM ya dibujado
// por la aplicación, con datos sintéticos.
const VALIDADOR = "https://validator.w3.org/nu/?out=json";

interface Mensaje {
  type: "error" | "info" | "non-document-error";
  subType?: string;
  message: string;
  extract?: string;
  lastLine?: number;
}

for (const pantalla of PANTALLAS) {
  test(`W3C: ${pantalla.nombre}`, async ({ page }) => {
    await abrir(page, pantalla);
    const html = await page.evaluate(() => `<!DOCTYPE html>\n${document.documentElement.outerHTML}`);

    const respuesta = await page.request.post(VALIDADOR, {
      headers: { "Content-Type": "text/html; charset=utf-8", "User-Agent": "RouteZero-auditoria/1.0" },
      data: html,
      timeout: 90_000,
    });
    expect(respuesta.ok(), `El validador respondió ${respuesta.status()}`).toBeTruthy();
    const mensajes = ((await respuesta.json()) as { messages: Mensaje[] }).messages;
    const errores = mensajes.filter((m) => m.type === "error");
    const avisos = mensajes.filter((m) => m.type === "info" && m.subType === "warning");
    console.log(`W3C ${pantalla.nombre}: ${errores.length} error(es), ${avisos.length} aviso(s)`);
    for (const m of [...errores, ...avisos]) console.log(`  [${m.type === "error" ? "ERROR" : "AVISO"}] ${m.message}${m.lastLine ? ` (línea ${m.lastLine})` : ""}\n    ${(m.extract ?? "").replace(/\s+/g, " ").slice(0, 160)}`);
    expect(errores, "errores de HTML").toEqual([]);
  });
}
