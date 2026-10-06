-- Datos para la demostración del Sprint 2 (Andina Reparto S.A.C., Huancayo).
--
-- Deja la base lista para mostrar el flujo completo: borra rutas, pedidos, clientes, vehículos y
-- conductores existentes (incluidos los de pruebas y de benchmark) y carga datos realistas.
-- NO toca usuarios, sesiones ni la auditoría.
--
-- Ejecutar en Supabase > SQL Editor (rol postgres) ANTES de la demostración. Es repetible:
-- se puede volver a correr para reiniciar el escenario (por ejemplo, tras confirmar rutas).
--
-- Escenario: 6 vehículos disponibles (+1 en mantenimiento), 5 conductores, 20 clientes y
-- 25 pedidos pendientes, más 1 pedido EXPRESS de 2,500 kg que ningún vehículo puede cargar
-- (muestra los pedidos sin cobertura con su motivo y sugerencia).

BEGIN;

-- 1. Limpieza (ruta_pedidos se borra en cascada con rutas)
DELETE FROM rutas;
DELETE FROM pedidos;
DELETE FROM clientes;
DELETE FROM vehiculos;
DELETE FROM conductores;

-- 2. Vehículos
INSERT INTO vehiculos (placa, tipo, capacidad_kg, consumo_km_l, factor_emision_co2, "año_fabricacion", estado, soat_vence, revision_tecnica_vence) VALUES
  ('RZ1-201', 'CAMIONETA', 900.00,  9.50, 2.3100, 2021, 'DISPONIBLE',    CURRENT_DATE + 200, CURRENT_DATE + 150),
  ('RZ1-202', 'CAMIONETA', 900.00,  9.00, 2.3100, 2020, 'DISPONIBLE',    CURRENT_DATE + 120, CURRENT_DATE + 90),
  ('RZ1-203', 'CAMIONETA', 800.00, 10.50, 2.3100, 2022, 'DISPONIBLE',    CURRENT_DATE + 300, CURRENT_DATE + 250),
  ('RZ1-204', 'FURGON',   1500.00,  6.50, 2.6800, 2019, 'DISPONIBLE',    CURRENT_DATE + 20,  CURRENT_DATE + 180),
  ('RZ1-205', 'FURGON',   1500.00,  6.00, 2.6800, 2018, 'DISPONIBLE',    CURRENT_DATE + 90,  CURRENT_DATE + 60),
  ('RZ1-206', 'MOTO',      120.00, 38.00, 2.3100, 2023, 'DISPONIBLE',    CURRENT_DATE + 250, CURRENT_DATE + 250),
  ('RZ1-207', 'CAMIONETA', 900.00,  9.20, 2.3100, 2017, 'MANTENIMIENTO', CURRENT_DATE - 5,   CURRENT_DATE + 40);

-- 3. Conductores (DNI ficticios; consentimiento RN-013 registrado)
INSERT INTO conductores (nombre, dni, categoria_licencia, telefono, correo, licencia_vence, horario_inicio, horario_fin, disponible, consentimiento_datos, consentimiento_en) VALUES
  ('Carlos Mendoza Quispe', '70000001', 'A-IIb',  '964100001', 'carlos.mendoza@andinareparto.example', CURRENT_DATE + 600, '06:00', '14:00', TRUE, TRUE, now()),
  ('Luis Huamán Ccora',     '70000002', 'A-IIb',  '964100002', 'luis.huaman@andinareparto.example',    CURRENT_DATE + 450, '06:00', '14:00', TRUE, TRUE, now()),
  ('Rosa Paucar Ríos',      '70000003', 'A-IIIa', '964100003', 'rosa.paucar@andinareparto.example',    CURRENT_DATE + 25,  '07:00', '15:00', TRUE, TRUE, now()),
  ('Jorge Salazar Lazo',    '70000004', 'A-IIIa', '964100004', NULL,                                   CURRENT_DATE + 800, '07:00', '15:00', TRUE, TRUE, now()),
  ('Miguel Ayala Torres',   '70000005', 'A-I',    '964100005', 'miguel.ayala@andinareparto.example',   CURRENT_DATE + 365, '08:00', '16:00', TRUE, TRUE, now());

-- 4. Clientes: 20 negocios repartidos por la zona urbana de Huancayo y El Tambo (cuadrícula determinista)
INSERT INTO clientes (nombre, tipo_negocio, referencia, latitud, longitud, horario_inicio, horario_fin)
SELECT
  n.nombre,
  n.tipo,
  'Cerca de ' || n.ref,
  ROUND((-12.035 - 0.050 * ((n.i * 37) % 100) / 100.0)::numeric, 8),
  ROUND((-75.235 + 0.040 * ((n.i * 53) % 100) / 100.0)::numeric, 8),
  CASE WHEN n.tipo = 'RESTAURANTE' THEN TIME '07:00' ELSE TIME '06:00' END,
  CASE WHEN n.tipo = 'RESTAURANTE' THEN TIME '17:00' ELSE TIME '20:00' END
FROM (VALUES
  (1,  'Bodega San Jerónimo',          'BODEGA',      'la plaza de armas'),
  (2,  'Restaurante El Tambo',         'RESTAURANTE', 'la avenida Mariscal Castilla'),
  (3,  'Mercado Modelo - Puesto 14',   'MERCADO',     'el Mercado Modelo'),
  (4,  'Comercial Los Andes',          'COMERCIO',    'la avenida Ferrocarril'),
  (5,  'Bodega La Esperanza',          'BODEGA',      'el parque de la Identidad'),
  (6,  'Pollería Huancaína',           'RESTAURANTE', 'la calle Real'),
  (7,  'Minimarket Santa Rosa',        'COMERCIO',    'la avenida Giráldez'),
  (8,  'Bodega Don Pepe',              'BODEGA',      'el hospital Carrión'),
  (9,  'Restaurante Sabor Wanka',      'RESTAURANTE', 'la avenida Huancavelica'),
  (10, 'Mercado Mayorista - Puesto 3', 'MERCADO',     'el Mercado Mayorista'),
  (11, 'Distribuidora Mantaro',        'COMERCIO',    'la avenida Evitamiento'),
  (12, 'Bodega Nuevo Amanecer',        'BODEGA',      'la avenida Leoncio Prado'),
  (13, 'Cevichería Pacífico',          'RESTAURANTE', 'la avenida Circunvalación'),
  (14, 'Abarrotes El Progreso',        'COMERCIO',    'la calle Ancash'),
  (15, 'Bodega Villa Hermosa',         'BODEGA',      'la avenida Next'),
  (16, 'Restaurante Casa Andina',      'RESTAURANTE', 'la plaza Constitución'),
  (17, 'Mercado Zonal - Puesto 22',    'MERCADO',     'el Mercado Zonal'),
  (18, 'Ferretería Central',           'COMERCIO',    'la calle Piura'),
  (19, 'Bodega Los Olivos',            'BODEGA',      'la avenida Universitaria'),
  (20, 'Panadería San Carlos',         'OTRO',        'la avenida Progreso')
) AS n(i, nombre, tipo, ref);

-- 5. Pedidos pendientes: 25 con pesos de 15 a 104 kg; cada quinto es EXPRESS (ventana de la mañana)
INSERT INTO pedidos (cliente_id, descripcion, peso_kg, volumen_m3, prioridad, latitud, longitud, ventana_inicio, ventana_fin)
SELECT
  c.cliente_id,
  'Pedido de demostración ' || g.i,
  15 + ((g.i * 17) % 90),
  ROUND((0.05 + ((g.i * 7) % 20) / 100.0)::numeric, 3),
  CASE WHEN g.i % 5 = 0 THEN 'EXPRESS' WHEN g.i % 3 = 0 THEN 'ECONOMICO' ELSE 'ESTANDAR' END,
  c.latitud,
  c.longitud,
  CASE WHEN g.i % 5 = 0 THEN TIME '08:00' ELSE TIME '07:00' END,
  CASE WHEN g.i % 5 = 0 THEN TIME '11:00' WHEN g.i % 3 = 0 THEN TIME '16:00' ELSE TIME '13:00' END
FROM generate_series(1, 25) AS g(i)
JOIN (SELECT cliente_id, latitud, longitud, ROW_NUMBER() OVER (ORDER BY nombre) AS orden FROM clientes) c
  ON c.orden = ((g.i - 1) % 20) + 1;

-- 6. Pedido que ningún vehículo puede cargar: demuestra los pedidos sin cobertura
INSERT INTO pedidos (cliente_id, descripcion, peso_kg, volumen_m3, prioridad, latitud, longitud, ventana_inicio, ventana_fin)
SELECT cliente_id, 'Carga industrial de 2,500 kg (excede toda la flota)', 2500.00, 6.000, 'EXPRESS', latitud, longitud, TIME '08:00', TIME '12:00'
FROM clientes WHERE nombre = 'Distribuidora Mantaro';

COMMIT;

-- Verificación rápida (debe dar 6 disponibles + 1 en mantenimiento, 5 conductores, 20 clientes y 26 pedidos pendientes)
SELECT
  (SELECT COUNT(*) FROM vehiculos WHERE estado = 'DISPONIBLE')    AS vehiculos_disponibles,
  (SELECT COUNT(*) FROM vehiculos WHERE estado = 'MANTENIMIENTO') AS vehiculos_en_mantenimiento,
  (SELECT COUNT(*) FROM conductores)                              AS conductores,
  (SELECT COUNT(*) FROM clientes)                                 AS clientes,
  (SELECT COUNT(*) FROM pedidos WHERE estado = 'PENDIENTE')       AS pedidos_pendientes;
