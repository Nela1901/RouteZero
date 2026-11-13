# 02 Estándares de Ingeniería de Software y Guía de Desarrollo Verde

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Líder del Proyecto** | Inciso Aguilar Elizabeth Antonela |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Actividad** | Inspección 04 — Green Software y verificación de estándares (actividad de cierre del Sprint 4) |
| **Fecha** | 2026-11-10 |
| **Estándares aplicados** | ISO/IEC 25010, principios de la Green Software Foundation, W3C Web Sustainability Guidelines, Clean Code, SOLID, DRY y YAGNI |
| **Documento hermano** | [01 Informe de Reducción del Impacto Ambiental](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_4_0.md) |
| **Versión** | 1.4.0 |

[← Volver al README Principal](../../../../README.md)

---

## 1. Propósito y alcance

Este documento fundamenta en estándares las mejoras del [informe de reducción del impacto ambiental](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_4_0.md), define las reglas de desarrollo verde que sigue el equipo para el backend y el frontend, y cruza cada una de las 8 áreas de optimización con los estándares en una matriz (sección 6).

**Nota sobre la numeración de W3C.** Las *Web Sustainability Guidelines* (WSG, Pautas de Sostenibilidad Web) de W3C están publicadas como **Group Note Draft del 16 de octubre de 2026** (borrador del Grupo de Interés en Web Sostenible; el documento no se rotula «1.0»). Su numeración oficial es: **2.x** Diseño de experiencia de usuario, **3.x** Desarrollo web, **4.x** Hosting, infraestructura y sistemas, y **5.x** Estrategia de negocio y gestión de producto; la sección 1 es solo introducción. Este documento cita siempre **la numeración oficial**. Los materiales de la actividad hablan de «pautas 1.2, 2.4 y 3.1» con tres temas (optimización de medios, arquitectura y caché, transferencia de red); esos temas se corresponden con las pautas oficiales **2.9, 4.2 y 4.3** (y 3.1), como se explica en la sección 4.

### 1.1 La numeración de la rúbrica frente a la oficial

La rúbrica de la inspección habla de las pautas «1.2», «2.4» y «3.1». En el documento oficial vigente **la sección 1 es solo introducción y no contiene pautas**, y los números 2.4 y 3.1 corresponden a otros temas. Por eso cada tema de la rúbrica se asocia con su pauta oficial equivalente:

| Rúbrica | Tema que describe | Pauta oficial (16-10-2026) | Evidencia de RouteZero |
|---|---|---|---|
| 1.2 | Optimización de medios | **2.9** Optimizar los medios para reducir el uso de recursos | `favicon.svg` ya minimizado (−0.2 %) y sin imágenes rasterizadas ([informe 01, 5.3](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_4_0.md)) |
| 2.4 | Arquitectura y caché | **4.2** Optimizar la caché y 3.7 Diferir recursos no críticos | `Cache-Control: immutable` en `/assets/*` y carga diferida con `React.lazy` (5.7 y 5.4) |
| 3.1 | Transferencia de red | **4.3** Reducir la transferencia de datos con compresión | gzip en la API (−72 % a −83 %) y Brotli en los archivos estáticos (5.8) |

En el documento oficial, la 2.4 es «Diseñar recorridos de usuario eficientes» y la 3.1 es «Fijar metas según el impacto en rendimiento y energía»; ambas también se cubren (sección 4).

---

## 2. ISO/IEC 25010: las ocho características de calidad

**ISO/IEC 25010** es el modelo internacional de calidad del producto de software: define características de calidad y las subdivide en subcaracterísticas medibles. La actividad se apoya en dos: la **eficiencia de desempeño** (qué tan bien rinde el software con los recursos que usa) y la **mantenibilidad** (qué tan fácil es cambiarlo). El requisito no funcional que las motiva es **RNF-011, Eficiencia energética** (ver [`07. Requisitos no funcionales`](../../../01%20Inicio/07.%20Requisitos%20no%20funcionales%20V_1_2_0.md)).

### 2.1 Eficiencia de desempeño

| Subcaracterística | Qué mide | Cómo se aplicó en RouteZero | Evidencia |
|---|---|---|---|
| **Comportamiento temporal** (*time behaviour*) | Tiempos de respuesta y de procesamiento | Carga diferida y fuentes propias reducen el FCP y el LCP; índices y consultas acotadas bajan los tiempos de la base | FCP móvil 2.18 → 1.66 s; LCP de escritorio 797 → 488 ms; 17 consultas críticas ≤ 42 ms (informe 01, secciones 5.1, 5.4 y 5.6) |
| **Utilización de recursos** (*resource utilization*) | Cantidad de recursos (red, CPU, memoria) que consume | Menos bytes transferidos y menos JavaScript que ejecutar en el celular del conductor | Peso 213 → 140 KB en móvil (−34 %); JavaScript inicial −49 %; TBT de 0 ms |
| **Capacidad** (*capacity*) | Límites que soporta el sistema | Paginación de la tabla que más crece (pedidos, de 12 en 12 y máximo 200 por página); el motor de rutas se probó con 150 pedidos y 15 vehículos | Informe 01, sección 5.2; mediciones de generación y re-optimización de los sprints 2 y 3 |

