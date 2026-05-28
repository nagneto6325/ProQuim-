import sqlite3
import os
from abc import ABC, abstractmethod

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'proquim.db')

# Los repositorios dependen de esta interfaz, no de la clase concreta.
# Esto permite sustituir la BD por un mock en pruebas sin tocar el resto del sistema.
class IDatabaseConnection(ABC):
    @abstractmethod
    def get_connection(self):
        pass


# --- SINGLETON + DIP: implementacion concreta que cumple el contrato ---
class DatabaseConnection(IDatabaseConnection):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            print("[Singleton] Instancia de DatabaseConnection creada")
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_connection(self):
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn


# instancia global — los repositorios reciben esta abstraccion por inyeccion
db: IDatabaseConnection = DatabaseConnection()