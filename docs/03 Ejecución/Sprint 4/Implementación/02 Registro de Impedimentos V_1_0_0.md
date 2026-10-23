# 02 Registro de Impedimentos

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Líder del Proyecto** | Inciso Aguilar Elizabeth Antonela |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Sprint** | Sprint 4 — Sostenibilidad y Cierre (22-10-2026 – 13-11-2026) |
| **Versión** | 1.0.0 |

[← Volver al README Principal](../../../../README.md)

---

La numeración continúa la del [Registro del Sprint 3](../../Sprint%203/Implementaci%C3%B3n/02%20Registro%20de%20Impedimentos%20V_1_1_0.md) (IMP-005 a IMP-022). Se arrastran los impedimentos que siguen abiertos y se registran los del Sprint 4 (IMP-023 a IMP-026). IMP-018, IMP-020, IMP-021 e IMP-022 quedaron resueltos en el Sprint 3 y no se repiten.

| Impedimento # | Fecha de Registro | Descripción del Impedimento así como el Impacto en el Proyecto | Prioridad | Reportado por | Fecha tope de Resolución | Estado | Fecha de Resolución | Resolución/Comentarios |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| IMP-005 | 2026-09-20 | *(Arrastrado del Sprint 3)* Disponibilidad limitada de los integrantes por carga académica (RSK-005): la implementación se concentra casi por completo en un solo integrante | Alta | Inciso Aguilar Elizabeth Antonela | 2026-11-13 | Abierto | — | Cada ítem del Sprint 4 tiene responsable en Jira; el aporte de cada integrante se documenta con hechos declarados en la revisión y la retrospectiva. Dos compañeros revisaron y aprobaron el Pull Request #64 |
| IMP-013 | 2026-10-05 | *(Arrastrado del Sprint 3)* La CPU compartida de Render gratuito (0.1 vCPU) hace lento el cálculo del motor; en el Sprint 4 también alarga la generación del reporte PDF | Media | Inciso Aguilar Elizabeth Antonela | 2026-11-13 | Abierto | — | La re-optimización cumple su límite de 30 s; el reporte de un mes tarda 7.5 s (ver IMP-026). Mejora posible: un plan con más CPU |
| IMP-016 | 2026-10-06 | *(Arrastrado del Sprint 3)* Cada petición a la API tarda cerca de 2 s en Render gratuito por los viajes a la base remota de Supabase | Media | Inciso Aguilar Elizabeth Antonela | 2026-11-13 | Abierto | — | Medido en el Sprint 4: el dashboard con 450 rutas (2.4 s) cuesta casi lo mismo que con 15 (2.3 s), así que el tiempo es de red y no de las consultas, que tardan unos 3 ms en el servidor |
| IMP-019 | 2026-10-20 | *(Arrastrado del Sprint 3)* La segunda matriz de tiempos de hora punta sube el cálculo de las matrices de unos 9 a unos 13 s en Render gratuito; el ACO de la re-optimización hace 2 a 3 iteraciones | Media | Inciso Aguilar Elizabeth Antonela | 2026-11-13 | Abierto | — | La re-optimización cumple (22.2 s en el servidor). Mejora posible: reutilizar las matrices entre peticiones, una sola pasada de Dijkstra o más CPU |
| IMP-023 | 2026-10-23 | El rol `app_admin` no es dueño de las tablas: no puede crear columnas ni índices, ni siquiera dentro de una transacción de prueba. Los cambios de esquema de HU-016 (precio de compra y vida útil del vehículo) y de HT-11 (índice de pedidos) solo se pueden aplicar desde el SQL Editor de Supabase y no se pudo simular el efecto del índice antes de crearlo | Media | Inciso Aguilar Elizabeth Antonela | 2026-10-23 | Resuelto | 2026-10-23 | Cada cambio va en un `.sql` idempotente de `backend/scripts/` (`migracion_ciclo_vida.sql`, `migracion_indices_ht11.sql`) que la líder ejecutó antes de desplegar; el efecto del índice se midió con el script de auditoría antes y después de crearlo (7.0 a 0.1 ms) |
| IMP-024 | 2026-10-23 | No hay datos reales de la empresa ficticia para el precio del combustible, la meta mensual de CO₂, el CO₂ que absorbe un árbol ni el precio y la vida útil de los vehículos. Las cifras del dashboard, del plan de compensación y del costo del ciclo de vida dependen de supuestos | Media | Inciso Aguilar Elizabeth Antonela | 2026-11-13 | Abierto | — | Los tres supuestos son variables de entorno con valor por defecto (S/ 4.50 por litro, 800 kg al mes y 22 kg por árbol al año) y se declaran en la pantalla, el PDF y los documentos; el precio y la vida útil son opcionales y los vehículos sin ellos salen como «sin dato». Falta validarlos y cargar los datos |
| IMP-025 | 2026-10-23 | Los Pull Request #62 y #63 se fusionaron antes de que un compañero los aprobara en GitHub, por lo que el criterio 3 del Definition of Done no tenía evidencia en ellos | Media | Inciso Aguilar Elizabeth Antonela | 2026-10-23 | Resuelto | 2026-10-23 | El Pull Request #64 fue aprobado por Yago Espinoza y Keen Guerra antes del merge, con los pasos de revisión documentados. Los #62 y #63 quedan sin aprobación registrada; desde el #64 cada Pull Request espera la aprobación de un compañero |
| IMP-026 | 2026-10-23 | El reporte PDF de un mes completo tarda unos 7.5 s en Render (3.3 s el de un día): la CPU de 0.1 multiplica por unas 12 el dibujo del documento, que en una máquina de desarrollo toma 0.4 s | Baja | Inciso Aguilar Elizabeth Antonela | 2026-11-13 | Abierto | — | Aceptable para una descarga manual: la pantalla muestra «Generando reporte…» y el PDF lista como máximo 300 rutas. Se resolvería con un plan con más CPU |

---

[← Volver al README Principal](../../../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-10-23 | Versión inicial: se arrastran IMP-005, IMP-013, IMP-016 e IMP-019 y se registran IMP-023 a IMP-026 | Inciso Aguilar Elizabeth Antonela |
