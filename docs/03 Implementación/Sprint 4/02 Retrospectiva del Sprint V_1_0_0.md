# Retrospectiva del sprint

[← Volver al README principal](../../../README.md)

**Nombre del Proyecto:** RouteZero — Optimizador de rutas sostenibles (empresa ficticia Andina Reparto S.A.C., Huancayo)

**Líder del Proyecto:** Inciso Aguilar Elizabeth Antonela

## ¿Qué aprendimos?

- **Los datos de prueba chicos esconden los problemas de rendimiento.** Con las tablas casi vacías toda consulta parece rápida. Cargar seis meses de operación en una transacción que se deshace mostró dos mejoras reales: el listado de pedidos ordenaba todo sin un índice (7.0 a 0.1 ms) y el dashboard y el reporte contaban las paradas de todo el historial en vez de las del periodo (6.6 a 3.1 ms).
- **Un PDF se prueba leyéndolo de vuelta.** Las pruebas extraen el texto del archivo generado y se revisó una captura de sus páginas: así se vio, por ejemplo, que la primera versión no llevaba tildes aunque el formato las admite.
- **El tiempo de Render no está donde se supone.** El dashboard tarda lo mismo con 15 que con 450 rutas porque casi todo es la ida y vuelta a la base. El monitoreo de producción con Playwright lo confirmó: con el servicio despierto, `/api/health` responde en unos 200 ms, pero la primera petición tras un periodo inactivo tardó 51.7 s por el arranque en frío del plan gratuito.
- **Un mismo código puede comportarse distinto según el navegador.** Al correr la suite de extremo a extremo en Chromium, Firefox y WebKit apareció una diferencia real: Safari no pasa el foco a los enlaces con la tecla Tab, así que la prueba del enlace «Saltar al contenido» no se puede verificar con teclado en WebKit. Se documentó como una limitación del motor y no se tapó.
- **Las pruebas de resiliencia obligan a pensar en lo que ve la persona cuando algo falla.** Simular una red caída o un error 500 comprobó que el inicio de sesión y la vista del conductor avisan con un mensaje y permiten reintentar, en vez de quedarse cargando.
- **Un despliegue automático debe esperar a las pruebas.** La integración nativa de Render y Vercel despliega aunque las pruebas fallen. Pasar el despliegue a un workflow que solo actúa cuando `ci.yml` y `tests.yml` terminan en verde, con los accesos guardados como Secrets de GitHub, cambia eso.
- **Lo que no tiene datos reales se declara como supuesto y se deja configurable** (precio del combustible, meta de CO₂, árboles por tonelada), la misma lección de las horas punta del Sprint 3.
- **La mayor debilidad percibida no es la complejidad sino la curva de entrada.** La escala SUS dio 73.8 (B-) y el sistema se percibe fácil, consistente y confiable, pero los ítems sobre necesitar ayuda y aprender antes de usarlo fueron los más bajos (1.4 de 4 cada uno), y 8 de 10 comentarios piden una explicación inicial.
- **Verificar el estado de git antes de abrir el Pull Request.** Una corrección hecha después de los commits quedó fuera del Pull Request #62 y hubo que publicarla en uno posterior.

## ¿Qué estamos haciendo bien?

- Los 18 Story Points del sprint se completaron el día 2 de 23, con cada funcionalidad medida en Render desde el primer día y no solo en local.
- La calidad es verificable y repetible: integración continua en verde, 359 pruebas del backend con 98 % de cobertura (100 % en el módulo nuevo), 99 de Vitest, la suite de Playwright en tres navegadores, Lighthouse en 100 en accesibilidad, buenas prácticas y SEO, y W3C sin errores.
- El módulo nuevo respeta la independencia entre módulos (la prueba de arquitectura lo vigila) y cada endpoint nuevo está restringido al rol de administrador.
- El Pull Request #64 fue aprobado por dos compañeros antes del merge, con los pasos de revisión escritos para quien revisa.
- Las mediciones se pueden repetir con un comando: la auditoría de consultas (`scripts/auditar_consultas.py`), el monitoreo de producción (`npm run monitorear`) y el cálculo de la escala SUS (`scripts/usabilidad/procesar_sus.py`), con pruebas propias.
- Se probó el sistema con personas reales de los tres roles (administración, operación y conducción) y no solo con pruebas automáticas.

## ¿Qué podemos hacer mejor?

### Personas

El trabajo sigue concentrándose en pocas personas (IMP-005, abierto): la construcción la lleva casi toda la líder, mientras que el resto del equipo aporta como tester. Conviene que cada integrante deje evidencia de su aporte en el repositorio y en la documentación, y que las pruebas de aceptación las haga un integrante distinto de quien implementó la historia.

### Relaciones

Los Pull Request #62 y #63 se fusionaron sin la aprobación de un compañero; recién el #64 la tuvo (IMP-025). Pedirla antes de cada merge y no después. Además, validar con la empresa los supuestos de sostenibilidad antes de presentarlos como cifras de la operación.

### Procesos

Planificar las pruebas de usabilidad con más anticipación: se concentraron en los días previos a la inspección, con poco margen para analizar los resultados y aplicar mejoras. Cargar los datos reales de la flota antes de la sustentación, y usar cuentas temporales y no las de prueba permanentes cuando participen personas ajenas al equipo, porque el repositorio es público.

