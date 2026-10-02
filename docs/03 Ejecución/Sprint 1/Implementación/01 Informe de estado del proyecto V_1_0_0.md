# 01 Informe de Estado del Proyecto

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Líder del Proyecto** | Inciso Aguilar Elizabeth Antonela |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Fecha del reporte** | 2026-10-01 |
| **Periodo del Informe** | 19-09-2026 – 02-10-2026 (Sprint 1 — Base del sistema) |
| **Versión** | 1.0.0 |

[← Volver al README Principal](../../../../README.md)

---

## Estado del proyecto

| Variables de control | Descripción del estado |
|---|---|
| **Alcance** | 13/13 ítems completados (8 Historias de Usuario + 5 Historias Técnicas, 42/42 Story Points comprometidos). El backend (FastAPI) cubre autenticación con MFA y sesiones, gestión de flota, clientes y pedidos; el frontend (React + Vite + TypeScript) cubre login, MFA, sesiones, flota, pedidos con mapa real de Huancayo (Leaflet + OpenStreetMap) y una vista mobile-first para el rol Conductor. Ver el detalle ítem por ítem en [`01 Sprint 1 Plan de ejecución y estado V_1_5_0.md`](../01%20Sprint%201%20Plan%20de%20ejecuci%C3%B3n%20y%20estado%20V_1_5_0.md). |
| **Cronograma** | El sprint se cerró al 100 % de su alcance comprometido un día antes de la fecha de inspección (02-10-2026), sin necesidad de aplicar el orden de recorte de alcance previsto originalmente. No hay atraso. |
| **Costos** | Presupuesto estimado académico: **USD $10,304.00** (ver [`04 Presupuesto del proyecto V_1_0_0.md`](../../../02%20Planificaci%C3%B3n/04%20Presupuesto%20del%20proyecto%20V_1_0_0.md)). Ejecución real del Sprint 1 sin desviación: toda la infraestructura (Render, Vercel, Supabase) se mantuvo dentro de los planes gratuitos previstos, por lo que el OPEX ejecutado es **USD $0.00**, igual a lo presupuestado. |
| **Calidad** | 65 pruebas automatizadas con pytest en el backend (95 % de cobertura combinada sobre autenticación, MFA, sesiones, flota, clientes, pedidos, auditoría y cifrado); el frontend cubre con Jest/Vitest únicamente los componentes de MFA. Análisis estático con Bandit + pip-audit (backend) y npm audit (frontend): 0 vulnerabilidades reales en dependencias. Prueba explícita de inyección SQL con payloads reales. Lighthouse y validación W3C del frontend aún no se han ejecutado formalmente. |

## Riesgos

| Riesgo | Responsable | Mitigación |
|---|---|---|
| El Custom Access Token Hook de Supabase parece cachear el `token_version` del usuario: tras revocar todas sus sesiones, un login nuevo puede seguir recibiendo un valor viejo y fallar con "Token revocado" (relacionado con RSK-006 del [`03 Registro de riesgos`](../../../02%20Planificaci%C3%B3n/03%20Registro%20de%20riesgos%20V_1_0_0.md)) | Guerra Lozano Keen | Revisar en el panel de Supabase si el hook tiene caché de resultado activada y desactivarla; documentado junto a las demás particularidades de Supabase en `design.md` del cambio OpenSpec archivado |
| Disponibilidad limitada de los integrantes del equipo por carga académica de otras asignaturas, materializada durante el Sprint 1 (RSK-005): la carga de trabajo de backend y frontend se concentró casi por completo en un solo integrante | Inciso Aguilar Elizabeth Antonela | Redistribuir explícitamente los módulos del Sprint 2 (motor de optimización, conductores) entre todo el equipo desde el Sprint Planning, con fechas de corte intermedias para detectar atrasos antes del cierre |

## Próximos avances

- **Sprint 2**: motor de optimización de rutas (VRPTW + Green VRP con ACO como algoritmo principal), módulo de conductores (RF-008, con el mecanismo de consentimiento explícito de RN-013), y las reglas de negocio aún pendientes (RN-002/003, RN-004, RN-005, RN-006, RN-008, RN-009, RN-012, RN-015), que dependen de conductores y rutas.
- Ampliar la cobertura de pruebas del frontend (Jest/Vitest) a los módulos de Flota y Pedidos, hoy solo cubiertos por verificación manual.
- Ejecutar auditorías de Lighthouse y validación W3C sobre el frontend desplegado en Vercel.
- Nueva versión de [`11. Base de datos`](../../../01%20Inicio/11.%20Base%20de%20datos%20V_1_4_0.md) que documente también los módulos de flota, clientes y pedidos (ya implementados pero sin reflejar en ese documento).

## Notas

El sistema corre en producción real, no solo en entorno local: backend en Render ([`routezero-7k7j.onrender.com`](https://routezero-7k7j.onrender.com)) y frontend en Vercel ([`route-zero-omega.vercel.app`](https://route-zero-omega.vercel.app)), con login y CORS verificados de extremo a extremo contra el origen de producción. La demostración del 02-10-2026 se hará sobre este despliegue en vivo.

---

[← Volver al README Principal](../../../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-10-01 | Versión inicial: informe de estado del Sprint 1 al cierre del sprint, un día antes de la inspección | Inciso Aguilar Elizabeth Antonela |
