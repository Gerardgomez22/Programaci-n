import psycopg2
from src.conexion_db import DBConnection

class UsuarioDAO:
    @classmethod
    def registrar_usuario(cls, nombre, foto_bytes):
        conn = DBConnection.get_connection()
        if conn is None:
            return False
        cursor = None

        try:
            cursor = conn.cursor()
            query = "INSERT INTO usuarios (nombre, foto) VALUES (%s, %s)"
            foto_blob = psycopg2.Binary(foto_bytes)
            cursor.execute(query, (nombre, foto_blob))
            conn.commit()
            print(f"--> Usuario '{nombre}' registrado con éxito.")
            return True

        except Exception as e:
            print(f"Error en el registro: {e}")
            if conn:
                conn.rollback()
                return False
        finally:
            if cursor:
                cursor.close()

    @classmethod
    def obtener_todos(cls):
        conn = DBConnection.get_connection()
        if conn is None:
            return []
        
        cursor = None
        lista_usuarios = []

        try:
            cursor = conn.cursor()
            query = "SELECT id, nombre, foto FROM usuarios"
            cursor.execute(query)
            
            registros = cursor.fetchall()

            for fila in registros:
                usuario = {
                    "id": fila[0],
                    "nombre": fila[1],
                    "foto_bytes": fila[2] 
                }
                lista_usuarios.append(usuario)
            
            return lista_usuarios

        except Exception as e:
            print(f"Error al obtener usuarios: {e}")
            return []
            
        finally:
            if cursor:
                cursor.close()