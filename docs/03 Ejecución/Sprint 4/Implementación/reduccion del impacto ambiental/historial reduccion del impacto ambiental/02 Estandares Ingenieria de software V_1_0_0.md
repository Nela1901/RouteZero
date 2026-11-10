# 02 Estándares de Ingeniería de Software y Guía de Desarrollo Verde

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Líder del Proyecto** | Inciso Aguilar Elizabeth Antonela |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Actividad** | Inspección 04 — Green Software y verificación de estándares (actividad de cierre del Sprint 4) |
| **Fecha** | 2026-11-09 |
| **Estándares aplicados** | ISO/IEC 25010, principios de la Green Software Foundation, W3C Web Sustainability Guidelines, Clean Code, SOLID, DRY y YAGNI |
| **Documento hermano** | [01 Informe de Reducción del Impacto Ambiental](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md) |
| **Versión** | 1.0.0 |

[← Volver al README Principal](../../../../../../README.md)

---

## 1. Propósito y alcance

Este documento fundamenta en estándares las mejoras del [informe de reducción del impacto ambiental](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md), define las reglas de desarrollo verde que sigue el equipo para el backend y el frontend, y cruza cada una de las 8 áreas de optimización con los estándares en una matriz (sección 6).

**Nota sobre la numeración de W3C.** Las *Web Sustainability Guidelines* (WSG, Pautas de Sostenibilidad Web) de W3C están publicadas como **Group Note Draft del 16 de octubre de 2026** (borrador del Grupo de Interés en Web Sostenible; el documento no se rotula «1.0»). Su numeración oficial es: **2.x** Diseño de experiencia de usuario, **3.x** Desarrollo web, **4.x** Hosting, infraestructura y sistemas, y **5.x** Estrategia de negocio y gestión de producto; la sección 1 es solo introducción. Este documento cita siempre **la numeración oficial**. Los materiales de la actividad hablan de «pautas 1.2, 2.4 y 3.1» con tres temas (optimización de medios, arquitectura y caché, transferencia de red); esos temas se corresponden con las pautas oficiales **2.9, 4.2 y 4.3** (y 3.1), como se explica en la sección 4.

---

## 2. ISO/IEC 25010: eficiencia de desempeño y mantenibilidad

**ISO/IEC 25010** es el modelo internacional de calidad del producto de software: define características de calidad y las subdivide en subcaracterísticas medibles. La actividad se apoya en dos: la **eficiencia de desempeño** (qué tan bien rinde el software con los recursos que usa) y la **mantenibilidad** (qué tan fácil es cambiarlo). El requisito no funcional que las motiva es **RNF-011, Eficiencia energética** (ver [`07. Requisitos no funcionales`](../../../../../01%20Inicio/07.%20Requisitos%20no%20funcionales%20V_1_2_0.md)).

### 2.1 Eficiencia de desempeño

| Subcaracterística | Qué mide | Cómo se aplicó en RouteZero | Evidencia |
|---|---|---|---|
| **Comportamiento temporal** (*time behaviour*) | Tiempos de respuesta y de procesamiento | Carga diferida y fuentes propias reducen el FCP y el LCP; índices y consultas acotadas bajan los tiempos de la base | FCP móvil 2.18 → 1.66 s; LCP de escritorio 797 → 488 ms; 17 consultas críticas ≤ 42 ms (informe 01, secciones 5.1, 5.4 y 5.6) |
| **Utilización de recursos** (*resource utilization*) | Cantidad de recursos (red, CPU, memoria) que consume | Menos bytes transferidos y menos JavaScript que ejecutar en el celular del conductor | Peso 213 → 140 KB en móvil (−34 %); JavaScript inicial −49 %; TBT de 0 ms |
| **Capacidad** (*capacity*) | Límites que soporta el sistema | Paginación de la tabla que más crece (pedidos, máximo 200 por página); el motor de rutas se probó con 150 pedidos y 15 vehículos | Informe 01, sección 5.2; mediciones de generación y re-optimización de los sprints 2 y 3 |

### 2.2 Mantenibilidad

