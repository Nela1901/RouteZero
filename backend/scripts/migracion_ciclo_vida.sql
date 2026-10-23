-- Costo del ciclo de vida de la flota para el reporte de sostenibilidad (HU-016, Sprint 4).
--
-- Agrega al vehículo el precio de compra y la vida útil estimada. El reporte prorratea el precio entre los
-- años de vida útil para estimar cuánto cuesta cada vehículo en el periodo, y le suma el combustible gastado.
-- Las dos columnas son opcionales: los vehículos ya registrados quedan sin dato y el reporte los marca así.
-- No hacen falta permisos nuevos: `app_backend` ya puede leer y actualizar `vehiculos`.
-- Ejecutar en Supabase > SQL Editor ANTES de desplegar el código que las usa. Es idempotente: se puede
-- correr más de una vez.

ALTER TABLE vehiculos
    ADD COLUMN IF NOT EXISTS precio_compra_soles NUMERIC(12, 2) CHECK (precio_compra_soles > 0),
    ADD COLUMN IF NOT EXISTS vida_util_anios SMALLINT CHECK (vida_util_anios BETWEEN 1 AND 40);