### 2.2 Mantenibilidad

| Subcaracterística | Qué mide | Cómo se aplicó en RouteZero | Evidencia |
|---|---|---|---|
| **Modularidad** | Cambiar una parte sin afectar al resto | Backend organizado por características; ningún módulo de negocio importa a otro. Frontend dividido en un trozo de código por pantalla | [`test_arquitectura.py`](../../../../backend/tests/test_arquitectura.py) vigila la independencia; trozos de la sección 5.4 del informe 01 |
| **Reusabilidad** | Reutilizar componentes en varios lugares | Componentes y utilidades compartidas en lugar de copias | `utilesCrud.ts` lo usan 4 pantallas y `ui.tsx`; `ui.tsx` y `acciones.tsx` los usan 9 archivos |
| **Analizabilidad** | Entender y diagnosticar el sistema | Comentarios que explican el porqué, documentación por sprint, auditorías con script | [Calidad de código](../../Sprint%203/Implementaci%C3%B3n/05%20Calidad%20de%20c%C3%B3digo%20V_1_2_0.md) (SonarQube); `auditar_consultas.py` |
| **Modificabilidad** | Cambiar sin introducir defectos | Parámetros que se ajustan sin tocar la lógica (precio del combustible, meta mensual, factores de congestión) | `backend/src/core/config.py`, `backend/src/rutas/congestion.py` |
| **Capacidad de ser probado** (*testability*) | Facilidad de verificar | Pruebas automáticas en las tres capas | 360 de backend (cobertura de 98 %), 178 de Vitest y 35 de extremo a extremo |

### 2.3 Las ocho características de un vistazo

Se usa la edición de ISO/IEC 25010 de ocho características (la que citan los documentos del proyecto). Las dos primeras de la lista de arriba, eficiencia de desempeño y mantenibilidad, se desarrollan en 2.1 y 2.2; las demás se resumen aquí con su evidencia y su límite.

| Característica | Qué mide | Evidencia en RouteZero | Límite declarado |
|---|---|---|---|
| **Adecuación funcional** | Que haga lo que debe, completo y correcto | Todos los ítems de los Sprints 3 y 4 completados (26 y 18 Story Points); las reglas de negocio RN-001 a RN-003 y RN-005 a RN-015 de los módulos entregados están implementadas y con pruebas automáticas | RN-004 (restricción por placa) está **desactivada a propósito**: el decreto citado inicialmente no existe |
| **Eficiencia de desempeño** | Tiempos, recursos y capacidad | Sección 2.1 | Latencia de Render gratuito (IMP-016) |
| **Compatibilidad** | Convivir e intercambiar información con otros sistemas | API REST/JSON documentada con Swagger (`/docs`); integra OpenStreetMap, Supabase Auth y PostgreSQL | Probado en Chrome y Chromium (Playwright y Lighthouse); Firefox y Safari **no** se probaron |
| **Usabilidad** | Facilidad de uso y accesibilidad | Lighthouse de accesibilidad en 100 (24 mediciones); WCAG 2.2 AA con 36 de 40 criterios cumplidos ([evaluación](../../Sprint%203/Implementaci%C3%B3n/07%20Evaluaci%C3%B3n%20de%20accesibilidad%20WCAG%20V_1_0_0.md)); ayudas «i» en los indicadores; todas las pantallas se ven en ancho móvil | La escala SUS y la evaluación con las 10 heurísticas de Nielsen **están pendientes** (Inspección 05) |
| **Fiabilidad** | Funcionar sin fallar y recuperarse | Respuestas 503 claras si Supabase o la base no responden (OWASP A10); la re-optimización cumple RN-012 (22.2 s en Render, límite de 30 s) y la generación RN-015 | Render gratuito tiene arranque en frío de unos 52 s y Supabase gratuito se pausa por inactividad (ocurrió el 09-11-2026) |
| **Seguridad** | Proteger datos y accesos | Verificación en dos pasos (TOTP), sesiones con detección de robo, RLS en la base, roles por endpoint (RN-014), CORS con el origen exacto y OWASP Top 10 evaluado ([documento](../../Sprint%203/Implementaci%C3%B3n/06%20Evaluaci%C3%B3n%20de%20seguridad%20OWASP%20V_1_2_0.md)); Bandit, `pip-audit` y `npm audit` en el CI | El DNI del conductor está en texto plano en la base y los tokens se guardan en `localStorage` (brechas declaradas) |
| **Mantenibilidad** | Facilidad para cambiar | Sección 2.2 | — |
| **Portabilidad** | Instalarlo y moverlo a otro entorno | Todo se configura con variables de entorno (`.env.example`) y se despliega con `render.yaml` y Vercel; sin contenedores | Depende de Supabase (autenticación y base de datos): reemplazarlo exigiría reescribir esa capa |

---

## 3. Green Software Foundation: los cuatro principios

La **Green Software Foundation (GSF)** es una organización de la Linux Foundation que define cómo construir software con menos carbono. Su enfoque se resume en **cuatro principios**, de los cuales la eficiencia de carbono es el objetivo general y los otros tres son las únicas actividades que reducen de verdad las emisiones del software.

