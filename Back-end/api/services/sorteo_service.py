import mysql.connector
from datetime import datetime
from typing import List, Optional, Tuple
from config.database import DB_CONFIG
from models.sorteo import Sorteo, SorteoResponse, DetalleSorteo, DetalleSorteoResponse, EstadoSorteo, EstadoParticipacion
from models.participante import Participante, RegistroSorteoConParticipantesResponse
import os
import base64
from fastapi import UploadFile
# Importación removida para evitar dependencia circular

class SorteoService:
    
    @staticmethod
    def crear_sorteo(nombre: str, descripcion: str = None) -> int:
        """Crea un nuevo sorteo y retorna su ID"""
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()
            
            if descripcion is None:
                descripcion = f"Sorteo {nombre}"
            
            # Encontrar el menor ID disponible
            cursor.execute("""
                SELECT COALESCE(MIN(t1.id + 1), 1) as next_id
                FROM sorteo t1
                LEFT JOIN sorteo t2 ON t1.id + 1 = t2.id
                WHERE t2.id IS NULL
            """)
            
            result = cursor.fetchone()
            sorteo_id = result[0] if result else 1
            
            # Insertar con el ID específico
            query = """
                INSERT INTO sorteo (id, nombre, descripcion, estado, fecha_creacion)
                VALUES (%s, %s, %s, %s, %s)
            """
            
            fecha_actual = datetime.now()
            cursor.execute(query, (sorteo_id, nombre, descripcion, EstadoSorteo.ACTIVO.value, fecha_actual))
            
            connection.commit()
            
            return sorteo_id
            
        except mysql.connector.Error as e:
            print(f"Error creando sorteo: {e}")
            return 0
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    # Método eliminar_sorteo removido - solo se permite finalizar sorteos
    
    @staticmethod
    def _compact_detalle_sorteo_ids():
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
            
        except mysql.connector.Error as e:
            print(f"Error compactando IDs de detalle_sorteo: {e}")
            if connection:
                connection.rollback()
                
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
    
    @staticmethod
    def _participante_existe(documento: str) -> bool:
        """Verifica si un participante existe en la base de datos"""
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()
            
            query = "SELECT documento FROM participantes WHERE documento = %s"
            cursor.execute(query, (documento,))
            
            result = cursor.fetchone()
            return result is not None
            
        except mysql.connector.Error as e:
            print(f"Error verificando participante: {e}")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    @staticmethod
    def _crear_participante(documento: str, nombre: str) -> bool:
        """Crea un nuevo participante en la base de datos"""
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()
            
            query = """
                INSERT INTO participantes (documento, nombre, fecha_registro)
                VALUES (%s, %s, %s)
            """
            
            fecha_actual = datetime.now()
            cursor.execute(query, (documento, nombre, fecha_actual))
            
            connection.commit()
            return True
            
        except mysql.connector.Error as e:
            print(f"Error creando participante: {e}")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    @staticmethod
    def obtener_sorteo(sorteo_id: int) -> Optional[SorteoResponse]:
        """Obtiene un sorteo por su ID"""
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor(dictionary=True)
            
            query = "SELECT * FROM sorteo WHERE id = %s"
            cursor.execute(query, (sorteo_id,))
            
            result = cursor.fetchone()
            
            if result:
                return SorteoResponse(**result)
            return None
            
        except mysql.connector.Error as e:
            print(f"Error obteniendo sorteo: {e}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    @staticmethod
    def asignar_participante_a_sorteo(sorteo_id: int, documento_participante: str) -> bool:
        """Asigna un participante a un sorteo"""
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()
            
            # Verificar si ya existe la asignación
            query_check = """
                SELECT id FROM detalle_sorteo 
                WHERE id_sorteo = %s AND documento_participante = %s
            """
            cursor.execute(query_check, (sorteo_id, documento_participante))
            existing = cursor.fetchone()
            
            if existing:
                return False  # Ya existe la asignación
            
            # Crear nueva asignación
            query_insert = """
                INSERT INTO detalle_sorteo (id_sorteo, documento_participante, estado, fecha_asignacion)
                VALUES (%s, %s, %s, %s)
            """
            
            fecha_actual = datetime.now()
            cursor.execute(query_insert, (
                sorteo_id, 
                documento_participante, 
                EstadoParticipacion.PARTICIPANDO.value, 
                fecha_actual
            ))
            
            connection.commit()
            return True
            
        except mysql.connector.Error as e:
            print(f"Error asignando participante a sorteo: {e}")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    @staticmethod
    def crear_sorteo_con_participantes(nombre_sorteo: str, participantes: List[Participante], descripcion_sorteo: str = None) -> RegistroSorteoConParticipantesResponse:
        """Crea un sorteo y asigna participantes. Retorna RegistroSorteoConParticipantesResponse"""
        errores = []
        participantes_registrados = 0
        participantes_existentes = 0
        sorteo_id = 0
        
        try:
            # Crear el sorteo
            sorteo_id = SorteoService.crear_sorteo(nombre_sorteo, descripcion_sorteo)
            
            if sorteo_id == 0:
                errores.append("Error al crear el sorteo")
                return RegistroSorteoConParticipantesResponse(
                    sorteo_id=0,
                    nombre_sorteo=nombre_sorteo,
                    participantes_registrados=0,
                    participantes_existentes=0,
                    errores=errores,
                    mensaje="Error al crear el sorteo"
                )
            
            # Registrar participantes y asignarlos al sorteo
            for participante in participantes:
                try:
                    # Verificar si el participante ya existe
                    if SorteoService._participante_existe(participante.documento):
                        participantes_existentes += 1
                    else:
                        # Crear el participante
                        if SorteoService._crear_participante(participante.documento, participante.nombre):
                            participantes_registrados += 1
                        else:
                            errores.append(f"Error creando participante {participante.documento}")
                            continue
                    
                    # Asignar participante al sorteo
                    asignacion_exitosa = SorteoService.asignar_participante_a_sorteo(sorteo_id, participante.documento)
                    if not asignacion_exitosa:
                        errores.append(f"Participante {participante.documento} ya está asignado al sorteo")
                        
                except Exception as e:
                    errores.append(f"Error procesando participante {participante.documento}: {str(e)}")
            
            mensaje = f"Sorteo '{nombre_sorteo}' creado exitosamente. Participantes registrados: {participantes_registrados}, Ya existían: {participantes_existentes}"
            return RegistroSorteoConParticipantesResponse(
                sorteo_id=sorteo_id,
                nombre_sorteo=nombre_sorteo,
                participantes_registrados=participantes_registrados,
                participantes_existentes=participantes_existentes,
                errores=errores,
                mensaje=mensaje
            )
            
        except Exception as e:
            errores.append(f"Error creando sorteo: {str(e)}")
            return RegistroSorteoConParticipantesResponse(
                sorteo_id=0,
                nombre_sorteo=nombre_sorteo,
                participantes_registrados=0,
                participantes_existentes=0,
                errores=errores,
                mensaje="Error al crear sorteo con participantes"
            )
    
    @staticmethod
    def obtener_participantes_sorteo(sorteo_id: int) -> List[DetalleSorteoResponse]:
        """Obtiene todos los participantes de un sorteo"""
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT ds.*, p.nombre as nombre_participante
                FROM detalle_sorteo ds
                JOIN participantes p ON ds.documento_participante = p.documento
                WHERE ds.id_sorteo = %s
                ORDER BY ds.fecha_asignacion
            """
            
            cursor.execute(query, (sorteo_id,))
            results = cursor.fetchall()
            
            return [DetalleSorteoResponse(**result) for result in results]
            
        except mysql.connector.Error as e:
            print(f"Error obteniendo participantes del sorteo: {e}")
            return []
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    @staticmethod
    def eliminar_participante_sorteo(sorteo_id: int, documento_participante: str) -> bool:
        """Elimina un participante de un sorteo"""
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()
            
            query = """
                DELETE FROM detalle_sorteo 
                WHERE id_sorteo = %s AND documento_participante = %s
            """
            
            cursor.execute(query, (sorteo_id, documento_participante))
            connection.commit()
            
            eliminado = cursor.rowcount > 0
            
            # Compactar IDs después de eliminar para mantener consecutividad
            if eliminado:
                SorteoService._compact_detalle_sorteo_ids()
            
            return eliminado
            
        except mysql.connector.Error as e:
            print(f"Error eliminando participante del sorteo: {e}")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    @staticmethod
    def actualizar_estado_participante(sorteo_id: int, documento_participante: str, nuevo_estado: EstadoParticipacion) -> bool:
        """Actualiza el estado de participación de un participante en un sorteo"""
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()
            
            query = """
                UPDATE detalle_sorteo 
                SET estado = %s
                WHERE id_sorteo = %s AND documento_participante = %s
            """
            
            cursor.execute(query, (nuevo_estado.value, sorteo_id, documento_participante))
            connection.commit()
            
            return cursor.rowcount > 0
            
        except mysql.connector.Error as e:
            print(f"Error actualizando estado del participante: {e}")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    @staticmethod
    def realizar_sorteo(sorteo_id: int) -> Optional[str]:
        """Realiza el sorteo y selecciona un ganador aleatoriamente"""
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()
            
            # Verificar que el sorteo existe y está activo
            cursor.execute("SELECT estado FROM sorteo WHERE id = %s", (sorteo_id,))
            sorteo_result = cursor.fetchone()
            
            if not sorteo_result or sorteo_result[0] != EstadoSorteo.ACTIVO.value:
                return None
            
            # Obtener participantes activos
            cursor.execute("""
                SELECT documento_participante 
                FROM detalle_sorteo 
                WHERE id_sorteo = %s AND estado = %s
                ORDER BY RAND() 
                LIMIT 1
            """, (sorteo_id, EstadoParticipacion.PARTICIPANDO.value))
            
            ganador_result = cursor.fetchone()
            
            if not ganador_result:
                return None
            
            documento_ganador = ganador_result[0]
            fecha_actual = datetime.now()
            
            # Actualizar el ganador
            cursor.execute("""
                UPDATE detalle_sorteo 
                SET estado = %s, fecha_ganador = %s
                WHERE id_sorteo = %s AND documento_participante = %s
            """, (EstadoParticipacion.GANADOR.value, fecha_actual, sorteo_id, documento_ganador))
            
            # No actualizar otros participantes como perdedores ni finalizar el sorteo automáticamente
            # El sorteo permanece activo para permitir múltiples ganadores
            
            connection.commit()
            
            return documento_ganador
            
        except mysql.connector.Error as e:
            print(f"Error realizando sorteo: {e}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    @staticmethod
    def finalizar_sorteo(sorteo_id: int) -> bool:
        """Finaliza un sorteo cambiando su estado a FINALIZADO"""
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()
            
            # Verificar que el sorteo existe (sin restricción de estado)
            cursor.execute("SELECT estado FROM sorteo WHERE id = %s", (sorteo_id,))
            sorteo_result = cursor.fetchone()
            
            if not sorteo_result:
                return False
            
            estado_actual = sorteo_result[0]
            
            # Si ya está finalizado, considerarlo como éxito
            if estado_actual == EstadoSorteo.FINALIZADO.value:
                return True
            
            fecha_actual = datetime.now()
            
            # Actualizar el estado del sorteo a finalizado
            cursor.execute("""
                UPDATE sorteo 
                SET estado = %s, fecha_finalizacion = %s
                WHERE id = %s
            """, (EstadoSorteo.FINALIZADO.value, fecha_actual, sorteo_id))
            
            # Actualizar todos los participantes activos como perdedores
            cursor.execute("""
                UPDATE detalle_sorteo 
                SET estado = %s
                WHERE id_sorteo = %s AND estado = %s
            """, (EstadoParticipacion.PERDEDOR.value, sorteo_id, EstadoParticipacion.PARTICIPANDO.value))
            
            connection.commit()
            
            # Compactar IDs de detalle_sorteo después de finalizar
            SorteoService._compact_detalle_sorteo_ids()
            
            return True
            
        except mysql.connector.Error as e:
            print(f"Error finalizando sorteo: {e}")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    @staticmethod
    def obtener_ganador_sorteo(sorteo_id: int) -> Optional[DetalleSorteoResponse]:
        """Obtiene el ganador de un sorteo finalizado"""
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT ds.*, p.nombre as nombre_participante
                FROM detalle_sorteo ds
                JOIN participantes p ON ds.documento_participante = p.documento
                WHERE ds.id_sorteo = %s AND ds.estado = %s
            """
            
            cursor.execute(query, (sorteo_id, EstadoParticipacion.GANADOR.value))
            result = cursor.fetchone()
            
            if result:
                return DetalleSorteoResponse(**result)
            return None
            
        except mysql.connector.Error as e:
            print(f"Error obteniendo ganador del sorteo: {e}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    @staticmethod
    def obtener_ganadores_sorteo(sorteo_id: int) -> List[DetalleSorteoResponse]:
        """Obtiene todos los ganadores de un sorteo"""
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT ds.*, p.nombre as nombre_participante
                FROM detalle_sorteo ds
                JOIN participantes p ON ds.documento_participante = p.documento
                WHERE ds.id_sorteo = %s AND ds.estado = %s
                ORDER BY ds.fecha_ganador DESC
            """
            
            cursor.execute(query, (sorteo_id, EstadoParticipacion.GANADOR.value))
            results = cursor.fetchall()
            
            return [DetalleSorteoResponse(**result) for result in results]
            
        except mysql.connector.Error as e:
            print(f"Error obteniendo ganadores del sorteo: {e}")
            return []
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    @staticmethod
    def obtener_todos_los_sorteos():
        """Obtiene todos los sorteos con la cantidad de participantes"""
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT s.id, s.nombre, s.descripcion, s.estado, s.fecha_creacion, s.cantidad_premio, s.ganadores_simultaneos,
                       COUNT(ds.id) as cantidad_participantes
                FROM sorteo s
                LEFT JOIN detalle_sorteo ds ON s.id = ds.id_sorteo
                WHERE s.estado = 'activo'
                GROUP BY s.id, s.nombre, s.descripcion, s.estado, s.fecha_creacion, s.cantidad_premio, s.ganadores_simultaneos
                ORDER BY s.fecha_creacion DESC
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            from models.sorteo import SorteoListResponse
            sorteos = []
            for result in results:
                sorteos.append(SorteoListResponse(**result))
            
            return sorteos
            
        except mysql.connector.Error as e:
            print(f"Error obteniendo sorteos: {e}")
            return []
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    @staticmethod
    def obtener_participante_aleatorio(sorteo_id: int) -> Optional[dict]:
        """Obtiene un participante aleatorio de un sorteo que no haya ganado"""
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor(dictionary=True)
            
            # Primero verificar si ya se alcanzó el límite de ganadores
            cursor.execute("""
                SELECT s.cantidad_premio, COUNT(ds.id) as ganadores_actuales
                FROM sorteo s
                LEFT JOIN detalle_sorteo ds ON s.id = ds.id_sorteo AND ds.estado = 'ganador'
                WHERE s.id = %s
                GROUP BY s.id, s.cantidad_premio
            """, (sorteo_id,))
            
            limite_result = cursor.fetchone()
            if not limite_result:
                return None
                
            cantidad_premio = limite_result['cantidad_premio'] or 1  # Default a 1 si es None
            ganadores_actuales = limite_result['ganadores_actuales'] or 0
            
            # Si ya se alcanzó el límite, no retornar más participantes
            if ganadores_actuales >= cantidad_premio:
                print(f"Límite de ganadores alcanzado: {ganadores_actuales}/{cantidad_premio}")
                return None
            
            # Obtener un participante aleatorio que no sea ganador
            query = """
                SELECT ds.documento_participante as documento, p.nombre
                FROM detalle_sorteo ds
                JOIN participantes p ON ds.documento_participante = p.documento
                WHERE ds.id_sorteo = %s AND ds.estado != 'ganador'
                ORDER BY RAND()
                LIMIT 1
            """
            
            cursor.execute(query, (sorteo_id,))
            result = cursor.fetchone()
            
            return result
            
        except mysql.connector.Error as e:
            print(f"Error obteniendo participante aleatorio: {e}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    @staticmethod
    def marcar_participante_ganador(sorteo_id: int, documento_participante: str) -> bool:
        """Marca un participante como ganador en un sorteo"""
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor(dictionary=True)
            
            fecha_actual = datetime.now()
            print(f"Marcando ganador - Sorteo: {sorteo_id}, Documento: {documento_participante}, Fecha: {fecha_actual}")
            
            # Verificar que el participante existe en el sorteo
            verify_query = """
                SELECT id, estado, fecha_ganador
                FROM detalle_sorteo 
                WHERE id_sorteo = %s AND documento_participante = %s
            """
            
            cursor.execute(verify_query, (sorteo_id, documento_participante))
            participante = cursor.fetchone()
            
            if not participante:
                print(f"Error: Participante {documento_participante} no encontrado en sorteo {sorteo_id}")
                return False
            
            print(f"Participante encontrado - ID: {participante['id']}, Estado actual: {participante['estado']}, Fecha ganador actual: {participante['fecha_ganador']}")
            
            # Actualizar el participante como ganador
            update_query = """
                UPDATE detalle_sorteo 
                SET estado = %s, fecha_ganador = %s
                WHERE id_sorteo = %s AND documento_participante = %s
            """
            
            cursor.execute(update_query, (EstadoParticipacion.GANADOR.value, fecha_actual, sorteo_id, documento_participante))
            connection.commit()
            
            if cursor.rowcount > 0:
                # Verificar que la actualización fue exitosa
                cursor.execute(verify_query, (sorteo_id, documento_participante))
                participante_actualizado = cursor.fetchone()
                
                print(f"Actualización exitosa - Estado: {participante_actualizado['estado']}, Fecha ganador: {participante_actualizado['fecha_ganador']}")
                
                # Validar que fecha_ganador no sea NULL
                if participante_actualizado['fecha_ganador'] is None:
                    print(f"ERROR CRÍTICO: fecha_ganador es NULL después de la actualización")
                    return False
                
                return True
            else:
                print(f"Error: No se pudo actualizar el participante")
                return False
            
        except mysql.connector.Error as e:
            print(f"Error marcando participante como ganador: {e}")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    @staticmethod
    def actualizar_sorteo(sorteo_id: int, cantidad_premio: Optional[int] = None, ganadores_simultaneos: Optional[int] = None, imagen_fondo: Optional[str] = None, nombre: Optional[str] = None, descripcion: Optional[str] = None) -> Optional[SorteoResponse]:
        """Actualiza la configuración de un sorteo"""
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor(dictionary=True)
            
            # Construir la consulta de actualización dinámicamente
            update_fields = []
            params = []
            
            if cantidad_premio is not None:
                update_fields.append("cantidad_premio = %s")
                params.append(cantidad_premio)
            
            if ganadores_simultaneos is not None:
                update_fields.append("ganadores_simultaneos = %s")
                params.append(ganadores_simultaneos)
            
            if imagen_fondo is not None:
                update_fields.append("imagen = %s")
                params.append(imagen_fondo)
            
            if nombre is not None:
                update_fields.append("nombre = %s")
                params.append(nombre)
            
            if descripcion is not None:
                update_fields.append("descripcion = %s")
                params.append(descripcion)
            
            if not update_fields:
                # Si no hay campos para actualizar, solo retornar el sorteo actual
                return SorteoService.obtener_sorteo(sorteo_id)
            
            # Agregar el ID del sorteo al final de los parámetros
            params.append(sorteo_id)
            
            query = f"UPDATE sorteo SET {', '.join(update_fields)} WHERE id = %s"
            print(f"Ejecutando query: {query}")
            print(f"Con parámetros: {params}")
            cursor.execute(query, params)
            connection.commit()
            
            print(f"Filas afectadas: {cursor.rowcount}")
            
            if cursor.rowcount > 0:
                # Retornar el sorteo actualizado
                return SorteoService.obtener_sorteo(sorteo_id)
            else:
                print(f"No se actualizó ninguna fila para sorteo_id: {sorteo_id}")
                # Verificar si el sorteo existe
                sorteo_existente = SorteoService.obtener_sorteo(sorteo_id)
                if sorteo_existente:
                    print(f"El sorteo existe, pero no se actualizó. Sorteo actual: {sorteo_existente}")
                    return sorteo_existente  # Retornar el sorteo existente aunque no se haya actualizado
                else:
                    print(f"El sorteo {sorteo_id} no existe")
                    return None
                
        except mysql.connector.Error as e:
            print(f"Error actualizando sorteo: {e}")
            print(f"Query ejecutada: {query}")
            print(f"Parámetros: {params}")
            raise e
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    @staticmethod
    def guardar_imagen_sorteo(sorteo_id: int, file: UploadFile) -> Optional[str]:
        """Guarda una imagen para un sorteo"""
        try:
            # Crear directorio de imágenes si no existe
            images_dir = "images/sorteos"
            os.makedirs(images_dir, exist_ok=True)
            
            # Generar nombre de archivo único
            file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
            filename = f"sorteo_{sorteo_id}.{file_extension}"
            file_path = os.path.join(images_dir, filename)
            
            # Guardar archivo
            with open(file_path, "wb") as buffer:
                content = file.file.read()
                buffer.write(content)
            
            # Actualizar la base de datos con la ruta de la imagen
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()
            
            query = "UPDATE sorteo SET imagen = %s WHERE id = %s"
            cursor.execute(query, (file_path, sorteo_id))
            connection.commit()
            
            return file_path
            
        except Exception as e:
            print(f"Error guardando imagen: {e}")
            return None
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
    
    @staticmethod
    def obtener_imagen_sorteo(sorteo_id: int) -> Optional[str]:
        """Obtiene la imagen de un sorteo en formato base64"""
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor(dictionary=True)
            
            query = "SELECT imagen FROM sorteo WHERE id = %s"
            cursor.execute(query, (sorteo_id,))
            result = cursor.fetchone()
            
            if result and result['imagen'] and os.path.exists(result['imagen']):
                with open(result['imagen'], "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                    return encoded_string
            
            return None
            
        except Exception as e:
            print(f"Error obteniendo imagen: {e}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    @staticmethod
    def eliminar_imagen_sorteo(sorteo_id: int) -> bool:
        """Elimina la imagen de un sorteo"""
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor(dictionary=True)
            
            # Obtener la ruta de la imagen actual
            query = "SELECT imagen FROM sorteo WHERE id = %s"
            cursor.execute(query, (sorteo_id,))
            result = cursor.fetchone()
            
            if result and result['imagen']:
                # Eliminar archivo físico si existe
                if os.path.exists(result['imagen']):
                    os.remove(result['imagen'])
                
                # Actualizar base de datos
                update_query = "UPDATE sorteo SET imagen = NULL WHERE id = %s"
                cursor.execute(update_query, (sorteo_id,))
                connection.commit()
                
                return True
            
            return False
            
        except Exception as e:
            print(f"Error eliminando imagen: {e}")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()