# 03 Registro de Riesgos

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

## 1. Metodología de Evaluación de Riesgos

La evaluación de riesgos del proyecto RouteZero sigue los estándares **PMBOK 7ª Edición** y **CMMI-DEV**, aplicando la fórmula de severidad cuantitativa:

**Severidad (Exposición) = Probabilidad (1–5) × Impacto (1–5)**

| Rango de Severidad | Nivel | Color |
|---|---|---|
| 1 – 6 | Bajo (Low) | 🟢 |
| 8 – 12 | Medio (Medium) | 🟡 |
| 15 – 25 | Alto (High) | 🔴 |

**Escala de Probabilidad:**
| Valor | Descripción |
|---|---|
| 1 | Muy baja — poco probable que ocurra |
| 2 | Baja — podría ocurrir en circunstancias excepcionales |
| 3 | Media — podría ocurrir en algún momento |
| 4 | Alta — probable que ocurra |
| 5 | Muy alta — casi certeza de que ocurrirá |

**Escala de Impacto:**
| Valor | Descripción |
|---|---|
| 1 | Insignificante — sin efecto en el proyecto |
| 2 | Menor — efecto mínimo gestionable |
| 3 | Moderado — efecto notable pero recuperable |
| 4 | Mayor — efecto significativo en tiempo/costo/calidad |
| 5 | Catastrófico — compromete la viabilidad del proyecto |

---

## 2. Matriz de Evaluación de Riesgos

