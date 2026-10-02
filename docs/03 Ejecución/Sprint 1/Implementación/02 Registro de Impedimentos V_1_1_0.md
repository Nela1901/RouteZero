# 02 Registro de Impedimentos

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Líder del Proyecto** | Inciso Aguilar Elizabeth Antonela |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Sprint** | Sprint 1 — Base del sistema (19-09-2026 – 02-10-2026) |
| **Versión** | 1.1.0 |

[← Volver al README Principal](../../../../README.md)

---

| Impedimento # | Fecha de Registro | Descripción del Impedimento así como el Impacto en el Proyecto | Prioridad | Reportado por | Fecha tope de Resolución | Estado | Fecha de Resolución | Resolución/Comentarios |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| IMP-001 | 2026-09-26 | **Enable automatic RLS** de Supabase activa RLS en toda tabla nueva del esquema `public`, incluidas tablas de referencia sin dato por usuario (`roles`, y por diseño también `vehiculos`/`clientes`/`pedidos`). Una tabla nueva sin política queda inaccesible en silencio (0 filas, sin error) para el rol `app_backend`, lo que bloqueaba el avance de los módulos de flota y pedidos sin ningún mensaje de error visible | Alta | Inciso Aguilar Elizabeth Antonela | 2026-09-27 | Resuelto | 2026-09-26 | Se agregó una política permisiva `FOR ALL USING (true) WITH CHECK (true)` a cada tabla organizacional (no por usuario), dejando el control de acceso real a `requiere_rol` en la API y no a RLS |
| IMP-002 | 2026-09-27 | `sesiones_activas.usuario_id` no tenía `ON DELETE CASCADE` hacia `usuarios`: borrar un usuario de prueba desde el panel de Supabase fallaba con "Database error deleting user" si le quedaba alguna sesión activa, bloqueando las pruebas manuales de extremo a extremo | Media | Guerra Lozano Keen | 2026-09-27 | Resuelto | 2026-09-27 | Se corrigió la restricción de clave foránea para incluir `ON DELETE CASCADE` |
| IMP-003 | 2026-09-28 | PyJWT no tolera ningún desfase de reloj por defecto; un desfase de pocos segundos entre la máquina de desarrollo y los servidores de Supabase causaba un `ImmatureSignatureError` intermitente al verificar el JWT, interrumpiendo sesiones de prueba sin un motivo aparente | Media | Guerra Lozano Keen | 2026-09-28 | Resuelto | 2026-09-28 | Se agregó `leeway=10` a `jwt.decode` en `src/core/security.py` |
| IMP-004 | 2026-10-01 | `requirements.txt` fijaba `sqlalchemy>=2.0` sin tope superior; al desplegar en Render se instaló una versión de SQLAlchemy más nueva que la usada en desarrollo local, que resuelve el driver de PostgreSQL por defecto hacia `psycopg` (v3, no instalado) en vez de `psycopg2`. El backend fallaba con `ModuleNotFoundError` al arrancar en producción, bloqueando HT-03 (despliegue) un día antes de la inspección | Alta | Inciso Aguilar Elizabeth Antonela | 2026-10-01 | Resuelto | 2026-10-01 | Se forzó el driver `psycopg2` explícitamente al crear el engine (`src/core/database.py`, `src/auth/mantenimiento.py`), sin tocar `settings.database_url` para no romper los scripts que ya conectan con `psycopg2` directo. Queda como mejora pendiente fijar también un tope superior de versión en `requirements.txt` |
| IMP-005 | 2026-09-20 | Disponibilidad limitada de los integrantes del equipo por carga académica de otras asignaturas (riesgo RSK-005 del [`03 Registro de riesgos`](../../../02%20Planificaci%C3%B3n/03%20Registro%20de%20riesgos%20V_1_0_0.md), materializado durante todo el sprint): la implementación de backend y frontend del Sprint 1 se concentró casi por completo en un solo integrante, sin que el resto del equipo tomara módulos propios | Alta | Inciso Aguilar Elizabeth Antonela | 2026-10-02 | Abierto | — | Mitigado parcialmente documentando el trabajo técnico en detalle (`design.md`, docs de ejecución) para facilitar que el resto del equipo se incorpore en el Sprint 2; pendiente de resolución real: redistribuir módulos concretos del Sprint 2 entre todos los integrantes desde el Sprint Planning |
| IMP-006 | 2026-09-28 | El Custom Access Token Hook de Supabase parece cachear el `token_version` del usuario: tras revocar todas sus sesiones, un login nuevo puede seguir recibiendo un valor de `token_version` viejo y fallar con "Token revocado". Se materializó en la práctica el 01-10-2026, la noche antes de la inspección, bloqueando el login de la cuenta de Administrador en producción | Alta | Inciso Aguilar Elizabeth Antonela | 2026-10-02 | Resuelto | 2026-10-01 | Se corrigió en el código propio en vez de depender del hook de Supabase: se dejó de incrementar `token_version` al revocar sesiones (detección de robo de sesión en `renovar` y "cerrar todas" en `revocar_todas`), apoyándose únicamente en `sesiones_activas.estado`, que `get_current_user` ya exige en cada request y no depende del hook. Se eliminó `incrementar_token_version` de `repository.py` por quedar sin uso. Costo residual aceptado: un access token ya emitido sigue vigente hasta sus 15 minutos naturales tras una revocación |

---

[← Volver al README Principal](../../../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-10-01 | Versión inicial: registro de los 6 impedimentos técnicos y de recursos humanos identificados durante el Sprint 1 | Inciso Aguilar Elizabeth Antonela |
| V_1_1_0 | 2026-10-01 | IMP-006 pasa a Resuelto: se materializó en producción la noche antes de la inspección y se corrigió dejando de incrementar `token_version` al revocar sesiones | Inciso Aguilar Elizabeth Antonela |
