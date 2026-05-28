from database.connection import db
# IMPORTANTE: este archivo NO debe importar nada de services/
# para evitar importaciones circulares

class RecetaRepository:
    @staticmethod
    def get_all():
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM recetas")
        recetas = cursor.fetchall()

        resultado = []
        for receta in recetas:
            receta_dict = dict(receta)
            cursor.execute("SELECT * FROM ingredientes WHERE receta_id = ?", (receta['id'],))
            ingredientes = cursor.fetchall()
            receta_dict['ingredientes'] = [dict(i) for i in ingredientes]
            resultado.append(receta_dict)

        conn.close()
        return resultado

    @staticmethod
    def get_by_id(receta_id):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM recetas WHERE id = ?", (receta_id,))
        receta = cursor.fetchone()

        if receta:
            receta_dict = dict(receta)
            cursor.execute("SELECT * FROM ingredientes WHERE receta_id = ?", (receta_id,))
            ingredientes = cursor.fetchall()
            receta_dict['ingredientes'] = [dict(i) for i in ingredientes]
            conn.close()
            return receta_dict

        conn.close()
        return None

    @staticmethod
    def create(nombre, categoria, rendimiento, compatible, ingredientes):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO recetas (nombre, categoria, rendimiento, compatible) VALUES (?, ?, ?, ?)",
            (nombre, categoria, rendimiento, compatible)
        )
        receta_id = cursor.lastrowid

        for ing in ingredientes:
            cursor.execute(
                "INSERT INTO ingredientes (receta_id, nombre, gramos) VALUES (?, ?, ?)",
                (receta_id, ing['nombre'], ing['gramos'])
            )

        conn.commit()
        conn.close()
        return receta_id

    @staticmethod
    def update_compatible(receta_id, compatible):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE recetas SET compatible = ? WHERE id = ?", (compatible, receta_id))
        conn.commit()
        conn.close()