from database.connection import db

class UsuarioRepository:
    @staticmethod
    def find_by_username(username):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None
    
    @staticmethod
    def create(username, password, rol):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usuarios (username, password, rol) VALUES (?, ?, ?)",
            (username, password, rol)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    
    @staticmethod
    def get_all():
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, rol FROM usuarios")
        users = cursor.fetchall()
        conn.close()
        return [dict(u) for u in users]