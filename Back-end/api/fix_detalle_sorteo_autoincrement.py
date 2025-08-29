import mysql.connector
from config.database import DB_CONFIG

def reset_detalle_sorteo_autoincrement():
    """
    Resetea el AUTO_INCREMENT de la tabla detalle_sorteo para que comience desde 1
    después de eliminar registros.
    """
    connection = None
    cursor = None
    
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Obtener el máximo ID actual en la tabla
        cursor.execute("SELECT MAX(id) FROM detalle_sorteo")
        max_id = cursor.fetchone()[0]
        
        # Si no hay registros, establecer AUTO_INCREMENT en 1
        if max_id is None:
            next_id = 1
        else:
            next_id = max_id + 1
        
        # Resetear el AUTO_INCREMENT
        query = f"ALTER TABLE detalle_sorteo AUTO_INCREMENT = {next_id}"
        cursor.execute(query)
        connection.commit()
        
        print(f"AUTO_INCREMENT de detalle_sorteo reseteado a {next_id}")
        return True
        
    except mysql.connector.Error as e:
        print(f"Error reseteando AUTO_INCREMENT: {e}")
        if connection:
            connection.rollback()
        return False
        
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def compact_detalle_sorteo_ids():
    """
    Compacta los IDs de detalle_sorteo para que sean consecutivos desde 1,
    eliminando gaps causados por eliminaciones.
    """
    connection = None
    cursor = None
    
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Crear tabla temporal con IDs consecutivos
        cursor.execute("""
            CREATE TEMPORARY TABLE temp_detalle_sorteo AS
            SELECT 
                ROW_NUMBER() OVER (ORDER BY id) as new_id,
                id as old_id,
                id_sorteo,
                documento_participante,
                estado,
                fecha_asignacion
            FROM detalle_sorteo
            ORDER BY id
        """)
        
        # Deshabilitar verificación de claves foráneas temporalmente
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        # Vaciar la tabla original
        cursor.execute("DELETE FROM detalle_sorteo")
        
        # Resetear AUTO_INCREMENT a 1
        cursor.execute("ALTER TABLE detalle_sorteo AUTO_INCREMENT = 1")
        
        # Insertar datos con nuevos IDs consecutivos
        cursor.execute("""
            INSERT INTO detalle_sorteo (id, id_sorteo, documento_participante, estado, fecha_asignacion)
            SELECT new_id, id_sorteo, documento_participante, estado, fecha_asignacion
            FROM temp_detalle_sorteo
            ORDER BY new_id
        """)
        
        # Obtener el nuevo máximo ID
        cursor.execute("SELECT MAX(id) FROM detalle_sorteo")
        max_id = cursor.fetchone()[0]
        
        if max_id is not None:
            # Establecer AUTO_INCREMENT al siguiente valor
            cursor.execute(f"ALTER TABLE detalle_sorteo AUTO_INCREMENT = {max_id + 1}")
        
        # Rehabilitar verificación de claves foráneas
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        # Eliminar tabla temporal
        cursor.execute("DROP TEMPORARY TABLE temp_detalle_sorteo")
        
        connection.commit()
        
        print(f"IDs de detalle_sorteo compactados. Nuevo AUTO_INCREMENT: {max_id + 1 if max_id else 1}")
        return True
        
    except mysql.connector.Error as e:
        print(f"Error compactando IDs: {e}")
        if connection:
            connection.rollback()
        return False
        
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

if __name__ == "__main__":
    print("Opciones:")
    print("1. Resetear AUTO_INCREMENT (mantiene IDs existentes)")
    print("2. Compactar IDs (reorganiza para ser consecutivos desde 1)")
    
    opcion = input("Seleccione una opción (1 o 2): ")
    
    if opcion == "1":
        reset_detalle_sorteo_autoincrement()
    elif opcion == "2":
        compact_detalle_sorteo_ids()
    else:
        print("Opción no válida")