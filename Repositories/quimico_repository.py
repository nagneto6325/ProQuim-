from database.connection import db

class QuimicoRepository:
    @staticmethod
    def get_all():
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventario")
        items = cursor.fetchall()
        conn.close()
        return [dict(i) for i in items]

    @staticmethod
    def get_by_id(quimico_id):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventario WHERE id = ?", (quimico_id,))
        item = cursor.fetchone()
        conn.close()
        return dict(item) if item else None

    @staticmethod
    def get_by_nombre(nombre):
        conn = db.get_connection()
        cursor = conn.cursor()
        # COLLATE NOCASE para tolerar diferencias de mayúsculas
        # LIMIT 1 como seguridad ante posibles duplicados residuales
        cursor.execute(
            "SELECT * FROM inventario WHERE nombre = ? COLLATE NOCASE LIMIT 1",
            (nombre,)
        )
        item = cursor.fetchone()
        conn.close()
        return dict(item) if item else None

    @staticmethod
    def update_cantidad(quimico_id, nueva_cantidad):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE inventario SET cantidad = ?, ultima_actualizacion = CURRENT_TIMESTAMP WHERE id = ?",
            (nueva_cantidad, quimico_id)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_incompatibilidades():
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT quimico1, quimico2 FROM incompatibilidades")
        incompatibilidades = cursor.fetchall()
        conn.close()
        return [(i['quimico1'], i['quimico2']) for i in incompatibilidades]

    @staticmethod
    def crear_alerta(quimico_id, mensaje):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO alertas (quimico_id, mensaje) VALUES (?, ?)",
            (quimico_id, mensaje)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_alertas_no_leidas():
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM alertas WHERE leida = 0")
        alertas = cursor.fetchall()
        conn.close()
        return [dict(a) for a in alertas]