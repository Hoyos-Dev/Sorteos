import mysql.connector
from config.database import DB_CONFIG
from services.sorteo_service import SorteoService

def test_compact_functionality():
    """
    Prueba la funcionalidad de compactación de IDs
    """
    try:
        # Mostrar estado actual de la tabla
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        print("Estado actual de detalle_sorteo:")
        cursor.execute("SELECT id, id_sorteo, documento_participante, estado FROM detalle_sorteo ORDER BY id")
        results = cursor.fetchall()
        
        if results:
            for row in results:
                print(f"ID: {row[0]}, Sorteo: {row[1]}, Documento: {row[2]}, Estado: {row[3]}")
        else:
            print("No hay registros en detalle_sorteo")
        
        # Mostrar AUTO_INCREMENT actual
        cursor.execute("SHOW TABLE STATUS LIKE 'detalle_sorteo'")
        status = cursor.fetchone()
        if status:
            print(f"\nAUTO_INCREMENT actual: {status[10]}")
        
        cursor.close()
        connection.close()
        
        # Probar la compactación
        print("\nEjecutando compactación de IDs...")
        SorteoService._compact_detalle_sorteo_ids()
        
        # Mostrar estado después de la compactación
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        print("\nEstado después de la compactación:")
        cursor.execute("SELECT id, id_sorteo, documento_participante, estado FROM detalle_sorteo ORDER BY id")
        results = cursor.fetchall()
        
        if results:
            for row in results:
                print(f"ID: {row[0]}, Sorteo: {row[1]}, Documento: {row[2]}, Estado: {row[3]}")
        else:
            print("No hay registros en detalle_sorteo")
        
        # Mostrar AUTO_INCREMENT después
        cursor.execute("SHOW TABLE STATUS LIKE 'detalle_sorteo'")
        status = cursor.fetchone()
        if status:
            print(f"\nAUTO_INCREMENT después: {status[10]}")
        
        cursor.close()
        connection.close()
        
        print("\n✅ Prueba completada exitosamente")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")

if __name__ == "__main__":
    test_compact_functionality()