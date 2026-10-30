# 04 Retrospectiva del Sprint

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Líder del Proyecto** | Inciso Aguilar Elizabeth Antonela |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Sprint** | Sprint 4 — Sostenibilidad y Cierre (22-10-2026 – 13-11-2026) |
| **Fecha de la retrospectiva** | Por confirmar (contenido al 23-10-2026) |
| **Versión** | 1.0.0 |

[← Volver al README Principal](../../../../../README.md)

---

> **Documento preparado el 23-10-2026** con los hechos del sprint, como propuesta de la líder del proyecto para validar con el equipo en la reunión de retrospectiva.

## ¿Qué aprendimos?

- **Los datos de prueba chicos esconden los problemas de rendimiento.** Con las tablas casi vacías toda consulta parece rápida. Cargar seis meses de operación en una transacción que se deshace mostró dos mejoras reales: el listado de pedidos ordenaba todo sin un índice (7.0 a 0.1 ms) y el dashboard y el reporte contaban las paradas de todo el historial en vez de las del periodo (6.6 a 3.1 ms).
- **Un PDF se prueba leyéndolo de vuelta.** Las pruebas extraen el texto del archivo generado y se revisó una captura de sus páginas: así se vio, por ejemplo, que la primera versión no llevaba tildes aunque el formato las admite.
- **El tiempo de Render no está donde se supone.** El dashboard tarda lo mismo con 15 que con 450 rutas porque casi todo es la ida y vuelta a la base; lo que sí pesa es dibujar el PDF con una CPU de 0.1 (7.5 s el de un mes).
- **Lo que no tiene datos reales se declara como supuesto y se deja configurable** (el precio del combustible, la meta de CO₂, los árboles por tonelada): la misma lección de las horas punta del Sprint 3.
- **El rol de la base limita lo que se puede automatizar.** `app_admin` no puede crear índices, así que cada cambio de esquema es un `.sql` idempotente que se ejecuta a mano antes de desplegar, y hay que pedirlo con tiempo (IMP-023).
- **Verificar el estado de git antes de abrir el Pull Request.** Una corrección hecha después de los commits quedó fuera del Pull Request #62 y hubo que publicarla en uno posterior.

## ¿Qué estamos haciendo bien?

- Los 18 Story Points se completaron el día 2 de 23, con cada funcionalidad medida en Render desde el primer día (la acción 6 de la retrospectiva anterior) y no solo en local.
- La calidad es verificable y repetible: integración continua en verde, 359 pruebas del backend con 98 % de cobertura (100 % en el módulo nuevo), 99 de Vitest, 26 de Playwright, Lighthouse en 100 en accesibilidad, buenas prácticas y SEO, y W3C sin errores.
- El módulo nuevo respeta la independencia entre módulos (la prueba de arquitectura lo vigila) y cada endpoint nuevo está restringido al rol de administrador.
- El Pull Request #64 fue aprobado por dos compañeros antes del merge, con los pasos de revisión escritos para quien revisa.
- La auditoría de consultas quedó como un script que cualquiera puede volver a correr sin dejar datos.

## ¿Qué podemos hacer mejor?

- **Personas:** el trabajo sigue concentrándose en pocas personas (IMP-005, abierto). Conviene que cada integrante lleve evidencia de su aporte en el repositorio y en la documentación.
- **Relaciones:** los Pull Request #62 y #63 se fusionaron sin la aprobación de un compañero; recién el #64 la tuvo (IMP-025). Pedirla antes de cada merge, no después.
- **Procesos:** validar con la empresa los supuestos de sostenibilidad y cargar los datos reales de la flota antes de la sustentación; hacer las pruebas de aceptación con un integrante distinto de quien implementó la historia.
- **Herramientas:** el plan gratuito de Render (CPU limitada y ~2 s por petición) sigue condicionando el rendimiento (IMP-013, IMP-016, IMP-019, IMP-026).

### Acciones propuestas en el Sprint 3: estado al 23-10-2026