| Principio | Qué significa | Cómo se aplicó | Lo que **no** se hace |
|---|---|---|---|
| **Eficiencia de carbono** | Emitir la menor cantidad de carbono posible por cada unidad de trabajo | Se mide la huella con SWDM v4 y se vigila con un presupuesto en CI (informe 01, secciones 7 y 8); el sistema optimiza rutas para gastar menos combustible y muestra su propia huella digital en la pantalla de Sostenibilidad (7.5) | La huella del hosting no se reduce: no es hosting verde |
| **Eficiencia energética** | Usar la menor electricidad posible | Menos bytes, menos JavaScript, consultas con índice, motor de rutas con presupuesto de tiempo (25 s) y sin llamadas a servicios externos en funcionamiento | Brotli propio: la plataforma ya comprime y duplicarlo gastaría CPU |
| **Eficiencia de hardware** | Reducir la fabricación de equipos (carbono incorporado) y alargar su vida útil | Páginas livianas que funcionan bien en celulares de gama media, sin exigir equipos nuevos; el módulo de sostenibilidad calcula el costo del ciclo de vida de la flota | Sin evaluación del hardware del proveedor de hosting |
| **Conciencia de carbono** | Hacer más trabajo cuando la electricidad es más limpia y menos cuando es más sucia | El pipeline de auditoría solo se ejecuta cuando cambia el frontend, para no gastar cómputo en cambios que no pueden afectar el rendimiento | **No** se desplazan tareas según la intensidad de la red eléctrica. Se declara como brecha |

La GSF también publica otros marcos (por ejemplo, un conjunto de ocho principios y la especificación SCI, *Software Carbon Intensity*); aquí se usan los cuatro anteriores, que son los que pide la actividad.

---

## 4. W3C Web Sustainability Guidelines (WSG)

Las **WSG** son pautas del W3C para que los sitios y aplicaciones web sean más sostenibles. Cada pauta tiene criterios de éxito verificables. La tabla relaciona las pautas oficiales (numeración y títulos de la publicación del 16-10-2026) con la evidencia del proyecto. Los números entre paréntesis remiten a las secciones del [informe 01](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_4_0.md).

| Pauta | Título (traducción) | Evidencia en RouteZero |
|---|---|---|
| **2.4** | Diseñar recorridos de usuario eficientes y ágiles | El conductor ve su ruta y registra cada entrega en una sola pantalla, sin pasos intermedios (HU-014) |
| **2.9** | Optimizar los medios para reducir el uso de recursos | No hay imágenes rasterizadas; el único SVG ya está minimizado (−0.2 %) y no se mantiene un archivo sin uso (informe 01, 5.3). *Corresponde al tema de «optimización de medios» de los materiales* |
| **2.11** | Usar tipografía web optimizada | Tres familias variables, solo subconjunto latino, `font-display: swap` (5.6) |
| **2.15** | Auditar y probar para encontrar y resolver problemas | Lighthouse, validador W3C, Playwright, SonarQube y OWASP en cada sprint |
| **3.1** | Fijar metas según el impacto en rendimiento y energía | Presupuesto de rendimiento y peso en `lighthouserc.json`; si se supera, falla la comprobación del Pull Request (8) |
| **3.2** | Minimizar y eliminar código no usado | La compilación de Vite minimiza; se eliminó `icons.svg`; no hay dependencias sin uso (5.3 y 5.5) |
| **3.3** | Modularizar los componentes que consumen mucho ancho de banda | Leaflet (45 KB comprimidos) queda en un trozo aparte que solo paga quien abre un mapa (5.4) |
| **3.5** | Tratar a los terceros igual que a lo propio | Fuentes autoalojadas: 0 peticiones a Google; los mosaicos de OpenStreetMap son la única dependencia externa, necesaria para el mapa (5.6) |
| **3.7** | Diferir la carga de recursos no críticos | `React.lazy` y `Suspense` en las nueve pantallas (5.4) |
| **3.12** | Usar dependencias con moderación y mantenerlas | 5 paquetes de ejecución en el frontend; Dependabot, `npm audit`, Bandit y `pip-audit` en el CI (5.5) |
| **3.16** | Reducir el número y la complejidad de las consultas a la base de datos | Auditoría de 17 consultas, índice nuevo y conteo solo del periodo con `JOIN LATERAL` (5.1) |
| **4.1** | Usar hosting sostenible | **Brecha declarada:** Vercel y Render no figuran como hosting verde (7.4) |
| **4.2** | Optimizar la caché | `Cache-Control: public, max-age=31536000, immutable` para `/assets/*`; `no-store` en la API por seguridad (5.7). *Corresponde al tema de «arquitectura y caché» de los materiales* |
| **4.3** | Reducir la transferencia de datos con compresión | La API responde con gzip (−72 % a −83 %) y los archivos estáticos con Brotli, ambos a cargo de la plataforma (5.8). *Corresponde al tema de «transferencia de red»* |
| **5.5** | Calcular el impacto ambiental | Cálculo con SWDM v4 verificado contra CO2.js (7) y mostrado dentro del sistema en la tarjeta «Huella digital de esta sesión» (7.5); el dashboard muestra la evolución y la proyección de las emisiones frente a la meta (7.6) |
| **5.24** | Definir presupuestos de rendimiento, ambientales y humanos | Los umbrales de `lighthouserc.json` son un presupuesto de rendimiento y peso (8) |

