import psycopg2
from src.config import Config

class DBConnection:
    _connection = None  

    @classmethod
    def get_connection(cls):
        try:
            if cls._connection is None or cls._connection.closed != 0:
                print("--> Conectando a PostgreSQL...")
                cls._connection = psycopg2.connect(
                    host=Config.DB_HOST,
                    database=Config.DB_NAME,
                    user=Config.DB_USER,
                    password=Config.DB_PASS,
                    port=Config.DB_PORT
                )
                cls._connection.autocommit = False
            
            return cls._connection
            
        except Exception as e:
            print(f"Error grave de conexión: {e}")
            return None