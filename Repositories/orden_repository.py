from database.connection import db

class OrdenRepository:
    @staticmethod
    def get_all():
        conn = db.get_connection()  # conexion nueva
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ordenes_produccion ORDER BY id DESC")
        ordenes = cursor.fetchall()
        conn.close()
        return [dict(o) for o in ordenes]
    
    @staticmethod
    def get_by_id(orden_id):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ordenes_produccion WHERE id = ?", (orden_id,))
        orden = cursor.fetchone()
        conn.close()
        return dict(orden) if orden else None
    
    @staticmethod
    def create(receta_id, cantidad_producir):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO ordenes_produccion (receta_id, cantidad_producir) VALUES (?, ?)",
            (receta_id, cantidad_producir)
        )
        orden_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return orden_id
    
    @staticmethod
    def update_estado(orden_id, estado):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE ordenes_produccion SET estado = ? WHERE id = ?",
            (estado, orden_id)
        )
        conn.commit()
        conn.close()
    
    @staticmethod
    def registrar_consumo(orden_id, quimico_id, cantidad_consumida):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO consumos (orden_id, quimico_id, cantidad_consumida) VALUES (?, ?, ?)",
            (orden_id, quimico_id, cantidad_consumida)
        )
        conn.commit()
        conn.close()
    
    @staticmethod
    def registrar_trazabilidad(orden_id, lote_produccion, responsable):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO trazabilidad (orden_id, lote_produccion, responsable) VALUES (?, ?, ?)",
            (orden_id, lote_produccion, responsable)
        )
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_trazabilidad_by_orden(orden_id):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trazabilidad WHERE orden_id = ?", (orden_id,))
        trazabilidad = cursor.fetchone()
        conn.close()
        return dict(trazabilidad) if trazabilidad else None
    
    @staticmethod
    def get_consumos_by_orden(orden_id):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.*, i.nombre as quimico_nombre 
            FROM consumos c 
            JOIN inventario i ON c.quimico_id = i.id 
            WHERE c.orden_id = ?
        """, (orden_id,))
        consumos = cursor.fetchall()
        conn.close()
        return [dict(c) for c in consumos]