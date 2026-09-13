# 04 Presupuesto del Proyecto

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Fecha** | 2026-09-10 |
| **Versión** | 1.0.0 |

[← Volver al README Principal](../../README.md)

---

## 1. Supuestos del Presupuesto

- El proyecto tiene una duración de **14 semanas académicas** con dedicación parcial del equipo.
- Las tarifas de recursos humanos se expresan en **USD** según tarifas referenciales del mercado peruano de desarrollo de software.
- La infraestructura cloud utiliza **planes gratuitos** durante el ciclo académico (Render, Vercel).
- El presupuesto refleja el **costo real estimado** si el proyecto fuera ejecutado en un contexto profesional.
- La reserva de contingencia es del **12%** del subtotal, derivada de la evaluación de riesgos del Artefacto 3.
- Tipo de cambio referencial: **1 USD = S/ 3.75**.

---

## 2. Costo de Recursos Humanos (CAPEX)

| Rol | Integrante | Horas Asignadas | Tarifa/Hora (USD) | Costo Total (USD) |
|---|---|---|---|---|
| Arquitecta de Software / Project Manager | Inciso Aguilar Elizabeth Antonela | 120 hrs | $25 | $3,000.00 |
| Ingeniero de IA e Integración | Espinoza Tiza Yago Imanol | 100 hrs | $22 | $2,200.00 |
| Desarrollador Backend | Guerra Lozano Keen | 100 hrs | $20 | $2,000.00 |
| Desarrollador Frontend | Uscuvilca Ramos Abraham Luis | 100 hrs | $20 | $2,000.00 |
| **Subtotal RRHH** | | **420 hrs** | | **$9,200.00** |

> Las tarifas referenciales corresponden al rango de desarrolladores junior-mid en Perú (S/ 25–50/hora según la consigna del proyecto, convertido a USD).

---

## 3. Costo de Licenciamiento y Herramientas

| Herramienta / Licencia | Tipo | Costo Mensual (USD) | Meses | Costo Total (USD) |
|---|---|---|---|---|
| Atlassian Jira Software | Plan gratuito (hasta 10 usuarios) | $0.00 | 4 | $0.00 |
| Figma | Plan gratuito (Starter) | $0.00 | 4 | $0.00 |
| GitHub | Plan gratuito (repositorio público) | $0.00 | 4 | $0.00 |
| Visual Studio Code | Gratuito | $0.00 | 4 | $0.00 |
| SonarQube Community | Plan gratuito (autohospedado) | $0.00 | 4 | $0.00 |
| Postman | Plan gratuito | $0.00 | 4 | $0.00 |
| Google Lighthouse | Gratuito (extensión Chrome) | $0.00 | 4 | $0.00 |
| **Subtotal Licenciamiento** | | | | **$0.00** |

> El equipo priorizó herramientas open source y planes gratuitos alineados con los principios Green Software y el presupuesto académico del proyecto.

---

## 4. Costo de Infraestructura Cloud y Servicios (OPEX)

| Servicio | Proveedor | Plan | Costo Mensual (USD) | Meses | Costo Total (USD) |
|---|---|---|---|---|---|
| Hosting Backend (FastAPI) | Render | Plan gratuito | $0.00 | 4 | $0.00 |
| Base de datos PostgreSQL | Render | Plan gratuito (90 días) | $0.00 | 3 | $0.00 |
| Hosting Frontend (React.js) | Vercel | Plan gratuito (Hobby) | $0.00 | 4 | $0.00 |
| Mapas y georreferenciación | OpenStreetMap | Gratuito / Open source | $0.00 | 4 | $0.00 |
| Dominio personalizado | — | No requerido para MVP | $0.00 | — | $0.00 |
| Certificado SSL | Render / Vercel | Incluido en plan gratuito | $0.00 | 4 | $0.00 |
| CI/CD Pipeline | GitHub Actions | Plan gratuito (2,000 min/mes) | $0.00 | 4 | $0.00 |
| **Subtotal Cloud (OPEX)** | | | | | **$0.00** |

> Para un entorno de producción real, los costos de infraestructura se estiman en USD $500/mes (AWS/GCP/Azure) según la consigna del proyecto.

---

## 5. Tabla Resumen Financiera

| Categoría | Costo Subtotal (USD) | Porcentaje del Total |
|---|---|---|
| 1. Recursos Humanos (CAPEX) | $9,200.00 | 100.0% |
| 2. Licenciamiento de Software | $0.00 | 0.0% |
| 3. Infraestructura Cloud (OPEX) | $0.00 | 0.0% |
| **SUBTOTAL DEL PROYECTO** | **$9,200.00** | **100.0%** |
| 4. Reserva de Contingencia (12%) | $1,104.00 | N/A |
| **PRESUPUESTO TOTAL ESTIMADO** | **$10,304.00** | **100.0%** |

> Equivalente en soles: **S/ 38,640.00** (tipo de cambio referencial: 1 USD = S/ 3.75)

---

## 6. Costo de Producción Estimado (Referencial)

Este presupuesto refleja el costo académico del MVP. Para un entorno de producción real con Andina Reparto S.A.C., los costos estimados serían:

| Categoría | Costo Estimado Producción (USD/mes) |
|---|---|
| Infraestructura cloud (AWS/GCP/Azure) | $500.00 |
| Mantenimiento y soporte del sistema | $1,000.00 |
| Actualizaciones y mejoras continuas | $500.00 |
| **Total operativo mensual** | **$2,000.00** |
| **Costo operativo anual** | **$24,000.00** |

> El costo total del ciclo de vida del software (LCC) a 3 años en producción se estima en **$81,200.00 USD** (desarrollo MVP + 3 años de operación), alineado con el análisis de restricciones del documento `13. Restricciones V_1_0_0.md`.

Este análisis permite visualizar el impacto económico real del sistema RouteZero más allá del contexto académico. Comprender el costo del ciclo de vida del software (LCC — Life Cycle Cost) es fundamental para que Andina Reparto S.A.C. pueda tomar decisiones informadas sobre la viabilidad y sostenibilidad del sistema a largo plazo. El LCC abarca desde la concepción del sistema hasta su eventual retiro, incluyendo el desarrollo inicial, la operación continua y el mantenimiento evolutivo. Los valores estimados se derivan del análisis de restricciones económicas y tecnológicas documentado en `13. Restricciones V_1_0_0.md`, considerando los costos referenciales de infraestructura cloud (USD $500/mes) y los compromisos normativos vigentes (Ley N° 29733, DS 033-2012-MTC, ISO/IEC 25010).

---

[← Volver al README Principal](../../README.md)