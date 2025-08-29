from config.database import DatabaseConnection

def check_sorteos():
    connection = DatabaseConnection.get_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Primero ver qué tablas existen
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print("=== TABLAS EN LA BASE DE DATOS ===")
    for table in tables:
        print(table)
    print("\n")
    
    # Intentar con diferentes nombres de tabla
    table_names = ['sorteos', 'sorteo', 'Sorteo', 'detalle_sorteo']
    
    for table_name in table_names:
        try:
            cursor.execute(f"SELECT id, nombre, cantidad_premio FROM {table_name}")
            sorteos = cursor.fetchall()
            
            print(f"=== DATOS DE TABLA {table_name} ===")
            for sorteo in sorteos:
                print(f"ID: {sorteo['id']}")
                print(f"Nombre: {sorteo['nombre']}")
                print(f"cantidad_premio: {sorteo['cantidad_premio']}")
                print("---")
            break
        except Exception as e:
            print(f"Tabla {table_name} no encontrada o error: {e}")
            continue
    
    cursor.close()
    connection.close()

if __name__ == "__main__":
    check_sorteos()