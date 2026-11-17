# 05 Evaluación de Calidad de Código — SonarQube

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Líder del Proyecto** | Inciso Aguilar Elizabeth Antonela |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Sprint** | Sprint 3 — Rutas y Visualización (Inspección 03) |
| **Fecha de análisis** | 2026-10-30 (reanálisis con cobertura, sobre el commit `7233c04` de la rama `sprint4` más los cambios de esta versión). Primer análisis: 2026-10-23 |
| **Herramienta** | SonarQube Cloud, proyecto `Nela1901_RouteZero`, ejecutado con SonarScanner y con los reportes de cobertura de pytest y Vitest |
| **Versión del análisis** | V_1_1_0 |
| **Versión** | 1.1.0 |

[← Volver al README Principal](../../../../README.md)

---

> **Estado del documento.** Esta versión reemplaza las estimaciones de la V_1_0_0 por una **medición real**: el reanálisis del 30-10-2026, ya con la cobertura de pruebas. Muestra el resultado del Quality Gate tal como lo calculó SonarQube. **El reanálisis ejecutado antes de corregir la cobertura falló en una condición (72.5 % de cobertura del código nuevo)**; la causa y su corrección están en la sección 3, y el análisis final **aprobó el Quality Gate**.

## 1. Resumen Ejecutivo de Quality Gate

- **Tamaño analizado:** 11 317 líneas de código. Bajó de 17 407 porque se excluyó del análisis `datos_demo.sql` (script de reinicio de la demostración) y las pruebas que viven junto al código.
- **Estado del Quality Gate:** **PASSED** (6 de 6 condiciones cumplidas). El Quality Gate «Sonar way» solo evalúa el **código nuevo** desde el primer análisis:

| Condición (código nuevo) | Resultado | Umbral | Estado |
|---|---|---|---|
| Calificación de fiabilidad | A | A | Cumple |
| Calificación de seguridad | A | A | Cumple |
| Calificación de mantenibilidad | A | A | Cumple |
| Duplicación | 0.0 % | ≤ 3 % | Cumple |
| Security Hotspots revisados | 100 % | 100 % | Cumple |
| **Cobertura** | **83.7 %** | **≥ 80 %** | Cumple |

- **Calificaciones sobre todo el código:** Seguridad **A** (era E), Fiabilidad **A** (era E) y Mantenibilidad **A**.
- **Porcentaje de cobertura de pruebas (Coverage):** **85.2 %** del proyecto según SonarQube (89.6 % de las líneas: 4 287 de 4 783 cubiertas). La cobertura del código nuevo es **83.7 %**, con la meta en 80 %.

| Parte | Cobertura de líneas según SonarQube | Líneas por cubrir | Sin cubrir | Medición propia de la herramienta del lenguaje |
|---|---|---|---|---|
| Backend (Python, `backend/src`) | **96.9 %** | 3 245 | 99 | pytest-cov: 98 % de los módulos medidos, con 363 pruebas contra la base real |
| Frontend (TypeScript, `frontend/src`) | **74.2 %** | 1 538 | 397 | Vitest con V8: 70.4 % de líneas, con 108 pruebas de componentes (y 33 de extremo a extremo con Playwright, que no entran en la cobertura) |

  El backend marca 96.9 % en SonarQube y 98 % en pytest-cov porque SonarQube cuenta además archivos que `pytest.ini` no mide, como la configuración y los esquemas.
- **Duplicación de código:** **0.6 %** (76 líneas en 4 bloques).

## 2. Métricas Principales

| Categoría | Cantidad Detectada | Severidad (Bloqueante / Alta / Media / Baja) |
|---|---|---|
| **Bugs** | **0** (eran 8) | Sin incidencias de fiabilidad |
| **Vulnerabilidades** | **0** (eran 16) | Sin incidencias de seguridad, ni abiertas ni resueltas como falso positivo: todas se corrigieron o salieron del análisis (sección 3) |
| **Code Smells** | **18** (eran 292) | 4 críticos y 14 mayores; todas de mantenibilidad |
| **Security Hotspots** | **0** | Calificación de revisión A. SonarQube Cloud los muestra dentro de las vulnerabilidades (etiqueta *former-hotspot*) |