| # | Acción | Responsable propuesto | Estado |
|---|---|---|---|
| 1 | Reutilizar las matrices de distancia y tiempo entre peticiones, o resolverlas con una sola pasada de Dijkstra | Inciso Aguilar Elizabeth Antonela | Pendiente (IMP-019 abierto) |
| 2 | Calibrar los factores de hora punta con datos reales o con un criterio documentado | Equipo | Pendiente |
| 3 | Dejar registrada en GitHub la aprobación de cada Pull Request por un compañero | Equipo | En curso: cumplida en el #64 (Yago Espinoza y Keen Guerra); no en el #62 ni en el #63 |
| 4 | Escribir el checklist de RLS y evaluar pytest en la integración continua con una base de pruebas dedicada | Guerra Lozano Keen | Pendiente; el sprint no creó tablas nuevas, así que no hizo falta aplicar el checklist |
| 5 | Antes de crear cuentas de conductores reales, revisar el hook de Supabase que emite `ver` en el token (IMP-020) | Inciso Aguilar Elizabeth Antonela | Pendiente |
| 6 | Medir en Render cada funcionalidad nueva que dependa del motor, desde su primer día | Quien la implemente | **Hecho:** dashboard, plan de compensación y reporte PDF medidos en Render el mismo día en que se desplegaron |

### Acciones propuestas para el cierre del proyecto

| # | Acción | Responsable propuesto |
|---|---|---|
| 1 | Ejecutar SonarQube Cloud sobre backend y frontend al terminar todos los sprints, corregir los hallazgos verificables y documentarlos | Equipo |
| 2 | Mapear el sistema a cada categoría de OWASP Top 10 2025 y registrar las brechas | Equipo |
| 3 | Revisar los criterios nuevos de WCAG 2.2 sobre las pantallas del sistema | Uscuvilca Ramos Abraham Luis |
| 4 | Aplicar la escala SUS en positivo y evaluar las heurísticas de Nielsen con el equipo y usuarios de prueba | Equipo |
| 5 | Cargar el precio de compra y la vida útil de los vehículos reales y validar los supuestos de sostenibilidad con la empresa | Inciso Aguilar Elizabeth Antonela |
| 6 | Pedir la aprobación de un compañero en cada Pull Request antes del merge | Equipo |
| 7 | Medir Lighthouse sobre las pantallas desplegadas en Vercel, incluida Sostenibilidad | Inciso Aguilar Elizabeth Antonela |

Los responsables son una propuesta y se confirman en la reunión de retrospectiva.

## Aporte por integrante

La columna «Asignación en Jira» es el dato objetivo del tablero. La columna «Aporte declarado por el equipo» recoge lo que informó la líder del proyecto; no se estima ni se reparte un porcentaje.

| Integrante | Asignación en Jira (Sprint 4) | Aporte declarado por el equipo |
|---|---|---|
| Inciso Aguilar Elizabeth Antonela | Sin ítems propios en el tablero; trabajó junto con Yago en HU-015, HU-016, HU-017 y HT-12 | Construcción de HU-015, HU-016, HU-017, HT-11 y HT-12: el módulo de sostenibilidad, el reporte PDF, el costo del ciclo de vida de la flota, la auditoría y optimización de consultas, las pruebas y las migraciones; mediciones en Render; documentación del sprint |
| Espinoza Tiza Yago Imanol | HU-015, HU-016, HU-017, HT-12 | Pruebas del sistema como tester. Aprobó el Pull Request #64 en GitHub |
| Uscuvilca Ramos Abraham Luis | Sin ítems propios en el tablero; trabajó junto con Keen en HT-11 | Pruebas del sistema como tester |
| Guerra Lozano Keen | HT-11 | Pruebas del sistema como tester. Aprobó el Pull Request #64 en GitHub |

---

[← Volver al README Principal](../../../../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-10-23 | Versión inicial: lo aprendido, lo que va bien, lo que se puede mejorar, el estado de las acciones del Sprint 3, las acciones propuestas para el cierre del proyecto y el aporte por integrante | Inciso Aguilar Elizabeth Antonela |
