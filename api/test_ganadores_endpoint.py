import requests
import json
from datetime import datetime

def test_ganadores_endpoint():
    """Prueba el endpoint de ganadores para verificar fecha_ganador"""
    base_url = "http://localhost:8000"
    
    try:
        # Primero obtener todos los sorteos
        print("=== Obteniendo sorteos disponibles ===")
        response = requests.get(f"{base_url}/sorteos")
        if response.status_code == 200:
            sorteos = response.json()
            print(f"Sorteos encontrados: {len(sorteos)}")
            
            if sorteos:
                sorteo_id = sorteos[0]['id']
                print(f"Usando sorteo ID: {sorteo_id}")
                
                # Obtener ganadores del sorteo
                print(f"\n=== Obteniendo ganadores del sorteo {sorteo_id} ===")
                response = requests.get(f"{base_url}/sorteos/{sorteo_id}/ganadores")
                
                if response.status_code == 200:
                    ganadores = response.json()
                    print(f"Ganadores encontrados: {len(ganadores)}")
                    
                    for ganador in ganadores:
                        print(f"\nGanador:")
                        print(f"  ID: {ganador.get('id')}")
                        print(f"  Documento: {ganador.get('documento_participante')}")
                        print(f"  Nombre: {ganador.get('nombre_participante')}")
                        print(f"  Estado: {ganador.get('estado')}")
                        print(f"  Fecha Asignación: {ganador.get('fecha_asignacion')}")
                        print(f"  Fecha Ganador: {ganador.get('fecha_ganador')}")
                        
                        # Verificar si fecha_ganador es None o está vacía
                        if ganador.get('fecha_ganador') is None:
                            print(f"  ⚠️  PROBLEMA: fecha_ganador es None")
                        elif ganador.get('fecha_ganador') == "":
                            print(f"  ⚠️  PROBLEMA: fecha_ganador está vacía")
                        else:
                            print(f"  ✅ fecha_ganador tiene valor")
                else:
                    print(f"Error obteniendo ganadores: {response.status_code}")
                    print(f"Respuesta: {response.text}")
            else:
                print("No hay sorteos disponibles")
        else:
            print(f"Error obteniendo sorteos: {response.status_code}")
            print(f"Respuesta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Error: No se puede conectar al servidor. ¿Está ejecutándose el backend?")
    except Exception as e:
        print(f"Error inesperado: {e}")

if __name__ == "__main__":
    test_ganadores_endpoint()