La complejidad cognitiva total del proyecto bajó de 1 634 a 1 179.

### Evolución respecto del primer análisis (23-10-2026)

| Medida | Primer análisis | Reanálisis | Cambio |
|---|---|---|---|
| Incidencias abiertas | 316 | **18** | −298 |
| Bugs | 8 | 0 | −8 |
| Vulnerabilidades | 16 | 0 | −16 |
| Deuda técnica | 1 736 min (28 h 56 min) | **282 min (4 h 42 min)** | −84 % |
| Calificación de seguridad | E | A | |
| Calificación de fiabilidad | E | A | |
| Cobertura | sin dato | 85.2 % | |
| Duplicación | 0.5 % | 0.6 % | |

De las 316 incidencias del primer análisis: **282** se corrigieron en el código (incluidas las 3 de `generar_grafo.py`, que se resolvieron quitando las rutas por línea de comandos) y **16** salieron del análisis al excluir `datos_demo.sql`; quedan **18** abiertas. Ninguna se resolvió como falso positivo.

### Incidencias abiertas (18)

| Regla | Cantidad | Qué señala | Decisión |
|---|---|---|---|
| `typescript:S6819` | 8 | Usar una etiqueta nativa en lugar de un `role` ARIA | Aceptada (ver sección 3) |
| `css:S9423` | 6 | Uso de `!important` | Aceptada |
| `python:S3776` | 4 | Complejidad cognitiva alta | Aceptada, queda como deuda técnica |

## 3. Plan de Remediación y Deuda Técnica

- **Deuda técnica estimada por SonarQube:** **282 minutos (4 h 42 min)**, todo de mantenibilidad. El esfuerzo de remediación de seguridad y de fiabilidad es **0**.
- **Principales hallazgos y acciones correctivas:**

| # | Hallazgo (regla) | Cantidad | Acción correctiva aplicada | Estado |
|---|---|---|---|---|
| 1 | Aserciones compuestas en pruebas (`python:S9073`) | 119 | Un script basado en el árbol sintáctico dividió cada `assert a and b` en una aserción por condición; las 363 pruebas pasan | Corregido |
| 2 | Props de React de solo lectura (`typescript:S6759`) | 45 | Se envolvió el tipo de cada componente en `Readonly<...>` | Corregido |
| 3 | Ternarios anidados (`typescript:S3358`) | 19 | Se reemplazaron por funciones y mapas de textos (`textoGuardar`, `marcaDeEntrega`, `textoDeEntrega`) | Corregido |
| 4 | Íconos sin texto alternativo (`typescript:S1077`) | 16 | Se marcaron con `aria-hidden="true"` (son decorativos) | Corregido |
| 5 | Etiquetas nativas en lugar de roles ARIA (`typescript:S6819`) | 15 | `main`, `section` y `output` en lugar de `role`; se aceptan los 8 restantes (diálogos modales, fondo que los cierra, barra de progreso y tarjetas con bloques), donde la etiqueta nativa cambiaría el comportamiento o el HTML dejaría de ser válido (lo detectó el validador W3C) | Parcial |
| 6 | Pruebas de excepciones con varias llamadas (`python:S5778`) | 8 | Cada bloque `pytest.raises` contiene una sola llamada | Corregido |
| 7 | Seguridad del script del grafo (`pythonsecurity`, *path traversal*) | 3 | Se quitaron las rutas y las opciones de la línea de comandos: el script solo descarga de Overpass y escribe el archivo en una ubicación fija. El grafo resultante es idéntico al anterior | Corregido (ver el apartado siguiente) |
| 8 | Seguridad del CI (`githubactions`) | 10 | `npm ci --ignore-scripts`, scripts de npm en lugar de `npx`, herramientas con versión exacta y `--only-binary :all:` | Corregido; cerradas por SonarQube en el reanálisis |
| 9 | Tipo `FormEvent` obsoleto (`typescript:S1874`) | 15 | Se cambió por `SubmitEvent` (React 19.3) en las 6 pantallas con formularios | Corregido |
| 10 | Expresiones regulares con retroceso (`python:S8786`) | 2 | En `verificar_enlaces.py` se reemplazaron por expresiones simples y el resto del tratamiento se hace en código Python; el verificador da la misma salida sobre los documentos y sigue detectando enlaces rotos y secciones inexistentes | Corregido |
| 11 | Literales repetidos, espaciado entre elementos y otras reglas puntuales (17 reglas distintas) | 36 | Constantes, espacios explícitos, `.at()`, `Annotated` en FastAPI, expresiones regulares sin retroceso y otras | Corregido |
| 12 | Complejidad cognitiva (`python:S3776`, `typescript:S3776`) | 9 | Se redujo en `aco.optimizar`, `service_sesiones.renovar`, `generar_grafo.construir` y `PedidosPage`, sin cambiar su lógica | 4 corregidos, 4 aceptados y 1 que SonarQube ya no informa (el servidor simulado de las pruebas de extremo a extremo) |
| 13 | Nombres de campo `Tp`, `Tpl`, `Tl` y `Dl` (`python:S116`), `enumerate()` con índice (`python:S8518`) y prueba omitida (`typescript:S1607`) | 6 | `tiempo_punta`, `tiempo_lista`, etc. en `evaluacion.py` (solo se usaban dentro de ese archivo); el bucle de `dos_opt` toma la ruta completa; el script de auditoría de producción falla con un mensaje claro si falta `CLAVE_PRUEBA`, en vez de omitirse. Pasan las 55 pruebas relacionadas con el motor | Corregido |

