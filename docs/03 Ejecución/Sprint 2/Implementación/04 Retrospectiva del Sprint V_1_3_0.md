# 04 Retrospectiva del Sprint

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Líder del Proyecto** | Inciso Aguilar Elizabeth Antonela |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Sprint** | Sprint 2 — Personas y Algoritmo ACO (03-10-2026 – 16-10-2026) |
| **Fecha de la retrospectiva** | 2026-10-16 (prevista); contenido preparado con el estado al 2026-10-06 |
| **Versión** | 1.3.0 |

[← Volver al README Principal](../../../../README.md)

---

> **Estado del documento.** Recoge lo aprendido hasta el 06-10-2026. Si la reunión de retrospectiva del 16-10-2026 aporta acuerdos nuevos, se registran en una nueva versión.

## ¿Qué aprendimos?

- **Medir en el entorno real, y pronto.** El motor se veía bien en local, pero en Render gratuito la generación tardó 64 s (límite 45 s). El perfilado mostró que el cuello de botella no era el algoritmo sino guardar el resultado fila por fila contra una base remota (IMP-010). Con INSERT en bloque bajó a 29.1 s.
- **Si el entorno no da métricas, hay que instrumentar.** Render gratuito oculta memoria y CPU (IMP-012). La respuesta de la API ahora devuelve los tiempos por etapa y el pico de memoria, así que la medición no depende del panel del proveedor.
- **Verificar las normas que se citan.** El «DS 033-2012-MTC» citado en la documentación no existe; es el DS 033-2001-MTC (IMP-014). Se comprobó contra el texto oficial.
- **Probar con datos reales las reglas de negocio entre módulos.** Los vehículos y conductores de rutas ya confirmadas podían reasignarse el mismo día (IMP-011); apareció al razonar con datos reales, no con pruebas de un solo módulo.
- **Un cambio de contrato de la API se entrega con todos sus consumidores.** Al paginar el listado de pedidos se rompió el mapa en producción (IMP-017). Lo detectó la auditoría de Lighthouse, no una prueba. Ahora existe `MapaPage.test.tsx` y la regla de buscar a todos los consumidores antes de cambiar un contrato.
- **No correr pruebas y mediciones a la vez sobre la misma cuenta.** `test_sesiones` y `test_mfa` borran las sesiones de esa cuenta y produjeron falsos fallos (IMP-015).
- **La accesibilidad y el HTML válido se corrigen mejor con herramienta que a ojo.** Lighthouse y el validador W3C encontraron contraste insuficiente, nombres accesibles faltantes, un `<style>` dentro del `<body>`, `<div>` dentro de `<span>` y etiquetas que envolvían dos controles. Hasta ese momento ninguno era visible en el uso normal.
- **Una regla pensada para proteger puede perjudicar.** El `Disallow: /app/` del `robots.txt` hacía caer el SEO de las pantallas internas a 63; las pantallas ya están protegidas por el inicio de sesión, así que se retiró.

## ¿Qué estamos haciendo bien?

- El núcleo del sprint (39 de 41 SP) quedó listo 10 días antes de la inspección, con el motor medido en el despliegue real y no solo en local.
- Se trabajó con especificación primero: el cambio `add-motor-rutas` de OpenSpec quedó archivado con sus cuatro especificaciones (30 requisitos), y las correcciones posteriores (doble asignación) se llevaron también a la especificación.
- Calidad verificable: 96 % de cobertura, Bandit, `pip-audit` y `npm audit` sin hallazgos críticos, Lighthouse con accesibilidad y SEO en 100 y W3C con 0 errores en las 8 pantallas.
- Las decisiones se documentan con su porqué (depósito, distancias por OpenStreetMap, flujo borrador → confirmar, límites del plan gratuito de Render) y las versiones de los documentos no se sobrescriben.
- Los errores se corrigieron el mismo día de detectarse y quedaron con su impedimento y su prueba de regresión.

## ¿Qué podemos hacer mejor?

### Personas

El equipo colaboró, pero la autoría quedó poco visible: los commits salen de una sola cuenta de GitHub, la de la líder, para ir más rápido (ver «Aporte por integrante»). IMP-005 sigue abierto. Mejora acordada: que cada integrante deje constancia de su aporte (por ejemplo, abriendo o revisando su propio Pull Request) y no solo en los documentos de cierre.

### Relaciones

El checkpoint de medio sprint se adelantó del 10-10-2026 al 06-10-2026, porque el núcleo del sprint ya estaba completo; su resultado está en el informe de estado. Las revisiones cruzadas existen en la práctica y son presenciales: cuando el equipo trabaja junto en clase, los cambios se revisan en conjunto desde la computadora de la líder (por ejemplo, la revisión de la HU-009). La constancia en GitHub empezó el 06-10-2026: el Pull Request #45 fue aprobado por YagoEspinoza (criterio 3 del Definition of Done). Falta hacerlo en todos los Pull Request.

