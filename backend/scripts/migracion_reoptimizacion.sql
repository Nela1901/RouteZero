-- HU-012: re-optimización de rutas ante cambios operativos (pedido urgente, cancelación, incidente de tráfico).
--
-- Cambios:
--   1. ruta_pedidos.entregado_en: instante en que el conductor marcó la parada (ENTREGADO o FALLIDO). Desde ahí
--      parte el vehículo al re-optimizar.
--   2. rutas.reemplaza_ruta_id: una re-optimización se guarda como borrador (PLANIFICADA) de la ruta en curso a la
--      que reemplaza; al confirmarla, sus paradas pasan a la ruta original. Si se borra la ruta original, cae el borrador.
--   3. incidentes_trafico: alertas de congestión activas en las vías de la RN-012. Las leen la re-optimización, el
--      mapa (HU-013) y la vista del conductor (HU-014).
--
-- Ejecutar en Supabase > SQL Editor. Es idempotente: se puede correr más de una vez.
-- Ojo (lección del Sprint 2): "Enable automatic RLS" activa RLS en toda tabla nueva; sin política queda inaccesible.

ALTER TABLE ruta_pedidos ADD COLUMN IF NOT EXISTS entregado_en TIMESTAMP WITH TIME ZONE;

ALTER TABLE rutas ADD COLUMN IF NOT EXISTS reemplaza_ruta_id UUID REFERENCES rutas(ruta_id) ON DELETE CASCADE;
CREATE INDEX IF NOT EXISTS idx_rutas_reemplaza ON rutas(reemplaza_ruta_id);

CREATE TABLE IF NOT EXISTS incidentes_trafico (
    incidente_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    calle VARCHAR(30) NOT NULL
        CHECK (calle IN ('Av. Ferrocarril', 'Av. Giráldez', 'Calle Real')),
    factor DECIMAL(4,2) NOT NULL CHECK (factor > 1 AND factor <= 10),
    descripcion VARCHAR(200),
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    registrado_por UUID REFERENCES usuarios(usuario_id) ON DELETE SET NULL,
    creado_en TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resuelto_en TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_incidentes_activos ON incidentes_trafico(activo, creado_en);

ALTER TABLE incidentes_trafico ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS incidentes_acceso_app ON incidentes_trafico;
CREATE POLICY incidentes_acceso_app ON incidentes_trafico FOR ALL USING (true) WITH CHECK (true);
GRANT ALL ON incidentes_trafico TO app_backend, app_admin;