### Seguridad: cómo se llegó a 0 vulnerabilidades

SonarQube señaló *path traversal* en los dos scripts de uso local del repositorio. Se necesitaron tres intentos, y se documentan porque los dos primeros no bastaron:

| Intento | Qué se hizo | Resultado del análisis |
|---|---|---|
| 1 | En `generar_grafo.py`, validar las rutas de la línea de comandos (dentro de `backend/` y con la extensión esperada) | SonarQube siguió informando 3 incidencias: no sigue la validación a través de `argparse` |
| 2 | Reemplazar los argumentos de ruta por dos opciones sin ruta (`--usar-descarga` y `--guardar-descarga`) con ubicaciones fijas, y **excluir `scripts/preparar_cobertura.py` del análisis** | Desaparecieron las 3, pero apareció 1 nueva: SonarQube marca como riesgo que un contenido leído (lo que devuelve Overpass) se escriba con `write_text`, y el Quality Gate falló por la calificación de seguridad del código nuevo |
| 3 | Quitar del script toda opción y la escritura de la descarga: solo descarga de Overpass y genera el grafo | **0 incidencias de seguridad** y Quality Gate aprobado |

- **`generar_grafo.py` (corregido):** ya no recibe rutas ni opciones, la ubicación del archivo de salida es fija y no escribe contenido descargado. Se comprobó, con datos de prueba, que el grafo que genera es idéntico al anterior (36 nodos y 115 tramos). Se retiraron las opciones `--entrada` y `--guardar-descarga`; el documento del motor de rutas del Sprint 2 (V_1_5_0) lo refleja.
- **`scripts/preparar_cobertura.py` (excluido del análisis):** es un paso de apoyo del propio análisis de SonarQube (reescribe las rutas de los reportes de cobertura) y no forma parte del sistema, igual que `datos_demo.sql`. La exclusión está en `sonar-project.properties`, a la vista de cualquiera que revise el repositorio; el script sigue versionado.

**Resultado:** 18 vulnerabilidades registradas a lo largo del trabajo (16 del primer análisis y 2 que aparecieron en scripts modificados), **todas cerradas**: 17 corregidas en el código y 1 por la exclusión del script de apoyo. SonarQube muestra 0 vulnerabilidades, 0 Security Hotspots y calificación de seguridad A.

### Hallazgos aceptados, con su justificación

| Hallazgo | Cantidad | Por qué se acepta |
|---|---|---|
| Complejidad cognitiva de `busqueda_local` (140), `construccion` (33), `trazado` (52) y `rutas/service.py` (27) (`python:S3776`) | 4 | Son los bucles centrales del motor de optimización; reducirla sin alterar los resultados es arriesgado y están cubiertos por pruebas. Se mantiene como deuda técnica |
| `!important` en `tokens.css` (`css:S9423`) | 6 | Necesario para que las reglas de las consultas de contenedor sobrescriban los estilos en línea de React |
| Roles ARIA sin etiqueta nativa equivalente (`typescript:S6819`) | 8 | Los diálogos modales y el fondo que los cierra (`<dialog>` cambiaría el manejo del foco y de Escape), la barra de progreso y las tarjetas con bloques (`<output>` solo admite contenido en línea) |