| Subcaracterística | Qué mide | Cómo se aplicó en RouteZero | Evidencia |
|---|---|---|---|
| **Modularidad** | Cambiar una parte sin afectar al resto | Backend organizado por características; ningún módulo de negocio importa a otro. Frontend dividido en un trozo de código por pantalla | [`test_arquitectura.py`](../../../../../../backend/tests/test_arquitectura.py) vigila la independencia; trozos de la sección 5.4 del informe 01 |
| **Reusabilidad** | Reutilizar componentes en varios lugares | Componentes y utilidades compartidas en lugar de copias | `utilesCrud.ts` lo usan 4 pantallas y `ui.tsx`; `ui.tsx` y `acciones.tsx` los usan 9 archivos |
| **Analizabilidad** | Entender y diagnosticar el sistema | Comentarios que explican el porqué, documentación por sprint, auditorías con script | [Calidad de código](../../../../Sprint%203/Implementaci%C3%B3n/05%20Calidad%20de%20c%C3%B3digo%20V_1_2_0.md) (SonarQube); `auditar_consultas.py` |
| **Modificabilidad** | Cambiar sin introducir defectos | Parámetros que se ajustan sin tocar la lógica (precio del combustible, meta mensual, factores de congestión) | `backend/src/core/config.py`, `backend/src/rutas/congestion.py` |
| **Capacidad de ser probado** (*testability*) | Facilidad de verificar | Pruebas automáticas en las tres capas | 359 de backend (cobertura de 98 %), 147 de Vitest y 33 de extremo a extremo |

---

## 3. Green Software Foundation: los cuatro principios

La **Green Software Foundation (GSF)** es una organización de la Linux Foundation que define cómo construir software con menos carbono. Su enfoque se resume en **cuatro principios**, de los cuales la eficiencia de carbono es el objetivo general y los otros tres son las únicas actividades que reducen de verdad las emisiones del software.

| Principio | Qué significa | Cómo se aplicó | Lo que **no** se hace |
|---|---|---|---|
| **Eficiencia de carbono** | Emitir la menor cantidad de carbono posible por cada unidad de trabajo | Se mide la huella con SWDM v4 y se vigila con un presupuesto en CI (informe 01, secciones 7 y 8); el sistema optimiza rutas para gastar menos combustible | La huella del hosting no se reduce: no es hosting verde |
| **Eficiencia energética** | Usar la menor electricidad posible | Menos bytes, menos JavaScript, consultas con índice, motor de rutas con presupuesto de tiempo (25 s) y sin llamadas a servicios externos en funcionamiento | Brotli propio: la plataforma ya comprime y duplicarlo gastaría CPU |
| **Eficiencia de hardware** | Reducir la fabricación de equipos (carbono incorporado) y alargar su vida útil | Páginas livianas que funcionan bien en celulares de gama media, sin exigir equipos nuevos; el módulo de sostenibilidad calcula el costo del ciclo de vida de la flota | Sin evaluación del hardware del proveedor de hosting |
| **Conciencia de carbono** | Hacer más trabajo cuando la electricidad es más limpia y menos cuando es más sucia | El pipeline de auditoría solo se ejecuta cuando cambia el frontend, para no gastar cómputo en cambios que no pueden afectar el rendimiento | **No** se desplazan tareas según la intensidad de la red eléctrica. Se declara como brecha |

La GSF también publica otros marcos (por ejemplo, un conjunto de ocho principios y la especificación SCI, *Software Carbon Intensity*); aquí se usan los cuatro anteriores, que son los que pide la actividad.

---

## 4. W3C Web Sustainability Guidelines (WSG)

Las **WSG** son pautas del W3C para que los sitios y aplicaciones web sean más sostenibles. Cada pauta tiene criterios de éxito verificables. La tabla relaciona las pautas oficiales (numeración y títulos de la publicación del 16-10-2026) con la evidencia del proyecto. Los números entre paréntesis remiten a las secciones del [informe 01](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md).

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
| **5.5** | Calcular el impacto ambiental | Cálculo con SWDM v4 verificado contra CO2.js (7) |
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
| B6 | La seguridad no se sacrifica por rendimiento | Clean Code, OWASP | Las respuestas de la API llevan `Cache-Control: no-store`; por eso no hay caché de datos en el cliente |
| B7 | Todo cambio de lógica lleva pruebas; la cobertura no baja | Clean Code | 359 pruebas, cobertura de 98 %; análisis de SonarQube, Bandit y `pip-audit` |

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

---

