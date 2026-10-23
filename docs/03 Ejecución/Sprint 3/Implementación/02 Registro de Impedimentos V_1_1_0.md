# 02 Registro de Impedimentos

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Líder del Proyecto** | Inciso Aguilar Elizabeth Antonela |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Sprint** | Sprint 3 — Rutas y Visualización (17-10-2026 – 30-10-2026) |
| **Versión** | 1.1.0 |

[← Volver al README Principal](../../../../README.md)

---

La numeración continúa la del [Registro del Sprint 2](../../Sprint%202/Implementaci%C3%B3n/02%20Registro%20de%20Impedimentos%20V_1_2_0.md) (IMP-005 a IMP-017). Se arrastran los impedimentos que siguen abiertos y se registran los del Sprint 3 (IMP-018 a IMP-022).

| Impedimento # | Fecha de Registro | Descripción del Impedimento así como el Impacto en el Proyecto | Prioridad | Reportado por | Fecha tope de Resolución | Estado | Fecha de Resolución | Resolución/Comentarios |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| IMP-005 | 2026-09-20 | *(Arrastrado del Sprint 2)* Disponibilidad limitada de los integrantes por carga académica (RSK-005): la implementación se concentra casi por completo en un solo integrante | Alta | Inciso Aguilar Elizabeth Antonela | 2026-10-30 | Abierto | — | Cada ítem del Sprint 3 tiene responsable en Jira; el aporte de cada integrante se documenta con hechos declarados en la revisión y la retrospectiva |
| IMP-013 | 2026-10-05 | *(Arrastrado del Sprint 2)* La CPU compartida de Render gratuito (0.1 vCPU) hace lento el cálculo del motor; afecta el objetivo de re-optimizar en ≤ 30 s de HU-012 | Media | Inciso Aguilar Elizabeth Antonela | 2026-10-30 | Abierto | — | Re-optimizar solo las rutas afectadas y medir en Render desde el primer día |
| IMP-016 | 2026-10-06 | *(Arrastrado del Sprint 2)* Cada petición a la API tarda cerca de 1 s en Render gratuito por los varios viajes a la base remota de Supabase; deja el rendimiento de Mapa y Pedidos en 85-89 en Lighthouse | Media | Inciso Aguilar Elizabeth Antonela | 2026-10-30 | Abierto | — | Reducir los viajes a la base por petición; si no alcanza, queda documentado como limitación del plan gratuito |
| IMP-018 | 2026-10-20 | Supabase dejó el proyecto en estado COMING_UP tras una incidencia del proveedor («Projects stuck in restarting state»): la base no respondía y bloqueó las pruebas contra la base real y la migración de HU-012 | Alta | Inciso Aguilar Elizabeth Antonela | 2026-10-20 | Resuelto | 2026-10-20 | Se esperó a que Supabase restableciera el proyecto, se verificó la conexión y se aplicó `migracion_reoptimizacion.sql`. No hay acción propia posible: es un riesgo del plan gratuito |
| IMP-019 | 2026-10-20 | La segunda matriz de tiempos de hora punta (RF-003) sube el cálculo de las matrices de unos 9 a unos 13 s en Render gratuito: el motor de la re-optimización queda con unos 6 s y el ACO hace 2 a 3 iteraciones | Media | Inciso Aguilar Elizabeth Antonela | 2026-10-30 | Abierto | — | La re-optimización cumple (22.2 s en el servidor y 24.0 s desde fuera, con el presupuesto en 25 s) y parte del plan vigente, por lo que no empeora. Mejora posible: reutilizar las matrices entre peticiones, una sola pasada de Dijkstra o más CPU |
| IMP-020 | 2026-10-20 | La cuenta conductora de prueba recibía 401 «Token revocado» en todos los endpoints: `token_version` valía 2 en la base y Supabase emitía tokens con `ver = 1` (su hook parece cachear la versión). Un conductor real con ese desajuste quedaría bloqueado | Media | Inciso Aguilar Elizabeth Antonela | 2026-10-20 | Resuelto | 2026-10-20 | Se restableció `token_version` a 1. Queda anotado revisar el hook antes de crear cuentas de conductores reales |
| IMP-021 | 2026-10-22 | En el celular el menú lateral aparecía expandido (el 56 % del ancho) y las pantallas de operaciones se desbordaban horizontalmente. Lo detectaron las pruebas de extremo a extremo en el viewport de un celular, no las de componentes | Media | Equipo (pruebas de HT-10) | 2026-10-22 | Resuelto | 2026-10-22 | El menú empieza colapsado en pantallas de menos de 900 px, el panel del mapa es plegable y las listas desplegables caben en su fila; hay pruebas que lo vigilan |
| IMP-022 | 2026-10-22 | El equipo no tiene Java, por lo que no se puede ejecutar el validador Nu del W3C en local; el validador público exige enviar el HTML | Baja | Inciso Aguilar Elizabeth Antonela | 2026-10-22 | Resuelto | 2026-10-22 | Se valida el DOM renderizado con datos sintéticos contra el servicio público, sin enviar datos reales. No puede ejecutarse en CI ni sin internet |

---

[← Volver al README Principal](../../../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-10-20 | Versión inicial: se arrastran IMP-005, IMP-013 e IMP-016 del Sprint 2 | Inciso Aguilar Elizabeth Antonela |
| V_1_1_0 | 2026-10-22 | Se registran IMP-018 a IMP-022: la base caída, el costo de la matriz de hora punta, el token de la cuenta conductora, el menú del celular y el validador W3C | Inciso Aguilar Elizabeth Antonela |
