#!/usr/bin/env python3
"""
Script para agregar la columna ganadores_simultaneos a la tabla sorteo
"""

import mysql.connector
from config.database import DB_CONFIG

def add_ganadores_simultaneos_column():
    """Agrega la columna ganadores_simultaneos a la tabla sorteo"""
    connection = None
    cursor = None
    
    try:
        # Conectar a la base de datos
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Verificar si la columna ya existe
        check_column_query = """
        SELECT COUNT(*) 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = %s 
        AND TABLE_NAME = 'sorteo' 
        AND COLUMN_NAME = 'ganadores_simultaneos'
        """
        
        cursor.execute(check_column_query, (DB_CONFIG['database'],))
        column_exists = cursor.fetchone()[0] > 0
        
        if column_exists:
            print("La columna 'ganadores_simultaneos' ya existe en la tabla 'sorteo'")
            return
        
        # Agregar la columna ganadores_simultaneos
        alter_query = """
        ALTER TABLE sorteo 
        ADD COLUMN ganadores_simultaneos INT DEFAULT 1 NOT NULL
        """
        
        cursor.execute(alter_query)
        connection.commit()
        
        print("✅ Columna 'ganadores_simultaneos' agregada exitosamente a la tabla 'sorteo'")
        
        # Actualizar registros existentes para que tengan valor por defecto
        update_query = """
        UPDATE sorteo 
        SET ganadores_simultaneos = 1 
        WHERE ganadores_simultaneos IS NULL
        """
        
        cursor.execute(update_query)
        connection.commit()
        
        print("✅ Registros existentes actualizados con valor por defecto")
        
    except mysql.connector.Error as err:
        print(f"❌ Error: {err}")
        if connection:
            connection.rollback()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

if __name__ == "__main__":
    print("Agregando columna ganadores_simultaneos a la tabla sorteo...")
    add_ganadores_simultaneos_column()
    print("Proceso completado.")