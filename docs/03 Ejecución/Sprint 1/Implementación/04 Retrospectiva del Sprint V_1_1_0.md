# 04 Retrospectiva del Sprint

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Líder del Proyecto** | Inciso Aguilar Elizabeth Antonela |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Sprint** | Sprint 1 — Base del sistema (19-09-2026 – 02-10-2026) |
| **Fecha de la retrospectiva** | 2026-10-02 |
| **Versión** | 1.1.0 |

[← Volver al README Principal](../../../../README.md)

---

## ¿Qué aprendimos?

- Las migraciones de Supabase necesitan revisarse contra **RLS automático**: al activar "Enable automatic RLS" toda tabla nueva queda protegida, incluso las de referencia sin dato por usuario, y si no recibe una política queda inaccesible en silencio (0 filas, sin error). Esto costó tiempo de depuración que se habría evitado revisando la configuración de RLS como parte del checklist de cada tabla nueva.
- Las diferencias de entorno entre desarrollo local y el proveedor de despliegue (Render) pueden introducir bugs invisibles en local: fijar `sqlalchemy>=2.0` sin tope superior permitió que Render resolviera un driver de PostgreSQL distinto al usado en desarrollo, lo que solo se detectó al desplegar, un día antes de la inspección.
- Documentar las decisiones técnicas y los bugs reales a medida que aparecen (como se hizo en `design.md` del cambio OpenSpec `add-mfa-sesiones`) permitió cerrar el sprint sin perder el porqué de cada corrección, algo que habría sido difícil de reconstruir de memoria al final.

## ¿Qué estamos haciendo bien?

- El sprint se cerró al 100 % de su alcance comprometido (42/42 Story Points) un día antes de la fecha de inspección.
- Cobertura de pruebas alta y real en el backend (95 % combinado, 65 pruebas con pytest), no solo pruebas manuales.
- Despliegue real verificado de extremo a extremo (backend en Render, frontend en Vercel, login y CORS probados contra el origen de producción), en vez de demostrar el sistema solo en local.
- Los bugs encontrados durante el sprint se corrigieron el mismo día que aparecieron, sin dejarlos acumularse para el cierre.

## ¿Qué podemos hacer mejor?

### Personas

La implementación técnica del Sprint 1 (backend y frontend) se concentró casi por completo en un solo integrante del equipo (ver IMP-005 del [`02 Registro de Impedimentos`](02%20Registro%20de%20Impedimentos%20V_1_1_0.md)), mientras el resto no tomó módulos propios del sprint pese a estar asignados como responsables de riesgos específicos en el [`03 Registro de riesgos`](../../../02%20Planificaci%C3%B3n/03%20Registro%20de%20riesgos%20V_1_0_0.md). El resto del equipo sí aportó durante el sprint desde otro rol: revisando el sistema en distintos momentos y avisando por chat errores que encontraban al probarlo, varios de los cuales se priorizaron junto con los detectados internamente. Esto ayudó a destapar bugs reales antes del cierre, pero no reemplaza tener un dueño por módulo — es un riesgo real para sprints con mayor complejidad técnica, como el motor de optimización ACO del Sprint 2.

### Relaciones

Falta un punto de sincronización intermedio dentro del sprint (a mitad de camino, no solo en el cierre) donde cada integrante reporte explícitamente su avance o su bloqueo, en vez de que la carga se reasigne recién cuando el sprint ya está por cerrarse.

### Procesos

El Sprint 1 no tuvo una re-planificación formal a mitad de sprint pese a que el plan de cierre (sección 5 de `01 Sprint 1 Plan de ejecución y estado`) tuvo que ajustarse varias veces de forma reactiva. Conviene incorporar un checkpoint formal de medio sprint.

### Herramientas

El pipeline de CI/CD (GitHub Actions) sigue sin ejecutar automáticamente las pruebas ni el análisis estático en cada Pull Request; por ahora ambos se corrieron manualmente antes de cada merge, lo que funciona pero no escala bien a medida que el equipo haga más commits en paralelo.

### Acciones a realizar

| # | Acción | Responsable | Para cuándo |
|---|---|---|---|
| 1 | Redistribuir explícitamente los módulos del Sprint 2 (motor de optimización, conductores) entre todos los integrantes desde el Sprint Planning, con un dueño por módulo | Inciso Aguilar Elizabeth Antonela | Inicio del Sprint 2 |
| 2 | Establecer un checkpoint de medio sprint con reporte de avance individual | Inciso Aguilar Elizabeth Antonela | Sprint 2 |
| 3 | Configurar GitHub Actions para correr pytest, Bandit/pip-audit y npm audit automáticamente en cada Pull Request | Guerra Lozano Keen | Sprint 2 |
| 4 | Agregar un checklist de revisión de políticas RLS a la definición de "terminado" de cualquier tarea que cree una tabla nueva en Supabase | Guerra Lozano Keen | Sprint 2 |
| 5 | Fijar un tope superior de versión en `requirements.txt` para evitar que una dependencia nueva cambie de comportamiento entre entornos sin aviso | Inciso Aguilar Elizabeth Antonela | Sprint 2 |

---

[← Volver al README Principal](../../../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-10-02 | Versión inicial: retrospectiva del Sprint 1 con aprendizajes, aciertos, oportunidades de mejora por eje y plan de acción para el Sprint 2 | Inciso Aguilar Elizabeth Antonela |
| V_1_1_0 | 2026-10-02 | Se precisa la sección "Personas": el resto del equipo sí participó durante el sprint revisando el sistema y reportando errores por chat, aunque no tomó módulos propios de implementación | Inciso Aguilar Elizabeth Antonela |
