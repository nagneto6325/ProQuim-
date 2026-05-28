-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    rol TEXT NOT NULL,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de recetas
CREATE TABLE IF NOT EXISTS recetas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    categoria TEXT NOT NULL,
    rendimiento INTEGER NOT NULL,
    compatible BOOLEAN DEFAULT 1,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de ingredientes
CREATE TABLE IF NOT EXISTS ingredientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    receta_id INTEGER NOT NULL,
    nombre TEXT NOT NULL,
    gramos INTEGER NOT NULL,
    FOREIGN KEY (receta_id) REFERENCES recetas(id) ON DELETE CASCADE
);

-- Tabla de inventario
CREATE TABLE IF NOT EXISTS inventario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    cantidad REAL NOT NULL,
    stock_minimo REAL NOT NULL,
    unidad TEXT NOT NULL,
    ultima_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de ordenes de produccion
CREATE TABLE IF NOT EXISTS ordenes_produccion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    receta_id INTEGER NOT NULL,
    cantidad_producir REAL NOT NULL,
    estado TEXT DEFAULT 'Pendiente',
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (receta_id) REFERENCES recetas(id)
);

-- Tabla de consumos (guarda cuanto se descuenta del stock)
CREATE TABLE IF NOT EXISTS consumos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    orden_id INTEGER NOT NULL,
    quimico_id INTEGER NOT NULL,
    cantidad_consumida REAL NOT NULL,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (orden_id) REFERENCES ordenes_produccion(id),
    FOREIGN KEY (quimico_id) REFERENCES inventario(id)
);

-- Tabla de trazabilidad (guarda el lote de cada orden completada)
CREATE TABLE IF NOT EXISTS trazabilidad (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    orden_id INTEGER NOT NULL,
    lote_produccion TEXT NOT NULL,
    responsable TEXT NOT NULL,
    fecha_produccion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (orden_id) REFERENCES ordenes_produccion(id)
);

-- Tabla de alertas de stock bajo
CREATE TABLE IF NOT EXISTS alertas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quimico_id INTEGER NOT NULL,
    mensaje TEXT NOT NULL,
    leida BOOLEAN DEFAULT 0,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (quimico_id) REFERENCES inventario(id)
);

-- Tabla para las incompatibilidades quimicas (se usa en el patron strategy)
CREATE TABLE IF NOT EXISTS incompatibilidades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quimico1 TEXT NOT NULL,
    quimico2 TEXT NOT NULL
);

-- DATOS INICIALES

-- Usuarios con contrasenas hasheadas (SHA-256)
-- admin123, jefe123, operario123, gerente123, inv123
INSERT OR IGNORE INTO usuarios (username, password, rol) VALUES
('admin',      '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'Administrador'),
('jefe',       'e577c004a29a6a084d8e9bc25242bfe08eee016313058aea0cb987f91bf7b1f8',  'Jefe de Produccion'),
('operario',   'ea66d0295003394ff7f847590fe43af491ded28bb3837d543d55dfa130c9b2f3', 'Operario'),
('gerente',    'ecfba551324356e5bd27b548adf36b728783f60d9b573d142caac7baad62be49',  'Gerente'),
('inventario', '170b00da0d752f0eef5fa3608ea2e6c0bd751a9bf539dc101ebe9425f5003c53', 'Responsable de Inventario');

-- Quimicos disponibles en el inventario
INSERT OR IGNORE INTO inventario (nombre, cantidad, stock_minimo, unidad) VALUES 
('Acido Sulfonico', 5000, 1000, 'kg'),
('Hidroxido de Sodio', 2000, 500, 'kg'),
('Agua Destilada', 10000, 2000, 'L'),
('Hipoclorito de Sodio', 800, 1000, 'L'),
('Alcohol Etilico', 3000, 800, 'L'),
('Amoniaco', 400, 500, 'L');

-- Recetas precargadas
INSERT OR IGNORE INTO recetas (id, nombre, categoria, rendimiento, compatible) VALUES 
(1, 'Detergente Liquido Neutro', 'Limpieza', 1000, 1),
(2, 'Desinfectante con Cloro', 'Desinfeccion', 1000, 1),
(3, 'Limpiador Multiusos', 'Multiusos', 1000, 0);

-- Ingredientes de cada receta
INSERT OR IGNORE INTO ingredientes (receta_id, nombre, gramos) VALUES 
(1, 'Acido Sulfonico', 150),
(1, 'Hidroxido de Sodio', 50),
(1, 'Agua Destilada', 800),
(2, 'Hipoclorito de Sodio', 200),
(2, 'Agua Destilada', 800),
(3, 'Alcohol Etilico', 300),
(3, 'Amoniaco', 100),
(3, 'Agua Destilada', 600);

-- Ordenes de ejemplo
INSERT OR IGNORE INTO ordenes_produccion (id, receta_id, cantidad_producir, estado, fecha) VALUES 
(1, 1, 500, 'Completada', '2026-04-10'),
(2, 2, 1000, 'Pendiente', '2026-04-12');

-- Trazabilidad de la orden completada
INSERT OR IGNORE INTO trazabilidad (orden_id, lote_produccion, responsable, fecha_produccion) VALUES 
(1, 'LP-2024-001', 'admin', '2026-04-10 14:30:00');

-- Mezclas peligrosas que no se permiten
INSERT OR IGNORE INTO incompatibilidades (quimico1, quimico2) VALUES 
('Alcohol Etilico', 'Hipoclorito de Sodio'),
('Amoniaco', 'Acido Clorhidrico');