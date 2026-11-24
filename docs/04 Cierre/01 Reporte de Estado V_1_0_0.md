# 01 Reporte de Estado del Proyecto (Status Report)

[← Volver al README Principal](../../README.md)

## Metadatos

| Campo | Detalle |
|---|---|
| **Proyecto** | RouteZero — Optimizador de rutas sostenibles (empresa ficticia Andina Reparto S.A.C., Huancayo) |
| **Líder del Proyecto** | Inciso Aguilar Elizabeth Antonela |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Periodo reportado** | 14-11-2026 a 29-11-2026 (desde el cierre del periodo del [`05 Informe de estado del proyecto`](../03%20Implementaci%C3%B3n/Sprint%204/Plan%20y%20documentos%20t%C3%A9cnicos/05%20Informe%20de%20estado%20del%20proyecto%20V_1_2_0.md) del Sprint 4, que llegó hasta el 13-11-2026) |
| **Fecha de Corte** | 2026-11-30 (cierre de la semana 15) |
| **Fecha de elaboración** | 2026-11-24. Lo correspondiente a la semana 15 es una proyección que se confirma el 30-11-2026 |
| **Estado general** | **VERDE** en la línea base (completa); **ÁMBAR** en el cierre final (margen de costo de $80 y tres semanas de trabajo documental concentradas en la semana 16) |
| **Versión** | 1.0.0 |

---

## 1. Información de Alcance

- **Logros completados.** La línea base de 14 semanas está completa: los 127 Story Points de los cuatro sprints (aceptados el 23-10), más la actividad de cierre y validación. En este periodo se completó lo que faltaba de esa actividad para la Inspección 05 (20-11-2026):
  - **Playwright** en tres navegadores (Chromium, Firefox y WebKit): 120 casos, 119 aprobados y 1 omitido en WebKit, con pruebas de resiliencia y monitoreo de producción.
  - **Escala SUS** aplicada a 10 participantes: 73.8 (grado B-), con la **guía de primeros pasos y preguntas frecuentes** aplicada el 17-11 como mejora derivada.
  - **Integración y despliegue continuos:** flujos de GitHub Actions de calidad, pruebas, despliegue a producción y auditoría Green IT.
  - **Documentación:** revisión y retrospectiva del Sprint 4, análisis de Playwright, usabilidad, y estructura de la carpeta del sprint según la consigna.
- **Cambios al alcance.** Se registra el cambio **CR-01: cierre final del proyecto**, que agrega siete reportes de cierre (en `docs/04 Cierre`), un video de unos 5 minutos (en `docs/05 Video proyecto`), la actualización de documentos previos y la sustentación del 04-12-2026. No estaba en la línea base de 14 semanas, que **no se modificó**. También se incorporó la guía de primeros pasos, mejora menor derivada del SUS.
- **Información de calidad (defectos o incidentes detectados).** 1 caso de Playwright omitido en WebKit por una limitación del motor (Safari no pasa el foco con la tecla Tab). Tres impedimentos nuevos registrados el 17-11: arranque en frío de Render de 51.7 s (IMP-027), despliegue automático que no esperaba a las pruebas (IMP-028) y una vulnerabilidad alta en `picomatch` sin versión corregida, solo en herramientas de desarrollo (IMP-029).

## 2. Información de Cronograma

- **Actividades o hitos planificados pero no completados.** (1) Los entregables del cierre final (CR-01), en elaboración. (2) Mejoras opcionales surgidas de la retrospectiva del Sprint 4, que quedan para una siguiente etapa (ver [`06 Reporte Final del Proyecto`](06%20Reporte%20Final%20del%20Proyecto%20V_1_0_0.md)).
- **Causa raíz de las desviaciones.** La prioridad de las dos últimas semanas fue la Inspección 05 y el cierre documental; las acciones de mejora técnica quedaron por detrás y dependen de pocas personas (IMP-005).
- **Impacto en próximos hitos o en la ruta crítica.** Ninguno en la línea base. El hito siguiente es la sustentación del **04-12-2026**: la ruta crítica del cierre final es **video, demostración y capturas de Jira**, porque dependen de la grabación y de sacar las imágenes una por una.
- **Acciones correctivas o preventivas planificadas.** Terminar los siete documentos y el README la semana 15; reservar la semana 16 para capturas, video, revisión de enlaces y ensayo de la demostración (10 minutos); calentar Render antes de ensayar y de exponer, por el arranque en frío.

