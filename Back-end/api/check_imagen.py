import mysql.connector
import os

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'junio5'
}

try:
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute('SELECT id, imagen FROM sorteo WHERE id = 2')
    result = cursor.fetchone()
    
    print(f'Sorteo 2 imagen: {result}')
    
    if result and result['imagen']:
        print(f'Ruta de imagen: {result["imagen"]}')
        print(f'Archivo existe: {os.path.exists(result["imagen"])}')
    else:
        print('No hay imagen configurada para el sorteo 2')
        
except Exception as e:
    print(f'Error: {e}')
finally:
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()