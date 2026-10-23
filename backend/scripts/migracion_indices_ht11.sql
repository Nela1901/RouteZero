-- Optimización de consultas (HT-11, Sprint 4): índice para el listado de pedidos sin filtro.
--
-- `GET /api/pedidos` sin filtro de estado ordena por `creado_en DESC, pedido_id` y pagina. Los índices que había
-- (`idx_pedidos_estado_creado`) solo ayudan cuando se filtra por estado, así que sin filtro PostgreSQL ordenaba
-- todos los pedidos en cada petición. Con este índice lee solo las filas de la página.
-- Medido con `scripts/auditar_consultas.py` sobre 16 000 pedidos: ver el documento de implementación del sprint.
-- Ejecutar en Supabase > SQL Editor. Es idempotente: se puede correr más de una vez.

CREATE INDEX IF NOT EXISTS idx_pedidos_creado ON pedidos (creado_en DESC, pedido_id);