---

## 5. Guía de desarrollo verde para el backend y el frontend

Reglas que sigue el equipo, ordenadas por el principio de ingeniería que las sostiene:

- **Clean Code** (Código Limpio): nombres que describen el dominio, funciones cortas y comentarios que explican el *porqué* y no el *qué*.
- **SOLID**: cinco principios de diseño orientado a objetos. **S**, responsabilidad única (cada clase o módulo hace una cosa); **O**, abierto a extensión y cerrado a modificación; **L**, sustitución de Liskov (un subtipo puede reemplazar al tipo base); **I**, segregación de interfaces (interfaces pequeñas); **D**, inversión de dependencias (depender de abstracciones, no de detalles).
- **DRY** (*Don't Repeat Yourself*, no te repitas): cada conocimiento tiene una sola fuente de verdad.
- **YAGNI** (*You Aren't Gonna Need It*, no vas a necesitarlo): no construir lo que todavía no hace falta.

### 5.1 Backend (FastAPI, SQLAlchemy y PostgreSQL)

| # | Regla | Principio | Cómo se cumple y se verifica |
|---|---|---|---|
| B1 | Una responsabilidad por capa: el router habla HTTP, el servicio aplica las reglas de negocio y el repositorio ejecuta el SQL | SOLID (S), Clean Code | `router.py` → `service.py` → `repository.py` en cada módulo. Los repositorios no hacen `commit`: lo hace una sola vez la petición |
| B2 | Dependencias inyectadas, no creadas dentro de la función (`Depends`), y módulos de negocio independientes entre sí | SOLID (D, O) | Los routers reciben la sesión, el usuario y los roles por inyección; `test_arquitectura.py` falla si un módulo importa a otro |
| B3 | Cada consulta frecuente trae solo las columnas y filas que necesita, las listas que crecen se paginan y cada consulta tiene el índice que la resuelve | Green (energía), YAGNI | `auditar_consultas.py` falla si una consulta pasa de 500 ms o recorre una tabla grande sin índice utilizable (informe 01, 5.1) |
| B4 | No duplicar lo que la plataforma ya hace (compresión, TLS) | YAGNI, Green | Se midió que Render comprime y no se agregó otro middleware (5.8) |
| B5 | Un valor configurable se define una sola vez | DRY | Precio del combustible, meta mensual y factores de congestión viven en `config.py` y `congestion.py` y se leen desde ahí |
| B6 | La seguridad no se sacrifica por rendimiento | Clean Code, OWASP | Las respuestas de la API llevan `Cache-Control: no-store`: el navegador no guarda copia de datos autenticados |
| B7 | Todo cambio de lógica lleva pruebas; la cobertura no baja | Clean Code | 360 pruebas, cobertura de 98 %; análisis de SonarQube, Bandit y `pip-audit` |
| B8 | El navegador solo puede ver de la API lo mínimo y solo nuestro frontend | Clean Code, OWASP | `Timing-Allow-Origin` con el origen exacto del frontend, nunca `*` (`test_seguridad_cabeceras.py`); los tamaños alimentan la huella digital de la sesión |

### 5.2 Frontend (React, Vite y TypeScript)

| # | Regla | Principio | Cómo se cumple y se verifica |
|---|---|---|---|
| F1 | Toda pantalla nueva se carga a demanda con `React.lazy` y tiene un mensaje de carga | Green (energía), WSG 3.7 | `App.tsx`; `npm run build` muestra un trozo por pantalla |
| F2 | Sin recursos de terceros en el arranque: fuentes y scripts se sirven desde el propio dominio | Green, WSG 3.5 | 0 peticiones externas en el login (verificado en el navegador). La excepción documentada son los mosaicos del mapa |
| F3 | Una dependencia nueva solo entra si no hay solución nativa y se justifica en el Pull Request | YAGNI, WSG 3.12 | 5 paquetes de ejecución; Dependabot y `npm audit` en el CI |
| F4 | Componentes y utilidades compartidas en vez de copias | DRY | `components/ui.tsx`, `components/acciones.tsx` y `components/utilesCrud.ts` los usan varias pantallas |
| F5 | El estado compartido va en contextos pequeños y con `useMemo`; no se memoiza «por si acaso», solo tras medir con el *Profiler* de React | YAGNI | `AuthContext`, `ThemeContext`, `ToastContext` y `ConfirmContext`; sin `React.memo` innecesario |
| F6 | El presupuesto de rendimiento lo vigila el CI, no la memoria del equipo | Green, WSG 3.1 y 5.24 | `green-audit.yml` con `lighthouserc.json` |
| F7 | Toda pantalla se ve bien en ancho móvil, sin desplazamiento horizontal, y mantiene 100 en accesibilidad | Clean Code, inclusión | Pruebas de Playwright en escritorio y celular; Lighthouse en 100 |
| F8 | Si en el futuro se agregan imágenes rasterizadas: WebP o AVIF con `<picture>`, `width` y `height` declarados y `loading="lazy"` salvo en la imagen principal (que lleva `fetchpriority="high"`) | Green, WSG 2.9 | Regla preventiva; hoy no hay imágenes de ese tipo |
| F9 | Una fórmula de huella de carbono se prueba contra una referencia externa | DRY (con una excepción declarada) | La fórmula SWDM v4 existe en Python (`scripts/calcular_huella_swdm.py`, para el informe) y en TypeScript (`huellaDigital.ts`, para el sistema): son dos implementaciones por ser dos lenguajes, y ambas se comprueban con los mismos valores de CO2.js |
| F10 | La pantalla inicial se dibuja con el HTML, sin esperar al JavaScript, y se mide el primer dibujo con la red limitada de verdad además del modo simulado | Green, WSG 3.7 | `index.html` con la cáscara y el CSS en línea; el informe 01 (5.9) compara los dos modos de medición |

---

## 6. Matriz de mapeo: las 8 optimizaciones frente a los estándares

| # | Optimización (informe 01) | ISO/IEC 25010 | GSF | W3C WSG | Estado |
|---|---|---|---|---|---|
| 1 | Consultas e índices de PostgreSQL (5.1) | Eficiencia de desempeño: comportamiento temporal y utilización de recursos | Eficiencia energética | 3.16 | Con ANTES y DESPUÉS (índice y `JOIN LATERAL`, HT-11) y por diseño (columnas necesarias, sin ORM) |
| 2 | Paginación (5.2) | Eficiencia de desempeño: capacidad | Eficiencia energética | 3.16 y 4.2 (menos datos que viajan y se guardan) | Con ANTES y DESPUÉS: de 50 a 12 pedidos por página; el resto de las listas, justificado |
| 3 | Imágenes (5.3) | Eficiencia de desempeño: utilización de recursos | Eficiencia de carbono | 2.9 (la «1.2» de la rúbrica) | Por diseño: no hay imágenes PNG ni JPEG; inventario y medición con `svgo` |
| 4 | Carga diferida y división de código (5.4) | Mantenibilidad: modularidad; eficiencia: utilización de recursos | Eficiencia energética y de hardware (menos CPU en el celular) | 3.3 y 3.7 | Con ANTES y DESPUÉS |
| 5 | Dependencias y APIs nativas (5.5) | Mantenibilidad: analizabilidad | Eficiencia de carbono | 3.2 y 3.12 | Por diseño: APIs nativas y 5 dependencias; costo evitado medido (46.4 KB comprimidos) |
| 6 | Peticiones HTTP, terceros y SVG en línea (5.6) | Eficiencia de desempeño: comportamiento temporal | Eficiencia de carbono | 3.5 y 2.11 | Con ANTES y DESPUÉS (fuentes y CSS: de 4 peticiones de terceros a 0) y por diseño (iconos SVG en línea) |
| 7 | Caché (5.7) | Eficiencia de desempeño: comportamiento temporal | Eficiencia energética | 4.2 (la «2.4» de la rúbrica) | Con ANTES y DESPUÉS (`immutable`, verificado en producción) y por diseño (`no-store` en la API) |
| 8 | Compresión de la API (5.8) | Eficiencia de desempeño: capacidad | Eficiencia de carbono | 4.3 (la «3.1» de la rúbrica) | Por la plataforma (gzip en Render y Brotli en Vercel), con medición |
| — | Presupuesto en CI (8) | Mantenibilidad: capacidad de ser probado | Eficiencia de carbono (medición) | 3.1, 5.24 y 2.15 | Implementado |
| — | Cáscara de la aplicación y CSS en línea (5.9) | Eficiencia de desempeño: comportamiento temporal | Eficiencia energética y de hardware (menos espera en el celular) | 3.7 y 3.2 | Implementada y medida en producción |
| — | Cálculo SWDM v4 (7) | Analizabilidad | Eficiencia de carbono (medición) | 5.5 | Implementado y verificado |
| — | Huella digital dentro del sistema (7.5) | Analizabilidad | Eficiencia de carbono (medición) | 5.5 | Implementada, probada y verificada en producción |
| — | Historial y proyección de emisiones en el dashboard (7.6) | Analizabilidad | Eficiencia de carbono (medición y seguimiento de la meta) | 5.5 y 5.24 | Implementada y probada |

---

## 7. Verificación de los ocho estándares del proyecto

El README declara ocho estándares de referencia. Este es su estado, con la evidencia y las brechas:

| Estándar | Estado | Evidencia |
|---|---|---|
| W3C (HTML válido) | Cubierto | 0 errores y 0 avisos en las 6 pantallas ([accesibilidad WCAG](../../Sprint%203/Implementaci%C3%B3n/07%20Evaluaci%C3%B3n%20de%20accesibilidad%20WCAG%20V_1_0_0.md)) |
| OWASP Top 10 | Cubierto | [Evaluación de seguridad](../../Sprint%203/Implementaci%C3%B3n/06%20Evaluaci%C3%B3n%20de%20seguridad%20OWASP%20V_1_2_0.md) |
| WCAG 2.2 AA | Cubierto | [Evaluación de accesibilidad](../../Sprint%203/Implementaci%C3%B3n/07%20Evaluaci%C3%B3n%20de%20accesibilidad%20WCAG%20V_1_0_0.md): 36 de 40 criterios evaluados cumplen |
| ISO/IEC 25010 | **Cubierto: las ocho características** | Secciones 2.1 a 2.3 de este documento, cada una con su evidencia y su límite |
| Green Software | Cubierto | Este documento y el [informe 01](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_4_0.md) |
| Ley N° 29733 (datos personales) | **Parcial: controles técnicos y procedimientos definidos; faltan operarlos, anonimizar e inscribir el banco de datos** | Sección 7.2 |
| DS 033-2001-MTC | Cubierto | Velocidades por tipo de vía; se corrigió que el decreto «2012» citado inicialmente no existe |
| ISO 14083 | **Parcial: método por distancia coherente, sin cumplir la norma completa; plan de cierre definido** | Sección 7.1 |

### 7.1 ISO 14083 (emisiones de gases de efecto invernadero del transporte)

**ISO 14083** es la norma internacional para cuantificar e informar las emisiones de gases de efecto invernadero de las operaciones de transporte (las del marco GLEC la usan). **Alcance de esta verificación:** se hizo a partir del resumen público de la norma y del código del sistema; la norma completa es de pago y no se consultó, así que esto **no sustituye una auditoría**.

El motor calcula las emisiones de cada ruta como `distancia (km) × factor de emisión del vehículo (kg de CO₂ por km)` (regla RN-009; [`evaluacion.py`](../../../../backend/src/algoritmo/evaluacion.py)), y el dashboard y el reporte PDF las suman.

| Aspecto | Qué pide la norma (en términos generales) | RouteZero | Evaluación |
|---|---|---|---|
| Alcance | Emisiones de las operaciones de transporte de una flota | Emisiones por ruta, por jornada y por periodo, con su reporte | Coherente |
| Datos de actividad | Datos primarios por vehículo cuando existen | La distancia sale de la ruta calculada y el factor es **propio de cada vehículo**, registrado por el administrador | Coherente; el factor no lleva fuente documentada |
| Gases | CO₂ equivalente (CO₂, CH₄ y N₂O) | Solo CO₂ | **Brecha** |
| Alcance de la energía | Ciclo completo del combustible (*well-to-wheel*: producción más combustión) | El sistema no distingue si el factor registrado es solo de combustión (*tank-to-wheel*) o del ciclo completo | **Brecha** |
| Intensidad | Emisiones por tonelada-kilómetro transportada | No se calcula; solo kg totales y kg por ruta | **Brecha** |
| Asignación | Reparto de las emisiones entre los envíos transportados | No se reparte entre pedidos | **Brecha** |
| Transparencia | Declarar método, supuestos e incertidumbre | El reporte PDF incluye «supuestos y notas»; no se informa incertidumbre | Parcial |
| Verificabilidad | Cálculo reproducible | Pruebas automáticas de la fórmula contra la base (`test_sostenibilidad.py`) | Coherente |

**Conclusión.** El cálculo es coherente con un método **basado en distancia con factor por vehículo**, que es una aproximación razonable para el alcance académico del proyecto, pero **no cumple ISO 14083 completa**. Para cumplirla faltaría informar CO₂e, definir si el factor es del ciclo completo, calcular la intensidad por tonelada-kilómetro y repartir las emisiones entre envíos. La conversión de los factores de ejemplo de kg/L a kg/km (informe 01, sección 7.6) es parte de mantener coherente este cálculo.

#### 7.1.1 Plan para cerrar las brechas

Estas mejoras **no se implementaron en esta actividad**: exigen cambios del esquema de la base, del cálculo del reporte y de la interfaz, y no forman parte de la rúbrica de la Inspección 04. Quedan definidas para que el cierre sea concreto:

| Brecha | Qué se cambiaría en el sistema | Dónde |
|---|---|---|
| Solo CO₂ (falta CO₂e) | Agregar a cada vehículo un factor en CO₂e (CO₂ más metano y óxido nitroso) y mostrarlo en el dashboard y en el PDF | Migración de `vehiculos`, `service.py` y `reporte.py` de sostenibilidad, pantalla Sostenibilidad |
| Combustión o ciclo completo | Registrar el tipo de combustible y usar factores del ciclo completo (producción más combustión) de una fuente publicada, citándola en «supuestos y notas» | Migración de `vehiculos`, reporte PDF |
| Sin intensidad por tonelada-kilómetro | Calcular por cada tramo la carga a bordo × la distancia del tramo (los tramos ya existen para el mapa) y mostrar kg de CO₂e por tonelada-kilómetro por ruta y por periodo | `rutas/trazado.py`, repositorio de sostenibilidad, dashboard |
| Sin reparto entre envíos | Repartir las emisiones de cada ruta entre sus pedidos en proporción a su peso × la distancia recorrida hasta su entrega | Servicio de sostenibilidad y reporte |
| Sin fuente ni incertidumbre | Guardar la fuente de cada factor y declarar un rango de incertidumbre en el reporte | Campo nuevo en `vehiculos` y reporte PDF |

### 7.2 Ley N° 29733 (protección de datos personales del Perú)

La **Ley N° 29733** regula el tratamiento de datos personales; su reglamento es el D. S. N° 003-2013-JUS. El único dato personal que trata RouteZero es el de los **conductores** (nombre, DNI, teléfono, correo opcional y licencia); los clientes son negocios.

| Principio o requisito | Qué exige (en términos generales) | Evidencia | Brecha |
|---|---|---|---|
| Consentimiento | Consentimiento previo, libre e informado | `consentimiento_datos` y `consentimiento_en` obligatorios, con una restricción `CHECK` en la base (RN-013): sin consentimiento no se registra al conductor | No hay un flujo documentado para retirar el consentimiento |
| Finalidad y proporcionalidad | Pedir solo los datos necesarios para la finalidad | Solo los datos necesarios para asignar rutas y comprobar la licencia y el horario; el DNI **nunca** se escribe en la auditoría | No hay una política de retención de datos |
| Seguridad | Medidas técnicas y organizativas | Las fichas de conductores solo las gestiona el administrador (RN-014), RLS, verificación en dos pasos y sesiones seguras; HTTPS en Vercel y Render | El DNI está en texto plano en la base (sin cifrado a nivel de columna), declarado en el [documento de OWASP](../../Sprint%203/Implementaci%C3%B3n/06%20Evaluaci%C3%B3n%20de%20seguridad%20OWASP%20V_1_2_0.md) |
| Derechos de acceso, rectificación, cancelación y oposición | Atender las solicitudes de la persona titular | El administrador puede **consultar** la ficha de un conductor, **editarla** (rectificación) y **eliminarla** (cancelación); cada acción queda en la auditoría (`conductor_registrado`, `conductor_editado` y `conductor_eliminado`) **sin escribir el DNI** | Si el conductor ya tiene rutas, la ficha no se puede eliminar (solo marcarse como no disponible) y sus datos personales permanecen: **no hay anonimización**. Falta un procedimiento escrito (7.2.1) |
| Registro del banco de datos | Inscribir el banco de datos ante la Autoridad Nacional de Protección de Datos Personales | — | No realizado: es un proyecto académico con datos ficticios; en una operación real habría que inscribirlo |

**Conclusión.** Hay controles técnicos reales (consentimiento verificado por la base, acceso restringido, exclusión del DNI de la auditoría y funciones de consulta, edición y eliminación de fichas). Los procedimientos organizativos se definen en 7.2.1, pero **todavía no se operan**, y faltan la anonimización de fichas con rutas y la inscripción del banco de datos. El estado se mantiene como **parcial**.

#### 7.2.1 Procedimientos definidos por el equipo

Son una **propuesta del equipo** para este proyecto académico y no constituyen asesoría legal; los plazos y requisitos exactos deben tomarse de la ley y de su reglamento (D. S. N° 003-2013-JUS) al aplicarlos en una operación real. Los ejecuta el **administrador** de Andina Reparto.

| Procedimiento | Pasos |
|---|---|
| **A. Retiro del consentimiento o solicitud de cancelación** | 1) El conductor lo pide por escrito al administrador. 2) El administrador verifica su identidad. 3) Desde la pantalla Conductores marca la ficha como **no disponible**, para que no reciba más rutas. 4) Si la ficha **no tiene rutas**, la elimina; la auditoría registra `conductor_eliminado` sin el DNI. 5) Si **tiene rutas**, conserva solo lo necesario para el historial de las jornadas y, hasta que exista la anonimización (7.1.1 y 7.2), deja constancia del motivo. 6) Responde por escrito al conductor |
| **B. Atención de solicitudes de acceso, rectificación u oposición** | 1) Recibe la solicitud por escrito y la registra con su fecha. 2) **Acceso:** entrega al conductor los datos de su ficha. 3) **Rectificación:** edita la ficha (`conductor_editado` queda en la auditoría). 4) **Oposición:** si el uso de los datos no es necesario para asignar rutas, deja la ficha como no disponible. 5) Responde por escrito dentro del plazo legal |
| **C. Retención de datos** | Los datos del conductor se conservan **mientras mantenga relación con la empresa y se le asignen rutas**. Al terminar la relación se aplica el procedimiento A. Las sesiones expiradas se limpian con el job de mantenimiento (`python -m src.auth.mantenimiento`) |