### Herramientas

El plan gratuito de Render (CPU limitada, unos 2 s por petición y arranque en frío de hasta 50 s) sigue condicionando el rendimiento (IMP-013, IMP-016, IMP-019 e IMP-026). Las pruebas de integración del backend usan la base real de Supabase y por eso no corren en GitHub Actions (fase 2 pendiente).

### Acciones a realizar

| # | Acción | Responsable | Plazo y métrica de seguimiento |
|---|---|---|---|
| 1 | Pedir en GitHub la aprobación de un compañero en cada Pull Request antes del merge | Equipo | Desde el próximo Pull Request; meta: 100 % de los PR con aprobación registrada |
| 2 | Cargar el precio de compra y la vida útil de los vehículos reales y validar con la empresa los tres supuestos de sostenibilidad | Inciso Aguilar Elizabeth Antonela | Antes de la sustentación final (semana 16); meta: 0 vehículos «sin dato» en el reporte PDF |
| 3 | Reutilizar las matrices de distancia y tiempo entre peticiones, o resolverlas con una sola pasada de Dijkstra, para bajar el tiempo de generar y re-optimizar rutas en Render (IMP-019) | Inciso Aguilar Elizabeth Antonela | Antes de la sustentación; meta: generar 150 pedidos y 15 vehículos en menos de 30 s en Render (hoy 30 s) |
| 4 | **Guía de primeros pasos con preguntas frecuentes: aplicada el 17-11-2026.** Falta volver a aplicar la escala SUS para medir su efecto | Inciso Aguilar Elizabeth Antonela | Antes de la sustentación; meta: promedio igual o mayor a 73.8, ningún participante bajo 68 y contribución media de los ítems P4 y P10 de al menos 2.0 (hoy 1.4) |
| 5 | Escribir el checklist de políticas RLS y evaluar llevar las pruebas del backend a la integración continua con una base de pruebas dedicada | Guerra Lozano Keen | Antes de la sustentación; meta: checklist publicado y una decisión documentada sobre la fase 2 |
| 6 | Calibrar los factores de hora punta con datos reales o con un criterio documentado | Equipo | Antes de la sustentación; meta: factores con fuente citada |
| 7 | Cerrar las brechas de seguridad pendientes del plan de OWASP: `Content-Security-Policy`, bloqueo de `requirements.txt` con sumas de verificación y MFA obligatorio para el administrador | Uscuvilca Ramos Abraham Luis | Antes de la sustentación; meta: 0 brechas abiertas en el documento de OWASP |

Los responsables son una propuesta que se confirma en la reunión de retrospectiva con el equipo.

## Aporte por integrante

La columna «Asignación en Jira» es el dato objetivo del tablero. La columna «Aporte declarado por el equipo» recoge lo que informó la líder del proyecto; no se estima ni se reparte un porcentaje.

| Integrante | Asignación en Jira (Sprint 4) | Aporte declarado por el equipo |
|---|---|---|
| Inciso Aguilar Elizabeth Antonela | Sin ítems propios en el tablero; trabajó junto con Yago en HU-015, HU-016, HU-017 y HT-12 | Construcción de HU-015, HU-016, HU-017, HT-11 y HT-12: el módulo de sostenibilidad, el reporte PDF, el costo del ciclo de vida de la flota, la auditoría y optimización de consultas, las pruebas y las migraciones; mediciones en Render; documentación del sprint |
| Espinoza Tiza Yago Imanol | HU-015, HU-016, HU-017, HT-12 | Pruebas del sistema como tester. Aprobó el Pull Request #64 en GitHub |
| Uscuvilca Ramos Abraham Luis | Sin ítems propios en el tablero; trabajó junto con Keen en HT-11 | Pruebas del sistema como tester |
| Guerra Lozano Keen | HT-11 | Pruebas del sistema como tester. Aprobó el Pull Request #64 en GitHub |

## Metadatos del documento

| Campo | Detalle |
|---|---|
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Sprint** | Sprint 4 — Sostenibilidad y Cierre (22-10-2026 – 13-11-2026) |
| **Fecha de la retrospectiva** | Inspección 05, viernes 20-11-2026 |
| **Versión** | 1.0.0 |

---

[← Volver al README principal](../../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-11-17 | Primera versión con la numeración y la plantilla de la consigna de la Inspección 05. Continúa el contenido de `04 Retrospectiva del Sprint` V_1_1_0 (versiones anteriores en [`historial Sprint 4`](historial%20Sprint%204/)): se agregan lo aprendido en la inspección (navegadores, resiliencia, despliegue y monitoreo), las cuatro áreas de mejora (personas, relaciones, procesos y herramientas) y una tabla de acciones con responsable, plazo y métrica; el aporte por integrante pasa a una sección final | Inciso Aguilar Elizabeth Antonela |
| V_1_0_0 (ajuste) | 2026-11-17 | Se ajustan la acción de usabilidad (meta con los resultados reales de la escala SUS) y lo aprendido | Inciso Aguilar Elizabeth Antonela |
| V_1_0_0 (ajuste) | 2026-11-17 | La acción de usabilidad pasa a «aplicada»: queda pendiente volver a medir con la escala SUS | Inciso Aguilar Elizabeth Antonela |
