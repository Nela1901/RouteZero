-- Permisos para eliminar vehículos y clientes desde la API (CRUD completo).
--
-- `app_backend` solo tenía SELECT, INSERT y UPDATE sobre estas tablas. La API borra únicamente
-- registros sin datos relacionados (el servicio responde 409 si tienen rutas o pedidos).
-- Ejecutar en Supabase > SQL Editor. Es idempotente: se puede correr más de una vez.

GRANT DELETE ON vehiculos, clientes TO app_backend;