### Procesos

Los hallazgos de Lighthouse y W3C llegaron en la última semana. Conviene correrlos desde el primer módulo y no al cierre, y automatizarlos junto con las pruebas en cada Pull Request. Las pruebas de integración del frontend alcanzan solo a algunas pantallas; el mapa no tenía ninguna hasta la regresión.

### Herramientas

El plan gratuito de Render condiciona el rendimiento: CPU limitada (IMP-013) y cerca de 1 s por petición a la base remota (IMP-016), lo que deja el rendimiento de Mapa y Pedidos en 85-89 en Lighthouse. Opciones: reducir viajes por petición, o un plan con más CPU y una región cercana a Supabase.

### Acciones heredadas del Sprint 1: estado al 06-10-2026

| # | Acción | Responsable | Estado |
|---|---|---|---|
| 1 | Redistribuir los módulos del Sprint 2 entre todos los integrantes, con un dueño por módulo | Inciso Aguilar Elizabeth Antonela | Hecho en Jira (cada ítem tiene responsable). La ejecución se concentró en gran parte en la líder; el equipo declara apoyos en HU-009, HU-010 y HU-011 |
| 2 | Checkpoint de medio sprint con reporte de avance individual | Inciso Aguilar Elizabeth Antonela | Hecho el 06-10-2026 (adelantado respecto al 10-10-2026); resultado en el informe de estado |
| 3 | GitHub Actions con pytest, Bandit/pip-audit y npm audit en cada Pull Request | Guerra Lozano Keen | Pendiente; se trasladará al Sprint 3. El análisis estático se ejecutó a mano y quedó sin hallazgos críticos |
| 4 | Checklist de revisión de políticas RLS para toda tabla nueva en Supabase | Guerra Lozano Keen | Aplicado en la práctica a `conductores`, `rutas` y `ruta_pedidos` (política permisiva más GRANT explícito); falta dejarlo escrito como checklist formal |
| 5 | Tope superior de versión en `requirements.txt` | Inciso Aguilar Elizabeth Antonela | Parcial: la versión de Python en Render sigue sin fijarse |

### Acciones propuestas para el Sprint 3

| # | Acción | Responsable propuesto |
|---|---|---|
| 1 | Correr Lighthouse y W3C al terminar cada pantalla, no al cierre del sprint | Equipo |
| 2 | Antes de cambiar un contrato de la API, listar y actualizar todos sus consumidores en el mismo Pull Request | Quien modifique el endpoint |
| 3 | Reducir los viajes a la base por petición (IMP-016) | Inciso Aguilar Elizabeth Antonela |
| 4 | Fijar la versión de Python en Render y poner topes en `requirements.txt` | Inciso Aguilar Elizabeth Antonela |
| 5 | Integrar cada Pull Request solo después de que un compañero lo apruebe en GitHub (el primero fue el #45, aprobado por YagoEspinoza); la revisión presencial se mantiene | Equipo |

Los responsables son una propuesta y se confirman en la reunión de retrospectiva.

## Aporte por integrante

| Integrante | Asignación en Jira (Sprint 2) | Aporte declarado por el equipo |
|---|---|---|
| Inciso Aguilar Elizabeth Antonela | HU-011, HT-08 | Motor de rutas, red vial, arquitectura escalable, pruebas de rendimiento y carga; documentación del sprint |
| Guerra Lozano Keen | HU-009, HT-06 | Revisión de la HU-009 |
| Uscuvilca Ramos Abraham Luis | HU-010 | Realizó la HU-010 |
| Espinoza Tiza Yago Imanol | HT-07 | Apoyo en la HU-011 |

Los commits se hacen desde una sola cuenta de GitHub para agilizar la integración; el historial de Git por sí solo no muestra la autoría de cada integrante.

---

[← Volver al README Principal](../../../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-10-05 | Versión inicial: estructura de la retrospectiva y seguimiento de las acciones heredadas del Sprint 1 | Inciso Aguilar Elizabeth Antonela |
| V_1_1_0 | 2026-10-06 | Se completan lo aprendido, lo que va bien y lo que se puede mejorar; se actualiza el estado de las acciones heredadas, se proponen acciones para el Sprint 3 y se agrega el aporte por integrante | Inciso Aguilar Elizabeth Antonela |
| V_1_2_0 | 2026-10-06 | Se precisa que las revisiones cruzadas son presenciales y se ajusta la acción propuesta para dejar constancia en GitHub | Inciso Aguilar Elizabeth Antonela |
| V_1_3_0 | 2026-10-06 | Se registra la primera aprobación en GitHub (Pull Request #45) y se ajusta la acción propuesta | Inciso Aguilar Elizabeth Antonela |
