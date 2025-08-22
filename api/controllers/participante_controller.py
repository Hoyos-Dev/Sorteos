from fastapi import APIRouter, HTTPException, status
from typing import List
import logging

from models.participante import (
    RegistroParticipantesRequest, 
    RegistroParticipantesResponse, 
    ParticipanteResponse
)
from services.participante_service import ParticipanteService

# Configurar logging
logger = logging.getLogger(__name__)

# Crear router
router = APIRouter(
    prefix="/participantes",
    tags=["participantes"]
)


@router.post("/", response_model=RegistroParticipantesResponse)
async def registrar_participantes(request: RegistroParticipantesRequest):
    """
    Registra múltiples participantes desde el textarea del frontend.
    
    Formato esperado en cada línea: "documento - nombre"
    
    Args:
        request: Objeto con la lista de participantes en formato texto
    
    Returns:
        RegistroParticipantesResponse: Resultado del registro con estadísticas y errores
    
    Raises:
        HTTPException: Si hay errores en el procesamiento
    """
    try:
        logger.info(f"Iniciando registro de {len(request.participantes)} participantes")
        
        if not request.participantes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La lista de participantes no puede estar vacía"
            )
        
        # Procesar participantes usando el servicio
        resultado = ParticipanteService.registrar_participantes_objetos(request.participantes)
        
        logger.info(f"Registro completado: {resultado.participantes_registrados} nuevos, {resultado.participantes_existentes} existentes")
        
        return resultado
        
    except ValueError as ve:
        logger.error(f"Error de validación: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Error inesperado en registro de participantes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get("/", response_model=List[ParticipanteResponse])
async def obtener_participantes():
    """
    Obtiene todos los participantes registrados.
    
    Returns:
        List[ParticipanteResponse]: Lista de todos los participantes con su información completa
    
    Raises:
        HTTPException: Si hay errores al consultar la base de datos
    """
    try:
        logger.info("Obteniendo lista de participantes")
        
        participantes = ParticipanteService.obtener_todos_participantes()
        
        logger.info(f"Se encontraron {len(participantes)} participantes")
        
        return participantes
        
    except Exception as e:
        logger.error(f"Error obteniendo participantes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get("/{documento}", response_model=ParticipanteResponse)
async def obtener_participante(documento: str):
    """
    Obtiene un participante específico por su documento.
    
    Args:
        documento: Número de documento del participante
    
    Returns:
        ParticipanteResponse: Información completa del participante
    
    Raises:
        HTTPException: Si el participante no existe o hay errores en la consulta
    """
    try:
        logger.info(f"Buscando participante con documento: {documento}")
        
        participante = ParticipanteService.obtener_participante_por_documento(documento)
        
        logger.info(f"Participante encontrado: {participante.nombre}")
        
        return participante
        
    except ValueError as ve:
        logger.warning(f"Participante no encontrado: {documento}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Error obteniendo participante {documento}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )