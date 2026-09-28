-- Crear tabla de categorías de soporte técnico
CREATE TABLE IF NOT EXISTS categorias (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    descripcion TEXT
);

-- Insertar categorías por defecto
INSERT INTO categorias (nombre, descripcion) VALUES
('Soporte Técnico', 'Incidencias generales de hardware, software y servidores'),
('Redes', 'Problemas de conectividad, WiFi, switch e impresoras en red'),
('Accesos', 'Desbloqueo de cuentas, contraseñas y permisos de usuario'),
('Facturación', 'Consultas, reembolsos y cobros de servicios')
ON CONFLICT (nombre) DO NOTHING;

-- Crear tabla para registro y persistencia de tickets
CREATE TABLE IF NOT EXISTS tickets (
    id SERIAL PRIMARY KEY,
    texto_original TEXT NOT NULL,
    categoria_asignada VARCHAR(50) NOT NULL,
    nivel_confianza NUMERIC(5,2),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);