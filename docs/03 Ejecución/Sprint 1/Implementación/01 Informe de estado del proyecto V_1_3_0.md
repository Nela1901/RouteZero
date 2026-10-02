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
| **Versión** | 1.3.0 |

[← Volver al README Principal](../../../../README.md)

---

## Estado del proyecto

| Variables de control | Descripción del estado |
|---|---|
| **Alcance** | 13/13 ítems completados (8 Historias de Usuario + 5 Historias Técnicas, 42/42 Story Points comprometidos). El backend (FastAPI) cubre autenticación con MFA y sesiones, gestión de flota, clientes y pedidos; el frontend (React + Vite + TypeScript) cubre login, MFA, sesiones, flota, pedidos con mapa real de Huancayo (Leaflet + OpenStreetMap) y una vista mobile-first para el rol Conductor. Ver el detalle ítem por ítem en [`01 Sprint 1 Plan de ejecución y estado V_1_5_0.md`](../01%20Sprint%201%20Plan%20de%20ejecuci%C3%B3n%20y%20estado%20V_1_5_0.md). Además, ya implementado sobre ese alcance: búsqueda de direcciones con geocodificación y ajuste del punto sobre el mapa en el registro de pedidos/clientes (reemplaza la captura manual de lat/lng), vista de detalle al hacer clic en un pedido, y notificaciones/confirmaciones visuales propias del sistema para las acciones principales. |
| **Cronograma** | El sprint se cerró al 100 % de su alcance comprometido un día antes de la fecha de inspección (02-10-2026), sin necesidad de aplicar el orden de recorte de alcance previsto originalmente. No hay atraso. |
| **Costos** | Presupuesto estimado académico: **USD $10,304.00** (ver [`04 Presupuesto del proyecto V_1_0_0.md`](../../../02%20Planificaci%C3%B3n/04%20Presupuesto%20del%20proyecto%20V_1_0_0.md)). Ejecución real del Sprint 1 sin desviación: toda la infraestructura (Render, Vercel, Supabase) se mantuvo dentro de los planes gratuitos previstos, por lo que el OPEX ejecutado es **USD $0.00**, igual a lo presupuestado. |
| **Calidad** | 65 pruebas automatizadas con pytest en el backend (95 % de cobertura combinada sobre autenticación, MFA, sesiones, flota, clientes, pedidos, auditoría y cifrado); el frontend cubre con Jest/Vitest únicamente los componentes de MFA. Análisis estático con Bandit + pip-audit (backend) y npm audit (frontend): 0 vulnerabilidades reales en dependencias. Prueba explícita de inyección SQL con payloads reales. Lighthouse y validación W3C del frontend aún no se han ejecutado formalmente. |

## Riesgos

| Riesgo | Responsable | Mitigación |
|---|---|---|
| Disponibilidad limitada de los integrantes del equipo por carga académica de otras asignaturas, materializada durante el Sprint 1 (RSK-005): la implementación de backend y frontend se concentró casi por completo en un solo integrante. El resto del equipo sí participó durante el sprint revisando el sistema en distintos momentos y reportando errores encontrados por chat, que se priorizaron junto con los detectados internamente (ver [`02 Registro de Impedimentos`](02%20Registro%20de%20Impedimentos%20V_1_1_0.md)), pero no tomó módulos propios de implementación | Inciso Aguilar Elizabeth Antonela | Redistribuir explícitamente los módulos del Sprint 2 (motor de optimización, conductores) entre todo el equipo desde el Sprint Planning, con fechas de corte intermedias para detectar atrasos antes del cierre |

**Riesgo resuelto el 01-10-2026 (relacionado con RSK-006 del [`03 Registro de riesgos`](../../../02%20Planificaci%C3%B3n/03%20Registro%20de%20riesgos%20V_1_0_0.md)):** el Custom Access Token Hook de Supabase cacheaba el `token_version` del usuario, por lo que un login nuevo tras revocar todas las sesiones podía fallar con "Token revocado" — reproducido en producción la noche antes de la inspección. Se corrigió en el código propio en vez de depender del hook: se dejó de incrementar `token_version` al revocar sesiones (detección de robo de sesión y "cerrar todas"), apoyándose únicamente en `sesiones_activas.estado`, que ya invalida el acceso de inmediato en cada request sin pasar por el hook. El único costo residual es que un access token ya emitido sigue vigente hasta sus 15 minutos naturales tras una revocación, igual que el resto de JWTs del proyecto — ver IMP-006 del [`02 Registro de Impedimentos`](02%20Registro%20de%20Impedimentos%20V_1_1_0.md).

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
| V_1_1_0 | 2026-10-01 | Se agrega a "Próximos avances" el hueco de usabilidad detectado en el registro de pedidos (captura manual de lat/lng) y la mejora propuesta para el Sprint 2 (geocodificación + ajuste sobre el mapa) | Inciso Aguilar Elizabeth Antonela |
| V_1_2_0 | 2026-10-01 | Se marca como resuelto el riesgo del Custom Access Token Hook de Supabase (reproducido en producción la noche antes de la inspección): se corrigió dejando de incrementar `token_version` al revocar sesiones, apoyándose solo en `sesiones_activas.estado` | Inciso Aguilar Elizabeth Antonela |
| V_1_3_0 | 2026-10-02 | Se marca como implementada la mejora de geocodificación en Pedidos (antes listada como pendiente) y se agregan la vista de detalle de pedido y las notificaciones/confirmaciones propias al alcance. Se precisa el riesgo RSK-005: el resto del equipo participó durante el sprint revisando el sistema y reportando errores, sin tomar módulos propios de implementación | Inciso Aguilar Elizabeth Antonela |