La inscripción del banco de datos ante la Autoridad Nacional de Protección de Datos Personales no se hace en este proyecto académico (datos ficticios).

---

## 8. Glosario

| Término | Explicación breve |
|---|---|
| **ISO/IEC 25010** | Norma internacional con el modelo de calidad del producto de software (características y subcaracterísticas) |
| **Eficiencia de desempeño** | Característica de calidad: rendimiento en relación con los recursos usados (tiempo, recursos y capacidad) |
| **Mantenibilidad** | Característica de calidad: facilidad para modificar el software (modularidad, reusabilidad, analizabilidad, modificabilidad y capacidad de ser probado) |
| **Green Software Foundation (GSF)** | Organización de la Linux Foundation que define prácticas para reducir el carbono del software |
| **Eficiencia de carbono** | Emitir el menor carbono posible por cada unidad de trabajo |
| **Eficiencia energética** | Consumir la menor electricidad posible |
| **Eficiencia de hardware** | Usar menos equipos y por más tiempo, para reducir la fabricación |
| **Conciencia de carbono** | Adaptar cuándo y dónde se ejecuta el trabajo a la limpieza de la electricidad |
| **Carbono incorporado (*embodied*)** | Emisiones de fabricar y desechar el hardware |
| **SCI** | *Software Carbon Intensity*: especificación de la GSF para medir la intensidad de carbono del software |
| **W3C** | World Wide Web Consortium: organismo que define los estándares de la web |
| **WSG** | *Web Sustainability Guidelines*: pautas de W3C para una web sostenible, con criterios de éxito verificables |
| **Group Note Draft** | Estado de una publicación de W3C: borrador de un grupo, no es un estándar aprobado |
| **Clean Code** | Conjunto de prácticas para escribir código legible y fácil de mantener |
| **SOLID** | Cinco principios de diseño: responsabilidad única, abierto/cerrado, sustitución de Liskov, segregación de interfaces e inversión de dependencias |
| **DRY** | No repetir el mismo conocimiento en varios lugares |
| **YAGNI** | No construir funciones antes de necesitarlas |
| **Patrón Repository** | Capa que concentra el acceso a la base de datos para que el resto del sistema no escriba SQL |
| **Inyección de dependencias** | Recibir lo que una función necesita desde afuera (en FastAPI, con `Depends`) en lugar de crearlo adentro |
| **SonarQube** | Herramienta que analiza el código y detecta errores, vulnerabilidades y deuda técnica |
| **Cobertura de pruebas** | Porcentaje del código que ejecutan las pruebas automáticas |
| **OWASP Top 10** | Lista de los diez riesgos de seguridad más comunes en aplicaciones web |
| **WCAG** | *Web Content Accessibility Guidelines*: pautas de accesibilidad web (nivel AA) |
| **`Profiler` de React** | Herramienta que mide qué componentes se vuelven a dibujar y cuánto cuesta |
| **ISO 14083** | Norma internacional para cuantificar e informar las emisiones de gases de efecto invernadero del transporte |
| **CO₂e (dióxido de carbono equivalente)** | Unidad que expresa todos los gases de efecto invernadero (CO₂, metano, óxido nitroso) en su equivalente en CO₂ |
| ***Well-to-wheel* / *tank-to-wheel*** | Emisiones del ciclo completo del combustible (de la producción a la rueda) / solo las de su combustión en el vehículo |
| **Tonelada-kilómetro (t·km)** | Unidad de trabajo de transporte: una tonelada llevada un kilómetro; con ella se mide la intensidad de emisiones |
| **Ley N° 29733** | Ley peruana de protección de datos personales |
| **Anonimización** | Quitar o alterar los datos personales de un registro para que ya no identifique a una persona, conservando el resto para fines estadísticos |
| **ANPD** | Autoridad Nacional de Protección de Datos Personales del Perú |
| **Derechos ARCO** | Derechos de acceso, rectificación, cancelación y oposición de la persona sobre sus datos |
| **Cáscara de la aplicación (*app shell*)** | HTML mínimo visible de inmediato mientras carga el JavaScript (informe 01, sección 5.9) |