| ID | Descripción del Riesgo | Categoría | Prob. | Imp. | Severidad | Plan de Mitigación (Preventivo) | Plan de Contingencia (Reactivo) | Responsable |
|---|---|---|---|---|---|---|---|---|
| RSK-001 | Complejidad del algoritmo ACO mayor a la estimada, impidiendo cumplir el umbral de ≤ 45 segundos para 150 pedidos | Técnica | 4 | 5 | 🔴 20 (Alto) | Iniciar con una implementación simplificada del ACO desde el Sprint 1 y realizar pruebas de rendimiento incrementales en cada sprint | Reducir el tamaño del problema de prueba (menos pedidos) y ajustar los parámetros del ACO (número de hormigas, iteraciones) para cumplir el SLA | Espinoza Tiza Yago Imanol |
| RSK-002 | Indisponibilidad o límites de cuota en los servicios gratuitos de Render o Vercel durante la sustentación | Técnica / Infraestructura | 3 | 4 | 🟡 12 (Medio) | Monitorear el consumo de cuotas semanalmente e implementar alertas al 70% del límite gratuito | Migrar temporalmente el backend a Railway o el frontend a Netlify como alternativa gratuita de respaldo | Guerra Lozano Keen |
| RSK-003 | Precisión limitada de datos georreferenciados de OpenStreetMap para el distrito de Huancayo | Técnica / Datos | 3 | 3 | 🟡 9 (Medio) | Validar manualmente los puntos críticos del distrito de Huancayo (Mercado Modelo, Mercado Mayorista, Parque Industrial El Tambo) durante el Sprint 1 | Permitir la carga manual de coordenadas GPS corregidas por el operador desde el módulo de pedidos | Espinoza Tiza Yago Imanol |
| RSK-004 | Cambios en los requisitos por retroalimentación del docente durante el ciclo académico | Gestión | 4 | 3 | 🟡 12 (Medio) | Documentar todos los requisitos con versionado semántico y mantener el registro de control de cambios actualizado en cada sprint | Aplicar el proceso de control de cambios: actualizar el documento afectado incrementando su versión (V_1_1_0) y registrar el cambio en el historial | Inciso Aguilar Elizabeth Antonela |
| RSK-005 | Disponibilidad limitada de algún integrante del equipo por carga académica de otras asignaturas | Recursos Humanos | 3 | 3 | 🟡 9 (Medio) | Distribuir responsabilidades claramente por módulo y mantener documentación técnica actualizada para facilitar la transferencia de conocimiento | Reasignar temporalmente las tareas del integrante ausente al resto del equipo priorizando las HU de mayor valor del sprint | Inciso Aguilar Elizabeth Antonela |
| RSK-006 | Vulnerabilidades de seguridad detectadas tardíamente en la API FastAPI que incumplan OWASP Top 10 | Seguridad | 2 | 4 | 🟡 8 (Medio) | Implementar HT-02 (autenticación JWT + OWASP) desde el Sprint 1 y ejecutar análisis estático con CodeQL en cada Pull Request | Aplicar parches de seguridad de forma inmediata, documentar la vulnerabilidad en el registro de bugs de Jira y re-ejecutar las pruebas de seguridad | Guerra Lozano Keen |
| RSK-007 | Incumplimiento del estándar WCAG 2.1 AA en la interfaz del modo conductor | Calidad / Accesibilidad | 2 | 3 | 🟢 6 (Bajo) | Ejecutar auditorías de accesibilidad con Google Lighthouse desde el Sprint 2 y corregir issues en cada sprint | Priorizar la corrección de los criterios WCAG críticos (contraste de color, etiquetas ARIA) antes de la sustentación final | Uscuvilca Ramos Abraham Luis |
| RSK-008 | Conflictos de integración en el repositorio GitHub por commits simultáneos de los integrantes | Técnica / Gestión | 3 | 2 | 🟢 6 (Bajo) | Aplicar Feature Branch Workflow estrictamente: cada integrante trabaja en su rama propia e integra via Pull Request con revisión de al menos un par | Resolver los conflictos de merge manualmente con revisión del arquitecto de software antes de aprobar el Pull Request | Inciso Aguilar Elizabeth Antonela |
| RSK-009 | Incumplimiento de la Ley N° 29733 por almacenamiento inadecuado de datos personales de conductores | Normativa / Legal | 2 | 5 | 🔴 10 (Medio) | Implementar HT-07 (cifrado AES-256 en reposo) desde el Sprint 1 y revisar el cumplimiento normativo en cada sprint | Auditar inmediatamente los datos almacenados, aplicar cifrado retroactivo y documentar el incidente en el registro de auditoría del sistema | Inciso Aguilar Elizabeth Antonela |
| RSK-010 | Rendimiento insuficiente de PostgreSQL en Render (plan gratuito) con volumen alto de pedidos | Técnica / Infraestructura | 3 | 3 | 🟡 9 (Medio) | Implementar HT-06 (optimización de consultas SQL con índices) desde el Sprint 2 y ejecutar pruebas de carga con datos simulados | Reducir el volumen de datos de prueba para la sustentación y documentar las métricas de rendimiento obtenidas con el plan gratuito | Guerra Lozano Keen |
| RSK-011 | Conectividad a internet inestable en el distrito de Huancayo afectando el uso del sistema en campo | Operativa / Contexto | 4 | 3 | 🟡 12 (Medio) | Diseñar la interfaz del modo conductor con carga mínima de datos y optimizar las peticiones API para funcionar con conexiones lentas (2G/3G) | Implementar caché local en el navegador para que el conductor pueda ver su ruta asignada sin conexión activa durante la jornada | Uscuvilca Ramos Abraham Luis |
| RSK-012 | Pérdida del repositorio GitHub o corrupción del historial de commits por errores de manejo de Git | Técnica / Gestión | 1 | 5 | 🟢 5 (Bajo) | Mantener el repositorio público y accesible en todo momento, con al menos 2 integrantes con acceso de administrador y backups locales semanales | Restaurar el repositorio desde el último estado conocido usando el historial de commits y las copias locales de cada integrante | Inciso Aguilar Elizabeth Antonela |

---

## 3. Resumen de Exposición al Riesgo

| Nivel | Cantidad | Riesgos |
|---|---|---|
| 🔴 Alto (15–25) | 1 | RSK-001 |
| 🟡 Medio (8–12) | 8 | RSK-002, RSK-003, RSK-004, RSK-005, RSK-006, RSK-009, RSK-010, RSK-011 |
| 🟢 Bajo (1–6) | 3 | RSK-007, RSK-008, RSK-012 |

---

## 4. Mapa de Calor de Riesgos

| Probabilidad \ Impacto | 1 Insignificante | 2 Menor | 3 Moderado | 4 Mayor | 5 Catastrófico |
|---|---|---|---|---|---|
| **5 Muy alta** | | | | | |
| **4 Alta** | | | RSK-004, RSK-011 | | RSK-001 |
| **3 Media** | | | RSK-003, RSK-005, RSK-010 | RSK-002 | |
| **2 Baja** | | | RSK-007 | RSK-006 | RSK-009 |
| **1 Muy baja** | | | | | RSK-012 |

---

[← Volver al README Principal](../../README.md)