### Quality Gate: cómo se pasó de 72.5 % a 83.7 % de cobertura del código nuevo

El primer reanálisis del 30-10-2026 **falló en una sola condición**: la cobertura del código nuevo era **72.5 %** frente al 80 % que exige el Quality Gate «Sonar way». SonarQube calcula esa cobertura sobre líneas y ramas (`if`) de lo que cambió desde el primer análisis: 175 líneas y 113 ramas, de las cuales 78 estaban sin cubrir. Para llegar al 80 % podían quedar como máximo 56.

| Causa | Elementos sin cubrir | Corrección |
|---|---|---|
| `backend/src/main.py` figuraba en 0 %: tiene 10 pruebas (cabeceras de seguridad, CORS y respuestas 503), pero `pytest.ini` no lo incluía entre los módulos medidos | 17 líneas | Se agregó `--cov=src.main` a `pytest.ini`; el módulo pasa a 50 de 52 líneas cubiertas |
| El título de cada pantalla (`OperacionesLayout`, WCAG 2.4.2) no tenía pruebas | 6 | 3 pruebas nuevas: sección conocida, otra sección y ruta sin sección |
| El aviso de vencimiento de documentos (`EstadoVencimiento`, en `ui.tsx`) no tenía pruebas | 6 | 5 pruebas nuevas: vencida, vence en 12 días, sin aviso, sin fecha y cálculo de días |

**Resultado del análisis final: cobertura del código nuevo 83.7 % (≥ 80 %), con 47 elementos sin cubrir de 288 y el Quality Gate en PASSED.** No se cambió el umbral ni se excluyó código para lograrlo; las 8 pruebas del frontend son nuevas (108 en total) y el backend sigue en 363.

**Mejora pendiente (no bloquea el Quality Gate):** las pantallas con menor cobertura siguen siendo las de formularios.

| Pantalla (frontend) | Cobertura de líneas (Vitest) |
|---|---|
| `PedidosPage.tsx` | 54 % |
| `ConductoresPage.tsx` | 64 % |
| `FlotaPage.tsx` | 67 % |
| `SeguridadPage.tsx` | 67 % |

Se escribirán pruebas de componentes para sus formularios y acciones en una iteración posterior.

## 4. Cómo se repite el análisis

El análisis automático de SonarQube Cloud no recibe la cobertura de las pruebas, así que se desactivó y se ejecuta **SonarScanner** desde la raíz del repositorio:

1. `sonar-project.properties` define qué analizar, qué excluir y dónde están los reportes de cobertura.
2. Se generan los reportes: `backend/coverage.xml` con pytest (`--cov-report=xml:coverage.xml`, desde `backend/`) y `frontend/coverage/lcov.info` con `npm run test:coverage` (desde `frontend/`).
3. `python scripts/preparar_cobertura.py` ajusta las rutas de los reportes para que SonarQube los reconozca.
4. Se define el token en la variable de entorno `SONAR_TOKEN` (nunca se guarda en el repositorio) y se ejecuta `npx --yes @sonar/scan`. El análisis tarda unos 4 minutos.

---

[← Volver al README Principal](../../../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-10-26 | Versión inicial: primer análisis de SonarQube (23-10-2026), métricas, correcciones aplicadas, hallazgos aceptados y plan de reanálisis con cobertura | Inciso Aguilar Elizabeth Antonela |
| V_1_1_0 | 2026-10-30 | Reanálisis con cobertura: Quality Gate aprobado (el primer reanálisis falló por la cobertura del código nuevo, 72.5 %; se corrigió con `src.main` en `pytest.ini` y 8 pruebas nuevas hasta 83.7 %), cobertura por parte, evolución de 316 a 18 incidencias y vulnerabilidades y bugs en 0, sin falsos positivos (el script del grafo se corrigió y el de apoyo para la cobertura se excluyó del análisis) | Inciso Aguilar Elizabeth Antonela |
