import type { Page } from "@playwright/test";
import { congestion, conSesion, miRuta, parada, resumenRuta, rutaMapa, simularApi, type Rol } from "../api";

/** Las pantallas que se auditan, cada una con su sesión y los datos sintéticos que la llenan. */
export interface Pantalla {
  nombre: string;
  ruta: string;
  rol?: Rol; // sin rol: pantalla pública (inicio de sesión)
  preparar?: (page: Page) => Promise<void>;
}

const activa = rutaMapa("r1", "ABC-101", "EN_EJECUCION");
const borrador = rutaMapa("r2", "XYZ-202", "PLANIFICADA");

export const PANTALLAS: Pantalla[] = [
  { nombre: "Inicio de sesión", ruta: "/" },
  {
    nombre: "Mapa con rutas",
    ruta: "/app/mapa",
    rol: "ADMINISTRADOR",
    preparar: async (page) => {
      await simularApi(page, { rol: "ADMINISTRADOR", mapa: [activa, borrador], congestion: congestion("AMARILLO", "08:30:00") });
    },
  },
  {
    nombre: "Rutas",
    ruta: "/app/rutas",
    rol: "ADMINISTRADOR",
    preparar: async (page) => {
      await simularApi(page, {
        rol: "ADMINISTRADOR",
        mapa: [activa],
        rutas: [resumenRuta(activa)],
        incidentes: [{ incidente_id: "i1", calle: "Av. Ferrocarril", factor: 3, descripcion: null, activo: true, creado_en: "2026-10-22T10:00:00Z" }],
      });
    },
  },
  {
    nombre: "Conductor con ruta",
    ruta: "/",
    rol: "CONDUCTOR",
    preparar: async (page) => {
      const datos = miRuta([parada(1, { estado_entrega: "ENTREGADO" }), parada(2), parada(3)], "EN_EJECUCION");
      datos.alertas = [{ calle: "Av. Ferrocarril", nivel: "AMARILLO", factor: 1.8, motivos: ["hora punta"], en_tu_ruta: true, segmentos: [[[-12.07, -75.2], [-12.071, -75.201]]] }];
      await simularApi(page, { rol: "CONDUCTOR", miRuta: datos });
    },
  },
  {
    nombre: "Conductor sin ruta",
    ruta: "/",
    rol: "CONDUCTOR",
    preparar: async (page) => {
      await simularApi(page, { rol: "CONDUCTOR" });
    },
  },
];

/** Deja la pantalla lista: datos simulados, sesión iniciada y navegada a su ruta. */
export async function abrir(page: Page, pantalla: Pantalla) {
  if (pantalla.preparar) await pantalla.preparar(page);
  else await simularApi(page);
  if (pantalla.rol) await conSesion(page, pantalla.rol);
  await page.goto(pantalla.ruta);
  await page.waitForLoadState("networkidle");
}