## 6. Matriz de mapeo: las 8 optimizaciones frente a los estándares

| # | Optimización (informe 01) | ISO/IEC 25010 | GSF | W3C WSG | Estado |
|---|---|---|---|---|---|
| 1 | Consultas e índices de PostgreSQL (5.1) | Eficiencia de desempeño: comportamiento temporal y utilización de recursos | Eficiencia energética | 3.16 | Cumplida, con evidencia (HT-11) |
| 2 | Paginación (5.2) | Eficiencia de desempeño: capacidad | Eficiencia energética | 3.16 y 4.2 (menos datos que viajan y se guardan) | Parcial: pedidos paginado; el resto, justificado |
| 3 | Imágenes (5.3) | Eficiencia de desempeño: utilización de recursos | Eficiencia de carbono | 2.9 | «No aplica», medida con `svgo` |
| 4 | Carga diferida y división de código (5.4) | Mantenibilidad: modularidad; eficiencia: utilización de recursos | Eficiencia energética y de hardware (menos CPU en el celular) | 3.3 y 3.7 | Implementada |
| 5 | Dependencias (5.5) | Mantenibilidad: analizabilidad | Eficiencia de carbono | 3.2 y 3.12 | Ya mínima, con controles automáticos |
| 6 | Peticiones HTTP y terceros (5.6) | Eficiencia de desempeño: comportamiento temporal | Eficiencia de carbono | 3.5 y 2.11 | Implementada |
| 7 | Caché (5.7) | Eficiencia de desempeño: comportamiento temporal | Eficiencia energética | 4.2 | Implementada (verificación en producción pendiente del despliegue) |
| 8 | Compresión de la API (5.8) | Eficiencia de desempeño: capacidad | Eficiencia de carbono | 4.3 | Cubierta por la plataforma, con medición |
| — | Presupuesto en CI (8) | Mantenibilidad: capacidad de ser probado | Eficiencia de carbono (medición) | 3.1, 5.24 y 2.15 | Implementado |
| — | Cálculo SWDM v4 (7) | Analizabilidad | Eficiencia de carbono (medición) | 5.5 | Implementado y verificado |

---

## 7. Estado de los demás estándares del proyecto

El README declara ocho estándares de referencia. Este es su estado, con la evidencia donde ya existe:

| Estándar | Estado | Evidencia |
|---|---|---|
| W3C (HTML válido) | Cubierto | 0 errores y 0 avisos en las 6 pantallas ([accesibilidad WCAG](../../../../Sprint%203/Implementaci%C3%B3n/07%20Evaluaci%C3%B3n%20de%20accesibilidad%20WCAG%20V_1_0_0.md)) |
| OWASP Top 10 | Cubierto | [Evaluación de seguridad](../../../../Sprint%203/Implementaci%C3%B3n/06%20Evaluaci%C3%B3n%20de%20seguridad%20OWASP%20V_1_2_0.md) |
| WCAG 2.2 AA | Cubierto | [Evaluación de accesibilidad](../../../../Sprint%203/Implementaci%C3%B3n/07%20Evaluaci%C3%B3n%20de%20accesibilidad%20WCAG%20V_1_0_0.md): 36 de 40 criterios evaluados cumplen |
| ISO/IEC 25010 | Cubierto en dos características | Sección 2 de este documento (eficiencia de desempeño y mantenibilidad) |
| Green Software | Cubierto | Este documento y el [informe 01](01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md) |
| Ley N° 29733 (datos personales) | Parcial | Consentimiento del conductor y DNI fuera de la auditoría; la brecha del DNI en texto plano está declarada en el documento de OWASP |
| DS 033-2001-MTC | Cubierto | Velocidades por tipo de vía; se corrigió que el decreto «2012» citado inicialmente no existe |
| ISO 14083 | **Sin verificar** | Solo está listada; no se comprobó que el cálculo de emisiones de rutas la respete. Queda fuera de esta actividad |

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

---

[← Volver al README Principal](../../../../../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-11-09 | Versión inicial: fundamentación en ISO/IEC 25010, Green Software Foundation y W3C WSG (con su numeración oficial), guía de desarrollo verde para backend y frontend, matriz de mapeo de las 8 optimizaciones y estado de los demás estándares | Inciso Aguilar Elizabeth Antonela |
