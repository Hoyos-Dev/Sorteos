from typing import List, Tuple
from datetime import datetime
import logging
import mysql.connector

from models.participante import Participante, ParticipanteResponse, RegistroParticipantesResponse, RegistroSorteoConParticipantesResponse
# Importación removida para evitar dependencia circular
from config.database import DatabaseConnection

# Configurar logging
logger = logging.getLogger(__name__)


class ParticipanteService:
    """Servicio para manejar la lógica de negocio de participantes"""
    
    @staticmethod
    def parse_participantes(participantes_texto: List[str]) -> Tuple[List[Participante], List[str]]:
        """Parsea la lista de participantes desde el formato texto"""
        participantes = []
        errores = []
        
        for linea in participantes_texto:
            linea = linea.strip()
            if not linea:
                continue
                
            # Formato esperado: "documento - nombre"
            if " - " in linea:
                partes = linea.split(" - ", 1)
                if len(partes) == 2:
                    documento = partes[0].strip()
                    nombre = partes[1].strip()
                    
                    if documento and nombre:
                        participantes.append(Participante(documento=documento, nombre=nombre))
                    else:
                        errores.append(f"Línea inválida (documento o nombre vacío): {linea}")
                else:
                    errores.append(f"Formato inválido: {linea}")
            else:
                errores.append(f"Formato inválido (falta ' - '): {linea}")
        
        return participantes, errores
    
    @staticmethod
    def participante_existe(documento: str) -> bool:
        """Verifica si un participante ya existe en la base de datos"""
        query = "SELECT documento FROM participantes WHERE documento = %s"
        result = DatabaseConnection.execute_query(query, (documento,), fetch_one=True)
        return result is not None
    
    @staticmethod
    def crear_participante(participante: Participante) -> bool:
        """Crea un nuevo participante en la base de datos"""
        try:
            query = "INSERT INTO participantes (documento, nombre, fecha_registro) VALUES (%s, %s, %s)"
            params = (participante.documento, participante.nombre, datetime.now())
            rows_affected = DatabaseConnection.execute_query(query, params)
            
            if rows_affected > 0:
                logger.info(f"Participante registrado: {participante.documento} - {participante.nombre}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error creando participante {participante.documento}: {str(e)}")
            raise e
    
    @staticmethod
    def registrar_participantes(participantes_texto: List[str]) -> RegistroParticipantesResponse:
        """Registra múltiples participantes desde el textarea"""
        # Parsear participantes
        participantes, errores_parsing = ParticipanteService.parse_participantes(participantes_texto)
        
        if not participantes and errores_parsing:
            raise ValueError(f"No se pudieron procesar los participantes: {errores_parsing}")
        
        return ParticipanteService.registrar_participantes_objetos(participantes, errores_parsing)
    
    @staticmethod
    def registrar_participantes_objetos(participantes: List[Participante], errores_previos: List[str] = None) -> RegistroParticipantesResponse:
        """Registra múltiples participantes desde objetos Participante"""
        if errores_previos is None:
            errores_previos = []
            
        participantes_registrados = 0
        participantes_existentes = 0
        errores_db = []
        
        for participante in participantes:
            try:
                # Verificar si el participante ya existe
                if ParticipanteService.participante_existe(participante.documento):
                    participantes_existentes += 1
                    logger.info(f"Participante ya existe: {participante.documento}")
                else:
                    # Crear nuevo participante
                    if ParticipanteService.crear_participante(participante):
                        participantes_registrados += 1
                        
            except mysql.connector.Error as err:
                error_msg = f"Error registrando {participante.documento}: {str(err)}"
                errores_db.append(error_msg)
                logger.error(error_msg)
            except Exception as e:
                error_msg = f"Error inesperado registrando {participante.documento}: {str(e)}"
                errores_db.append(error_msg)
                logger.error(error_msg)
        
        # Preparar respuesta
        mensaje = f"Proceso completado. Registrados: {participantes_registrados}, Ya existían: {participantes_existentes}"
        
        return RegistroParticipantesResponse(
            mensaje=mensaje,
            participantes_registrados=participantes_registrados,
            participantes_existentes=participantes_existentes,
            errores=errores_previos + errores_db
        )
    
    @staticmethod
    def obtener_todos_participantes() -> List[ParticipanteResponse]:
        """Obtiene todos los participantes registrados"""
        query = "SELECT documento, nombre, fecha_registro FROM participantes ORDER BY fecha_registro DESC"
        participantes_data = DatabaseConnection.execute_query(query, fetch_all=True)
        
        return [ParticipanteResponse(**participante) for participante in participantes_data]
    
    @staticmethod
    def obtener_participante_por_documento(documento: str) -> ParticipanteResponse:
        """Obtiene un participante específico por su documento"""
        query = "SELECT documento, nombre, fecha_registro FROM participantes WHERE documento = %s"
        participante_data = DatabaseConnection.execute_query(query, (documento,), fetch_one=True)
        
        if not participante_data:
            raise ValueError(f"Participante con documento {documento} no encontrado")
        
        return ParticipanteResponse(**participante_data)
    
    # Método removido para evitar dependencia circular - funcionalidad movida a SorteoService