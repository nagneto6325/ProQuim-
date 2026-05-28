import os
from database.connection import db

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')

def init_db():
    try:
        if not os.path.exists(SCHEMA_PATH):
            print(f"No se encuentra {SCHEMA_PATH}")
            return False

        conn = db.get_connection()
        cur = conn.cursor()

        # Solo ejecutar el schema si la BD está vacía (primera vez)
        # Esto evita duplicar datos de seed cada vez que arranca Flask
        cur.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='inventario'")
        ya_existe = cur.fetchone()[0] > 0

        if not ya_existe:
            with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
                sql = f.read()
            conn.executescript(sql)
            conn.commit()
            print("Base de datos inicializada por primera vez.")
        else:
            print("Base de datos ya existe, sin cambios.")

        conn.close()
        return True
    except Exception as e:
        print(f"Error init_db: {e}")
        return False

if __name__ == '__main__':
    init_db()