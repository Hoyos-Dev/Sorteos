import mysql.connector
from datetime import datetime
from config.database import DB_CONFIG

def check_fecha_ganador_issue():
    """Verifica el problema con fecha_ganador"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        print("=== Verificando problema con fecha_ganador ===")
        
        # Buscar ganadores con fecha_ganador NULL
        print("\n1. Ganadores con fecha_ganador NULL:")
        cursor.execute("""
            SELECT ds.id, ds.id_sorteo, ds.documento_participante, ds.estado, 
                   ds.fecha_asignacion, ds.fecha_ganador, p.nombre
            FROM detalle_sorteo ds
            JOIN participantes p ON ds.documento_participante = p.documento
            WHERE ds.estado = 'ganador' AND ds.fecha_ganador IS NULL
            ORDER BY ds.id DESC
        """)
        
        ganadores_sin_fecha = cursor.fetchall()
        print(f"Encontrados: {len(ganadores_sin_fecha)} ganadores sin fecha_ganador")
        
        for ganador in ganadores_sin_fecha:
            print(f"  ID: {ganador['id']}, Sorteo: {ganador['id_sorteo']}, "
                  f"Documento: {ganador['documento_participante']}, "
                  f"Nombre: {ganador['nombre']}, "
                  f"Fecha Ganador: {ganador['fecha_ganador']}")
        
        # Buscar todos los ganadores
        print("\n2. Todos los ganadores:")
        cursor.execute("""
            SELECT ds.id, ds.id_sorteo, ds.documento_participante, ds.estado, 
                   ds.fecha_asignacion, ds.fecha_ganador, p.nombre
            FROM detalle_sorteo ds
            JOIN participantes p ON ds.documento_participante = p.documento
            WHERE ds.estado = 'ganador'
            ORDER BY ds.id DESC
            LIMIT 10
        """)
        
        todos_ganadores = cursor.fetchall()
        print(f"Encontrados: {len(todos_ganadores)} ganadores en total")
        
        for ganador in todos_ganadores:
            print(f"  ID: {ganador['id']}, Sorteo: {ganador['id_sorteo']}, "
                  f"Documento: {ganador['documento_participante']}, "
                  f"Nombre: {ganador['nombre']}, "
                  f"Fecha Ganador: {ganador['fecha_ganador']}")
        
        # Si hay ganadores sin fecha, intentar corregirlos
        if ganadores_sin_fecha:
            print("\n3. Corrigiendo ganadores sin fecha_ganador...")
            fecha_actual = datetime.now()
            
            for ganador in ganadores_sin_fecha:
                print(f"Actualizando ganador ID {ganador['id']}...")
                
                update_query = """
                    UPDATE detalle_sorteo 
                    SET fecha_ganador = %s
                    WHERE id = %s AND estado = 'ganador' AND fecha_ganador IS NULL
                """
                
                cursor.execute(update_query, (fecha_actual, ganador['id']))
                
            connection.commit()
            print(f"Actualizados {cursor.rowcount} registros")
            
            # Verificar la corrección
            print("\n4. Verificando corrección...")
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM detalle_sorteo 
                WHERE estado = 'ganador' AND fecha_ganador IS NULL
            """)
            
            result = cursor.fetchone()
            print(f"Ganadores sin fecha_ganador después de la corrección: {result['count']}")
        
        # Verificar sorteos activos
        print("\n5. Sorteos disponibles:")
        cursor.execute("""
            SELECT s.id, s.nombre, s.estado, 
                   COUNT(ds.id) as total_participantes,
                   SUM(CASE WHEN ds.estado = 'ganador' THEN 1 ELSE 0 END) as ganadores
            FROM sorteo s
            LEFT JOIN detalle_sorteo ds ON s.id = ds.id_sorteo
            GROUP BY s.id, s.nombre, s.estado
            ORDER BY s.id DESC
        """)
        
        sorteos = cursor.fetchall()
        for sorteo in sorteos:
            print(f"  ID: {sorteo['id']}, Nombre: {sorteo['nombre']}, "
                  f"Estado: {sorteo['estado']}, "
                  f"Participantes: {sorteo['total_participantes']}, "
                  f"Ganadores: {sorteo['ganadores']}")
        
    except mysql.connector.Error as e:
        print(f"Error de base de datos: {e}")
    except Exception as e:
        print(f"Error general: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    check_fecha_ganador_issue()