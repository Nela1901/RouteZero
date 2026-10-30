# 06 Reporte de Seguridad OWASP Top 10 (2025)

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Líder del Proyecto** | Inciso Aguilar Elizabeth Antonela |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Sprint** | Sprint 3 — Rutas y Visualización (Inspección 03) |
| **Fecha de la evaluación** | 2026-10-26 (reanálisis de SonarQube: 2026-10-30) |
| **Herramienta de escaneo** | SonarQube Cloud (primer análisis del 23-10-2026 y reanálisis del 30-10-2026), Bandit, pip-audit, npm audit y revisión manual del código |
| **Versión** | 1.2.0 |

[← Volver al README Principal](../../../../README.md)

---

## 0. Alcance y método

- **Qué se evaluó:** el backend (FastAPI, `backend/src`), el frontend (React, `frontend/src`), la integración continua (`.github/workflows`) y la configuración de despliegue (Render, Vercel y Supabase).
- **Lista usada:** OWASP Top 10:2025 oficial ([owasp.org/Top10/2025](https://owasp.org/Top10/2025/0x00_2025-Introduction/)). La plantilla de la consigna trae nombres de la edición 2021 con la etiqueta «2025» (por ejemplo `A06 Vulnerable and Outdated Components` y `A10 SSRF`). En la matriz se usan los nombres de la edición 2025 y una columna indica a qué fila de la plantilla equivale cada categoría. En 2025, SSRF pasó a formar parte de A01 y apareció `A10 Mishandling of Exceptional Conditions`.
- **Qué clasifica SonarQube:** SonarQube Cloud solo clasifica sus hallazgos con la taxonomía **OWASP 2021** (su API no ofrece la 2025). Por eso la equivalencia a 2025 de las 16 incidencias de seguridad la hicimos nosotros, por regla, y la dejamos explícita en cada fila.
- **Estados:** **Limpio** (sin brechas conocidas), **Bajo revisión** (hay controles pero queda una brecha o algo sin verificar) y **Vulnerable** (brecha abierta explotable). Ninguna categoría está en «Vulnerable»; las brechas explotables que se encontraron se corrigieron en este sprint y están en la sección 2.

## 1. Matriz de Cumplimiento OWASP Top 10 2025

| Categoría OWASP 2025 | Equivale a (plantilla de la consigna) | Estado en Proyecto | Hallazgos de SonarQube |
|---|---|---|---|
| A01:2025 Broken Access Control (incluye SSRF) | A01 Broken Access Control y A10 SSRF | **Limpio** | 3 de severidad alta o bloqueante por *path traversal* en el script `generar_grafo.py`: corregidas quitando las rutas por línea de comandos del script; el reanálisis las cierra |
| A02:2025 Security Misconfiguration | A05 Security Misconfiguration | **Bajo revisión** | Ninguno propio; brechas de revisión manual en la sección 3 |
| A03:2025 Software Supply Chain Failures | A06 Vulnerable and Outdated Components | **Bajo revisión** | 10 en `ci.yml` (scripts de instalación, versiones sin fijar, dependencias sin bloqueo): corregidas y cerradas por SonarQube en el reanálisis. La brecha real de `requirements.txt` sin bloquear sigue en el plan |
| A04:2025 Cryptographic Failures | A02 Cryptographic Failures | **Bajo revisión** | Ninguno; brechas de revisión manual |
| A05:2025 Injection | A03 Injection | **Limpio** | Ninguno |
| A06:2025 Insecure Design | A04 Insecure Design | **Bajo revisión** | No aplica a las reglas de SonarQube; brechas de revisión manual |
| A07:2025 Authentication Failures | A07 Identification and Authentication Failures | **Bajo revisión** | 3 por contraseñas escritas en el código de las pruebas de extremo a extremo (credenciales falsas de una API simulada): el reanálisis ya no las informa |
| A08:2025 Software or Data Integrity Failures | A08 Software and Data Integrity Failures | **Bajo revisión** | Ninguno; brechas de revisión manual |
| A09:2025 Security Logging and Alerting Failures | A09 Security Logging and Monitoring Failures | **Bajo revisión** | Ninguno; brechas de revisión manual |
| A10:2025 Mishandling of Exceptional Conditions | (no existe en la plantilla; reemplaza a SSRF) | **Limpio** (corregido en este sprint) | Ninguno; hallazgo propio corregido |

**Resultado del reanálisis (30-10-2026): 0 vulnerabilidades abiertas, 0 Security Hotspots y calificación de seguridad A.** Las 18 vulnerabilidades que registró SonarQube (las 16 del primer análisis y 2 que aparecieron en scripts modificados) quedaron **todas cerradas, sin falsos positivos**: 17 corregidas en el código y 1 por excluir del análisis el script de apoyo `preparar_cobertura.py` (sección 2).

**Total de las 16 incidencias de seguridad del primer análisis:** 3 (A01) + 10 (A03) + 3 (A07) = 16. SonarQube, con su taxonomía 2021, clasificó solo 5 de ellas (`a1`: 1, `a3`: 1, `a7`: 3); las otras 11 las ubicamos por el tipo de regla.

## 2. Detalles de Security Hotspots y Vulnerabilidades Críticas

En el primer análisis SonarQube Cloud muestra **0 Security Hotspots** como pestaña aparte: en su versión actual aparecen dentro de las vulnerabilidades, con la etiqueta *former-hotspot*. Hubo 16 vulnerabilidades (1 bloqueante y 15 mayores). **En el reanálisis del 30-10 no queda ninguna abierta** (calificación de seguridad A, esfuerzo de remediación 0).

### Hallazgos de SonarQube

- **Hotspot #1 — *Path traversal* en `backend/scripts/generar_grafo.py` (bloqueante, 3 incidencias).** El script, que regenera el grafo de calles y se ejecuta a mano, leía y escribía las rutas que recibía por la línea de comandos sin validarlas. No está expuesto a la red, pero un valor como `../../archivo` podía salirse de la carpeta. **Mitigación:** primero se validaron las rutas, pero SonarQube no reconoce esa validación y seguía informando el aviso; la corrección definitiva fue **quitar del script las rutas y las opciones de la línea de comandos**: ahora solo descarga de Overpass y escribe el grafo en una ubicación fija. Se comprobó que el grafo que genera es idéntico al anterior. Otro aviso de la misma regla en `scripts/preparar_cobertura.py`, un paso de apoyo del propio análisis, se resolvió excluyendo ese script del análisis.
- **Hotspot #2 — Scripts de instalación y `npx` en el CI (`.github/workflows/ci.yml`, 8 incidencias).** `npm ci` ejecutaba los scripts de ciclo de vida de cada paquete y `npx` podía descargar paquetes sin versión fija. **Mitigación:** `npm ci --ignore-scripts`, scripts de npm en lugar de `npx`, y Bandit y pip-audit con versión exacta e instalación solo de paquetes binarios (`--only-binary :all:`). Se comprobó en una copia limpia que el build y las pruebas siguen pasando.
- **Hotspot #3 — Dependencias de Python sin bloquear (`ci.yml`, 2 incidencias).** SonarQube las cerró todas en el reanálisis, pero **la brecha real sigue**: `backend/requirements.txt` usa rangos de versión y no un archivo bloqueado con sumas de verificación (ver A03 y el plan de la sección 5).
- **Hotspot #4 — Contraseñas en `frontend/e2e/api.ts` (3 incidencias, severidad mayor).** Son credenciales **falsas** de una API simulada en el navegador, que se usan solo en las pruebas de extremo a extremo; no existen en Supabase ni dan acceso a nada. El reanálisis ya no las informa.

### Hallazgos propios de la revisión (SonarQube no los detectó)

| Categoría | Hallazgo | Gravedad | Corrección |
|---|---|---|---|
| A02 | **CORS no permitía PATCH:** el navegador rechazaba el permiso previo (`400 Disallowed CORS method`) y registrar una entrega desde la vista del conductor, en Vercel hacia Render, fallaba. Las pruebas no lo veían porque simulan la API en el mismo origen | Alta (funcional) | Se agregó PATCH y una prueba por cada método que usa el frontend |
| A05 | El código QR del MFA se mostraba inyectando su SVG como HTML (`dangerouslySetInnerHTML`): un SVG con script llegaría a ejecutarse | Media | Ahora es una imagen (`<img>`), donde un SVG no puede ejecutar scripts |
| A10 | La API no tenía manejo propio para una base de datos o un proveedor de autenticación que no respondan (como en la caída de Supabase del 20-10, IMP-018): el resultado era el 500 genérico del servidor | Media | Respuesta 503 con un mensaje claro y sin detalles de conexión, con pruebas |
| A07 / A10 | Supabase rechazaba un código MFA **correcto** cuando el desafío y la verificación salían por IPs distintas (`mfa_ip_address_mismatch`); con Render puede pasar de vez en cuando | Media | El backend repite el desafío hasta 3 veces sin contarlo como intento fallido y responde 503 si persiste; 4 pruebas |
| A02 | Sin cabeceras de seguridad en la API ni en Vercel | Media | `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy` y `Cache-Control: no-store` en `/api/`; las tres primeras y `Permissions-Policy` en Vercel |
| A03 / A08 | Acciones de GitHub fijadas por etiqueta móvil y sin revisión automática de dependencias | Media | Acciones fijadas a su commit exacto y Dependabot semanal para npm, pip y GitHub Actions |
| A03 | `npm audit` detectó una vulnerabilidad nueva de severidad alta en `undici` (dependencia de `jsdom`) y rompió el CI | Alta | Actualización a `undici` 7.30.1; `npm audit` vuelve a 0 |

## 3. Detalle por categoría

### A01 Broken Access Control — Limpio

- **Controles:**
  - De las 48 operaciones de la API, **45 exigen token** y las 3 públicas son `POST /api/auth/login`, `POST /api/auth/sesiones/renovar` (que valida el token de refresco y la sesión) y `GET /api/health`.
  - Cada módulo de gestión declara su rol con `requiere_rol` (RN-014): flota, conductores, sostenibilidad y auditoría solo para ADMINISTRADOR; clientes y pedidos para OPERADOR o ADMINISTRADOR; las rutas distinguen administrador, operador y conductor.
  - El conductor solo ve y registra **sus** rutas: otra ruta responde 403 (`test_conductor.py`).
  - Row Level Security en la base de datos como segunda capa: `usuarios` y `sesiones_activas` solo muestran la fila propia.
  - SSRF: el backend solo hace peticiones salientes a Supabase, con una dirección fija de las variables de entorno; ninguna dirección la decide la persona usuaria.
- **Brechas:** ninguna conocida.

### A02 Security Misconfiguration — Bajo revisión

- **Controles:**
  - CORS con el origen exacto del frontend, sin comodín y sin credenciales.
  - Cabeceras de seguridad (sección 2) probadas con 10 pruebas.
  - Los secretos están solo en variables de entorno: `.env` está en `.gitignore`, `.env.example` no trae valores y no se usa la clave `service_role`.
  - Los roles de la base de datos tienen el mínimo privilegio: `app_backend` no tiene `BYPASSRLS`.
  - HTTPS en Render, Vercel y Supabase.
- **Brechas y acciones:**
  - No hay cabecera `Content-Security-Policy`: se requiere probarla en el navegador contra producción porque la interfaz usa estilos en línea, Leaflet y fuentes de Google.
  - La documentación de la API (`/docs` y `/openapi.json`) es pública en Render. Es útil para la revisión del curso, pero en una operación real debería protegerse o desactivarse.
  - Los tokens de sesión se guardan en `localStorage`, lo que los expone si hubiera una falla de XSS (ver A05); la alternativa es una cookie `HttpOnly`.

### A03 Software Supply Chain Failures — Bajo revisión

- **Controles:**
  - `pip-audit`, `npm audit --audit-level=high` y Bandit se ejecutan en **cada Pull Request**. Esta semana el propio CI detectó la vulnerabilidad nueva de `undici` y bloqueó la fusión hasta corregirla.
  - `package-lock.json` más `npm ci` en el frontend.
  - Acciones de GitHub fijadas por commit y Dependabot semanal.
  - Se verificó que las dependencias nuevas (`fpdf2`, `pypdf`) no traen vulnerabilidades conocidas.
- **Brechas y acciones:**
  - `backend/requirements.txt` usa rangos de versión y no un archivo bloqueado con sumas de verificación (SonarQube dejó de señalarlo al fijar las herramientas del CI, pero la brecha del backend sigue). Render instala lo que resuelve en ese momento.
  - Dependabot ya abrió 9 Pull Request de actualización que hay que revisar y fusionar o cerrar.

### A04 Cryptographic Failures — Bajo revisión

- **Controles:**
  - Cifrado en tránsito en todos los saltos. La conexión a la base exige TLS (`sslmode=require`) y hay 2 pruebas que lo comprueban.
  - Los tokens JWT usan firma ES256, verificada con las claves públicas del proveedor (JWKS).
  - Las contraseñas y los secretos TOTP los gestiona Supabase Auth: el sistema nunca los guarda.
  - Los tokens de refresco se guardan solo como **hash SHA-256**, nunca en claro.
- **Brechas y acciones:** el DNI de los conductores se guarda en texto plano en la base de datos (dato personal, Ley N° 29733). Está protegido por el consentimiento explícito (RN-013), por el acceso solo de ADMINISTRADOR y por no escribirse nunca en la auditoría, pero no tiene cifrado a nivel de columna. El cifrado en reposo depende de la infraestructura de Supabase y no se puede verificar desde el proyecto.

### A05 Injection — Limpio

- **Controles:**
  - Todas las consultas SQL se construyen con `text()` y **parámetros enlazados**; los pocos nombres de columna que se concatenan son constantes del código (Bandit B608, falsos positivos revisados).
  - Validación de entrada con Pydantic y validadores de texto (58 pruebas en `test_validacion_texto.py`).
  - 6 pruebas de inyección SQL contra clientes, pedidos y el inicio de sesión (`test_seguridad_inyeccion_sql.py`).
  - El frontend usa React, que escapa el contenido; tras corregir el QR no queda ninguna inyección de HTML.
- **Brechas:** ninguna conocida.

### A06 Insecure Design — Bajo revisión

- **Controles:**
  - Defensa en profundidad (rol en la API más Row Level Security).
  - Reglas de negocio en el servidor y no en la interfaz (capacidad, ventanas de tiempo, zona de Huancayo, vencimiento de licencias).
  - Diseño de borrador y confirmación para las rutas.
  - Una sola generación de rutas a la vez por fecha (409 si hay otra en curso).
  - Límites: periodos de 366 días como máximo en sostenibilidad, y 300 rutas como máximo en el PDF.
  - Bloqueo tras 3 intentos fallidos (RN-001).
- **Brechas y acciones:**
  - No hay límite de peticiones por IP en la propia API; el inicio de sesión se limita por el bloqueo de cuenta y por Supabase.
  - El MFA es opcional, también para el administrador.
  - Las operaciones pesadas (generar y re-optimizar rutas, y el PDF) solo se limitan por el rol.

### A07 Authentication Failures — Bajo revisión

- **Controles:**
  - MFA por TOTP; bloqueo tras 3 intentos fallidos de contraseña (15 minutos) y de código; **detección de reutilización del token de refresco** hecha por el backend, que revoca la sesión (`robo_sesion_detectado`).
  - Lista y revocación de sesiones, expiración por inactividad y `token_version`.
  - Mensaje genérico «Credenciales inválidas»: no revela si el correo existe.
  - 31 pruebas de sesiones y MFA contra Supabase real.
  - Esta semana se agregó el reintento ante el cambio de IP de la verificación.
- **Brechas y acciones:**
  - El MFA no es obligatorio.
  - La política de contraseñas depende de la configuración de Supabase, que el repositorio no controla ni verifica; hay que revisarla en el panel.
  - Los tokens están en `localStorage` (ver A02).

### A08 Software or Data Integrity Failures — Bajo revisión

- **Controles:** cambios por Pull Request con CI obligatorio, acciones de GitHub fijadas por commit, migraciones SQL idempotentes y revisadas en `backend/scripts/`, y `package-lock.json`.
- **Brechas y acciones:**
  - **Casi todos los Pull Request de los sprints 3 y 4 se fusionaron sin la aprobación de un compañero** (solo el #60 y el #64 la tuvieron), por lo que el control de cambios depende de una sola persona. Es una brecha de proceso, registrada como IMP-025 y en las retrospectivas.
  - La hoja de estilos de Google Fonts se carga sin integridad de subrecurso (un CSS externo no se puede fijar de forma práctica); la alternativa es alojar las fuentes en el propio proyecto.

### A09 Security Logging and Alerting Failures — Bajo revisión

- **Controles:** la tabla `logs_auditoria` registra **22 tipos de evento** (inicio de sesión exitoso y fallido, activación y desactivación del MFA, código inválido, robo de sesión, revocación de sesiones, y generación, confirmación y descarte de rutas, incidentes, conductores y reportes), con usuario, IP y fecha. Es de solo agregar para la API (`app_backend` solo puede insertar y leer), no guarda datos personales como el DNI y solo el administrador la consulta (`GET /api/auditoria`).
- **Brechas y acciones:**
  - Los cambios en flota, clientes y pedidos no se registran.
  - Los accesos denegados (403) no se registran.
  - No hay alertas: un `robo_sesion_detectado` solo queda en la tabla.
  - No hay política de retención.

### A10 Mishandling of Exceptional Conditions — Limpio

- **Controles:**
  - Los errores de negocio usan códigos HTTP precisos (400, 401, 403, 404, 409, 422, 429).
  - Cualquier excepción inesperada deshace la transacción (`get_db_con_rls`) y la API no devuelve trazas.
  - Se corrigió el caso de Supabase o base de datos caídos (503 con mensaje claro y sin detalles de conexión) y el rechazo de MFA por cambio de IP (reintento).
  - 10 pruebas de seguridad de cabeceras, CORS y 503.
- **Brechas:** ninguna conocida.

## 4. Evidencia de pruebas y análisis

| Verificación | Resultado |
|---|---|
| Pruebas de seguridad del backend | Sesiones 16, MFA 11 más 4 del reintento, cifrado 2, inyección SQL 6, cabeceras y CORS 10 y auditoría 4 |
| Backend completo contra la base real | 363 pruebas pasan; cobertura 98 % |
| Bandit (severidad alta) | 0 hallazgos |
| `pip-audit` | Sin vulnerabilidades |
| `npm audit` (severidad alta) | 0 vulnerabilidades |
| Integración continua | Bandit, pip-audit y npm audit en cada Pull Request |
| SonarQube Cloud (reanálisis del 30-10-2026) | 0 vulnerabilidades, 0 bugs, 0 Security Hotspots, seguridad A y fiabilidad A; Quality Gate aprobado, con la cobertura del código nuevo en 94.3 % y la total en 89.4 % (ver `05 Calidad de código`) |

## 5. Plan de acciones pendientes

| Prioridad | Acción | Categoría |
|---|---|---|
| Alta | Bloquear las dependencias del backend con sumas de verificación y revisar los Pull Request de Dependabot | A03 |
| Alta | Pedir la aprobación de un compañero en cada Pull Request antes de fusionar | A08 |
| Media | Agregar `Content-Security-Policy` en Vercel, probándola en un navegador contra producción | A02 |
| Media | Registrar en la auditoría los cambios de flota, clientes y pedidos y los accesos denegados, y avisar ante un robo de sesión | A09 |
| Media | Exigir MFA al administrador y revisar la política de contraseñas de Supabase | A06, A07 |
| Baja | Proteger o desactivar `/docs` en una operación real y alojar las fuentes en el propio proyecto | A02, A08 |
| Baja | Evaluar cifrado a nivel de columna para el DNI y cookies `HttpOnly` en lugar de `localStorage` | A04, A02 |

---

[← Volver al README Principal](../../../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-10-26 | Versión inicial: evaluación de OWASP Top 10 2025 con la matriz de 10 categorías, los hallazgos de SonarQube y de la revisión propia, las correcciones aplicadas y el plan de acciones | Inciso Aguilar Elizabeth Antonela |
| V_1_1_0 | 2026-10-30 | Se incorpora el reanálisis de SonarQube (30-10-2026): 0 vulnerabilidades abiertas, 0 Security Hotspots y seguridad A; 18 vulnerabilidades registradas, todas cerradas (17 corregidas y 1 por excluir un script de apoyo), sin falsos positivos | Inciso Aguilar Elizabeth Antonela |
| V_1_2_0 | 2026-10-30 | Se actualizan las cifras de cobertura del análisis final de SonarQube (código nuevo 94.3 %, total 89.4 %); el resultado de seguridad no cambia | Inciso Aguilar Elizabeth Antonela |