---

[← Volver al README Principal](../../../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-11-09 | Versión inicial: fundamentación en ISO/IEC 25010, Green Software Foundation y W3C WSG (con su numeración oficial), guía de desarrollo verde para backend y frontend, matriz de mapeo de las 8 optimizaciones y estado de los demás estándares | Inciso Aguilar Elizabeth Antonela |
| V_1_1_0 | 2026-11-10 | Se agregan la huella digital dentro del sistema (WSG 5.5, GSF y matriz), las reglas B8 (cabecera `Timing-Allow-Origin`) y F9 (una fórmula, dos lenguajes, una referencia) y se actualiza el número de pruebas (360, 166 y 34) | Inciso Aguilar Elizabeth Antonela |
| V_1_2_0 | 2026-11-10 | Se agrega el historial y la proyección de emisiones del dashboard a la matriz (WSG 5.5 y 5.24) y se actualiza el número de pruebas (360, 178 y 35) y los enlaces al informe 1.2.0 | Inciso Aguilar Elizabeth Antonela |
| V_1_3_0 | 2026-11-10 | Se agrega la equivalencia entre la numeración de la rúbrica y la oficial de W3C (1.1), las ocho características de ISO/IEC 25010 con su evidencia y su límite (2.3), la verificación de ISO 14083 con su plan de cierre y de la Ley N° 29733 con sus procedimientos definidos y sus brechas (7.1 y 7.2), la regla F10 y la fila de la cáscara en la matriz | Inciso Aguilar Elizabeth Antonela |
| V_1_4_0 | 2026-11-12 | Versión final: se actualizan los enlaces al informe 1.4.0, la paginación de pedidos pasa a 12 en la matriz y se ajusta la redacción de la regla B6 sobre `no-store` | Inciso Aguilar Elizabeth Antonela |
