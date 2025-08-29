import mysql.connector
from datetime import datetime
from config.database import DB_CONFIG

def test_fecha_ganador_update():
    """Prueba la actualización del campo fecha_ganador"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        # Primero, verificar la estructura de la tabla
        print("=== Estructura de la tabla detalle_sorteo ===")
        cursor.execute("DESCRIBE detalle_sorteo")
        columns = cursor.fetchall()
        for col in columns:
            print(f"{col['Field']}: {col['Type']} - {col['Null']} - {col['Default']}")
        
        print("\n=== Registros actuales en detalle_sorteo ===")
        cursor.execute("""
            SELECT id, id_sorteo, documento_participante, estado, 
                   fecha_asignacion, fecha_ganador
            FROM detalle_sorteo 
            ORDER BY id DESC 
            LIMIT 10
        """)
        
        registros = cursor.fetchall()
        for registro in registros:
            print(f"ID: {registro['id']}, Sorteo: {registro['id_sorteo']}, "
                  f"Documento: {registro['documento_participante']}, "
                  f"Estado: {registro['estado']}, "
                  f"Fecha Asignación: {registro['fecha_asignacion']}, "
                  f"Fecha Ganador: {registro['fecha_ganador']}")
        
        # Buscar un participante específico para probar la actualización
        if registros:
            primer_registro = registros[0]
            print(f"\n=== Probando actualización de fecha_ganador ===")
            print(f"Actualizando registro ID: {primer_registro['id']}")
            
            fecha_actual = datetime.now()
            print(f"Fecha actual: {fecha_actual}")
            
            # Actualizar el registro
            update_query = """
                UPDATE detalle_sorteo 
                SET estado = %s, fecha_ganador = %s
                WHERE id = %s
            """
            
            cursor.execute(update_query, ('ganador', fecha_actual, primer_registro['id']))
            connection.commit()
            
            print(f"Filas afectadas: {cursor.rowcount}")
            
            # Verificar la actualización
            cursor.execute("""
                SELECT id, estado, fecha_ganador
                FROM detalle_sorteo 
                WHERE id = %s
            """, (primer_registro['id'],))
            
            resultado = cursor.fetchone()
            print(f"\nDespués de la actualización:")
            print(f"ID: {resultado['id']}, Estado: {resultado['estado']}, "
                  f"Fecha Ganador: {resultado['fecha_ganador']}")
        
    except mysql.connector.Error as e:
        print(f"Error de base de datos: {e}")
    except Exception as e:
        print(f"Error general: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    test_fecha_ganador_update()