## 3. Información de Costos

- **Fondos ejecutados en este periodo (14-11 a 29-11, 16 días).** **$1,460.57**: $821.57 de la línea base (14-11 a 22-11) y $639.00 del CR-01 (semana 15, proyectada). Calculado con las horas semanales declaradas (8.2 h la líder y 7 h cada uno de los otros tres) a las tarifas del presupuesto. Acumulado a la fecha de corte: **$9,585.00**, el 93.0 % del BAC de $10,304.00.
- **Causa raíz de la variación (mano de obra, materiales o estimaciones).** Sin variación negativa: la mano de obra quedó por debajo de las horas presupuestadas y la infraestructura sigue en planes gratuitos (OPEX $0.00). Las horas son una **estimación declarada, no un registro de tiempo**.
- **Impacto en el presupuesto general o reserva de contingencia.** La línea base cerró con $8,946.00 (CV +$1,358.00). La reserva de $1,104.00 no se usó. Con el cierre final la proyección es **$10,224.00 (EAC)**, es decir, **$80.00 por debajo del BAC**. Ver [`03 Reporte de Análisis de Valor Ganado - EVM`](03%20Reporte%20de%20An%C3%A1lisis%20de%20Valor%20Ganado%20-%20EVM%20V_1_0_0.md).
- **Acciones correctivas o preventivas planificadas.** Contar las horas de la semana 16 y vigilar el margen: unas 3.2 horas adicionales de la líder (o 4 de otro integrante) lo agotarían. Si se superara el BAC, se declara en el reporte final.

## 4. Proyección (Look Ahead)

- **Logros y entregables planificados para el próximo periodo (semana 16, 30-11 a 06-12).**
  - Los siete documentos de `docs/04 Cierre`, enlaces de ida y vuelta con el README y verificación de enlaces.
  - Capturas reales de Jira (burndown, burnup, tablero y flujo acumulado), mini encuesta de satisfacción del equipo y tablero de retrospectiva.
  - Video de unos 5 minutos en `docs/05 Video proyecto` (1 minuto de presentación y 4 de demostración).
  - Actualización y versionado de documentos previos con inconsistencias (por ejemplo, la revisión del Sprint 2 frente a Jira).
  - Sustentación del 04-12-2026, de 15:00 a 15:20.
- **Costos planificados para el próximo periodo.** **$639.00** (semana 16), con las mismas horas declaradas.

## 5. Riesgos, Incidentes y Comentarios

- **Nuevos riesgos identificados.**
  - Margen de costo de solo $80 en el cierre final.
  - Un video de 5 minutos puede superar el límite de 100 MB por archivo de GitHub, por lo que hay que comprimirlo antes de subirlo.
  - Arranque en frío de Render durante la demostración (IMP-027): hay que calentarlo antes de exponer.
  - Concentración del trabajo en pocas personas (IMP-005), que se extiende a la redacción del cierre.
- **Nuevos incidentes (issues) surgidos.** IMP-027, IMP-028 e IMP-029 (ver arriba), todos del 17-11 y abiertos. IMP-028 se cierra al apagar el despliegue nativo de Render y Vercel después de comprobar el flujo de despliegue; IMP-029, cuando `picomatch` publique una versión corregida.
- **Comentarios relevantes.** Jira registra las historias terminadas en bloque al cerrar cada sprint, así que sus gráficos muestran el avance en escalón; el avance real está en el historial de git y en los planes de ejecución. La escala SUS mostró que la mayor debilidad percibida es la curva de entrada, no la complejidad, y la guía de primeros pasos es la respuesta aplicada.

---

[← Volver al README Principal](../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-11-24 | Versión inicial: estado del periodo 14-11-2026 a 29-11-2026, con la línea base completa, el cierre final CR-01 y la proyección de la semana 16 | Inciso Aguilar Elizabeth Antonela |
