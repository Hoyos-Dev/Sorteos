import mysql.connector
from mysql.connector import Error
import logging
from fastapi import HTTPException

# Configurar logging
logger = logging.getLogger(__name__)

# Configuración de la base de datos
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",  # Cambiar si es necesario
    "password": "",  # Cambiar si es necesario
    "database": "junio5"  # Base de datos del usuario
}


class DatabaseConnection:
    """Clase para manejar conexiones a la base de datos"""
    
    @staticmethod
    def get_connection():
        """Obtiene una conexión a la base de datos MySQL"""
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            return connection
        except Error as err:
            logger.error(f"Error conectando a la base de datos: {err}")
            raise HTTPException(
                status_code=500, 
                detail="Error de conexión a la base de datos"
            )
    
    @staticmethod
    def test_connection():
        """Prueba la conexión a la base de datos"""
        try:
            connection = DatabaseConnection.get_connection()
            connection.close()
            return True
        except Exception as e:
            logger.error(f"Error en test de conexión: {e}")
            return False
    
    @staticmethod
    def execute_query(query: str, params: tuple = None, fetch_one: bool = False, fetch_all: bool = False):
        """Ejecuta una consulta SQL y retorna el resultado"""
        connection = None
        cursor = None
        try:
            connection = DatabaseConnection.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch_one:
                return cursor.fetchone()
            elif fetch_all:
                return cursor.fetchall()
            else:
                connection.commit()
                return cursor.rowcount
                
        except Error as err:
            if connection:
                connection.rollback()
            logger.error(f"Error ejecutando consulta: {err}")
            raise HTTPException(
                status_code=500, 
                detail=f"Error en la base de datos: {str(err)}"
            )
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()