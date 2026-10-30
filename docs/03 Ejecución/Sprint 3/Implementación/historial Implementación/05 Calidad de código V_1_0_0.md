# 05 Evaluación de Calidad de Código — SonarQube

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Líder del Proyecto** | Inciso Aguilar Elizabeth Antonela |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Sprint** | Sprint 3 — Rutas y Visualización (Inspección 03) |
| **Fecha de análisis** | 2026-10-23 (primer análisis, sobre el commit `8401cc8` de la rama `main`) |
| **Herramienta** | SonarQube Cloud, proyecto `Nela1901_RouteZero`, análisis automático |
| **Versión del análisis** | V_1_0_0 |
| **Versión** | 1.0.0 |

[← Volver al README Principal](../../../../../README.md)

---

> **Estado del documento.** Recoge el **primer análisis** de SonarQube (23-10-2026) y las correcciones que se hicieron a partir de él (Pull Request #67 y #69). El análisis automático de SonarQube **no volvió a ejecutarse** después de esas correcciones, por lo que los valores «después» de la sección 3 son una estimación a partir del código corregido. El reanálisis, ya con la cobertura de pruebas, se registrará en la versión V_1_1_0 de este documento (ver la sección 4).

## 1. Resumen Ejecutivo de Quality Gate

- **Tamaño analizado:** 17 407 líneas de código en 159 archivos (Python 8 692, TypeScript 8 385, CSS 118, PL/SQL 114, YAML 75 y HTML 23).
- **Estado del Quality Gate:** **no calculado.** El proyecto usa la definición de código nuevo «Previous version» y el primer análisis no tiene una versión anterior contra la cual comparar, por lo que SonarQube no emite PASSED ni FAILED.
- **Calificaciones del primer análisis (sobre todo el código):** Seguridad **E**, Fiabilidad **E** y Mantenibilidad **A**. Las dos E se deben a pocas incidencias graves (1 vulnerabilidad bloqueante y 5 bugs bloqueantes), no a un volumen alto.
- **Porcentaje de cobertura de pruebas (Coverage):** SonarQube muestra **sin dato**, porque el análisis automático no recibe reportes de cobertura. La cobertura la medimos nosotros con las herramientas de cada lenguaje:

| Parte | Herramienta | Cobertura | Pruebas |
|---|---|---|---|
| Backend (Python) | pytest-cov | **98 %** (3 161 sentencias, 68 sin cubrir) | 363 contra la base real |
| Frontend (TypeScript) | Vitest con V8 | **67.8 %** de líneas (846 de 1 247), 60.5 % de ramas | 100 de componentes y 33 de extremo a extremo |

- **Duplicación de código:** **0.5 %** (103 líneas en 6 bloques).

## 2. Métricas Principales

| Categoría | Cantidad Detectada | Severidad (Bloqueante / Alta / Media / Baja) |
|---|---|---|
| **Bugs** | 8 | 5 bloqueantes (`DELETE` sin `WHERE` en `datos_demo.sql`), 1 mayor y 2 menores |
| **Vulnerabilidades** | 16 | 1 bloqueante (*path traversal* en `generar_grafo.py`) y 15 mayores (10 del CI, 2 más del mismo script y 3 de contraseñas de pruebas) |
| **Code Smells** | 292 | 25 críticos, 196 mayores y 71 menores |
| **Security Hotspots** | 0 | SonarQube Cloud ya no los muestra aparte: aparecen dentro de las vulnerabilidades con la etiqueta *former-hotspot* |

Con el modelo de impacto actual de SonarQube Cloud, las mismas 316 incidencias se reparten así: **Mantenibilidad 273, Fiabilidad 37 y Seguridad 16**. La complejidad cognitiva total del proyecto es 1 634.

### Reglas más frecuentes

| Regla | Cantidad | Qué señala |
|---|---|---|
| `python:S9073` | 119 | Aserciones compuestas (`assert a and b`) en las pruebas |
| `typescript:S6759` | 44 | Props de componentes de React que deberían ser de solo lectura |
| `typescript:S6819` | 23 | Usar una etiqueta nativa en lugar de un `role` ARIA |
| `typescript:S3358` | 19 | Ternarios anidados |
| `typescript:S1077` | 15 | Íconos SVG sin texto alternativo |
| `plsql:S1192` y `DeleteOrUpdateWithoutWhere` | 11 y 5 | Literales repetidos y `DELETE` sin `WHERE` en `datos_demo.sql` |
| `python:S5778` | 8 | Una prueba de excepciones con más de una llamada |
| `python:S3776` | 7 | Complejidad cognitiva alta |
| `css:S9423` | 6 | Uso de `!important` |

## 3. Plan de Remediación y Deuda Técnica

- **Deuda técnica estimada por SonarQube:** **1 736 minutos (28 h 56 min, unos 3.6 días de trabajo)**, un 0.3 % del tamaño del código. El esfuerzo de remediación de seguridad es de 10 h 30 min y el de fiabilidad, de 2 h 45 min.
- **Principales hallazgos y acciones correctivas:**

| # | Hallazgo (regla) | Cantidad | Acción correctiva aplicada | Estado |
|---|---|---|---|---|
| 1 | Aserciones compuestas en pruebas (`python:S9073`) | 119 | Un script basado en el árbol sintáctico dividió cada `assert a and b` en una aserción por condición; las 363 pruebas pasan | Corregido |
| 2 | Props de React de solo lectura (`typescript:S6759`) | 44 | Se envolvió el tipo de cada componente en `Readonly<...>` | Corregido |
| 3 | Ternarios anidados (`typescript:S3358`) | 19 | Se reemplazaron por funciones y mapas de textos (`textoGuardar`, `marcaDeEntrega`, `textoDeEntrega`) | Corregido |
| 4 | Íconos sin texto alternativo (`typescript:S1077`) | 15 | Se marcaron con `aria-hidden="true"` (son decorativos) | Corregido |
| 5 | Etiquetas nativas en lugar de roles ARIA (`typescript:S6819`) | 23 | `main`, `section` y `output` en lugar de `role`; se aceptan los diálogos, el fondo de los diálogos, la barra de progreso y las tarjetas con bloques, donde la etiqueta nativa cambiaría el comportamiento o el HTML dejaría de ser válido (lo detectó el validador W3C) | Parcial |
| 6 | Pruebas de excepciones con varias llamadas (`python:S5778`) | 8 | Cada bloque `pytest.raises` contiene una sola llamada | Corregido |
| 7 | Seguridad del script del grafo (`pythonsecurity`, *path traversal*) | 3 | Las rutas de la línea de comandos deben quedar dentro de `backend/` y tener la extensión esperada; el grafo resultante es idéntico al anterior | Corregido |
| 8 | Seguridad del CI (`githubactions:S6505`, `S8543`, `S8541`) | 9 | `npm ci --ignore-scripts`, scripts de npm en lugar de `npx`, herramientas con versión exacta y `--only-binary :all:` | Corregido |
| 9 | Dependencias de Python sin bloquear (`githubactions:S8544`) | 1 | Requiere un archivo con sumas de verificación para `requirements.txt` | Abierto (ver `06 OWASP`) |
| 10 | Literales repetidos, espaciado entre elementos y otras reglas puntuales (17 reglas distintas) | 36 | Constantes, espacios explícitos, `.at()`, `Annotated` en FastAPI, expresiones regulares sin retroceso y otras | Corregido |
| 11 | Complejidad cognitiva (`python:S3776`, `typescript:S3776`) | 9 | Se redujo en `aco.optimizar`, `service_sesiones.renovar`, `generar_grafo.construir` y `PedidosPage`, sin cambiar su lógica | 4 corregidos, 5 aceptados |

### Hallazgos aceptados, con su justificación

| Hallazgo | Cantidad | Por qué se acepta |
|---|---|---|
| `datos_demo.sql`: `DELETE` sin `WHERE` (5 bloqueantes) y literales repetidos (11) | 16 | Es el script de **reinicio de la demostración**: borra las tablas completas a propósito y sus literales son datos de ejemplo, no código. Se excluye del análisis en `sonar-project.properties` |
| Complejidad cognitiva de `busqueda_local` (140), `construccion` (33), `trazado` (52), `rutas/service.py` (27) y del servidor simulado de `e2e/api.ts` (41) | 5 | Son los bucles centrales del motor de optimización y de la prueba; reducirla sin alterar los resultados es arriesgado y están cubiertos por pruebas. Se mantiene como deuda técnica |
| `!important` en `tokens.css` | 6 | Necesario para que las reglas de las consultas de contenedor sobrescriban los estilos en línea de React |
| Nombres de campo `Tp`, `Tpl`, `Tl` y `Dl` en `evaluacion.py` (`python:S116`) | 4 | Notación de las matrices de tiempo del motor, usada en toda su documentación |
| Contraseñas de `e2e/api.ts` (`typescript:S2068`) | 3 | Credenciales falsas de una API simulada en el navegador; no existen en ningún servicio |
| `enumerate()` con índice en `busqueda_local` (`python:S8518`) | 1 | Cambio dentro del bucle del motor; se deja junto con su complejidad |
| Roles ARIA sin etiqueta nativa equivalente (`typescript:S6819`) | 7 | Los diálogos modales y el fondo que los cierra (`<dialog>` cambiaría el manejo del foco y de Escape), la barra de progreso y las tarjetas con bloques (`<output>` solo admite contenido en línea) |

### Estado estimado tras las correcciones

Se corrigieron en el código unas **273 de las 316 incidencias** del primer análisis. Quedarían abiertas unas 43: **16 de `datos_demo.sql`** (que se excluye del análisis), las 26 restantes aceptadas de la tabla anterior (roles ARIA 7, complejidad 5, `!important` 6, nombres de matrices 4, contraseñas simuladas 3 y `enumerate` 1) y la dependencia de Python sin bloquear. Estas cifras **no son una medición**: se confirmarán con el reanálisis.

Además de lo que marcó SonarQube, la revisión de seguridad y accesibilidad encontró cuatro problemas reales que SonarQube no detecta (CORS sin PATCH, el QR como HTML, falta de manejo de caídas de Supabase y de la base de datos, y 17 mensajes de error sin anuncio para lectores de pantalla); están en los documentos `06` y `07`.

## 4. Reanálisis y cobertura (pendiente)

El análisis automático dejó de ejecutarse tras el primer análisis (no hay un análisis nuevo desde el 23-10-2026, aunque `main` recibió varias fusiones) y no puede mostrar cobertura. Para resolver las dos cosas se dejó lista la configuración de **SonarScanner ejecutado con la cobertura de pruebas**:

1. `sonar-project.properties` (en la raíz): qué analizar, qué excluir y dónde están los reportes de cobertura.
2. `scripts/preparar_cobertura.py`: ajusta las rutas de los reportes de pytest-cov y Vitest para que SonarQube los reconozca.
3. Pasos: generar `backend/coverage.xml` con pytest y `frontend/coverage/lcov.info` con `npm run test:coverage`, ejecutar `python scripts/preparar_cobertura.py` y correr SonarScanner con un token en la variable `SONAR_TOKEN` (el token nunca se guarda en el repositorio). Hay que desactivar antes el análisis automático del proyecto.

Con ese reanálisis se completará la versión V_1_1_0 de este documento con el estado real del Quality Gate, la cobertura medida por SonarQube y las incidencias que queden abiertas.

---

[← Volver al README Principal](../../../../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-10-26 | Versión inicial: primer análisis de SonarQube (23-10-2026), métricas, correcciones aplicadas, hallazgos aceptados y plan de reanálisis con cobertura | Inciso Aguilar Elizabeth Antonela |
