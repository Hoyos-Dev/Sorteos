from fastapi import APIRouter, HTTPException
from typing import List, Optional
from models.sorteo import SorteoResponse, DetalleSorteoResponse, EstadoParticipacion, SorteoListResponse
from models.participante import RegistroSorteoConParticipantesRequest, RegistroSorteoConParticipantesResponse
from pydantic import BaseModel

from services.sorteo_service import SorteoService

class ActualizarEstadoRequest(BaseModel):
    nuevo_estado: EstadoParticipacion

class SorteoResultResponse(BaseModel):
    ganador: Optional[DetalleSorteoResponse]
    mensaje: str

router = APIRouter()

@router.get("/sorteos", response_model=List[SorteoListResponse])
def obtener_todos_los_sorteos():
    """Obtiene todos los sorteos con información básica y cantidad de participantes"""
    try:
        sorteos = SorteoService.obtener_todos_los_sorteos()
        return sorteos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

# Endpoint de eliminación removido - solo se permite finalizar sorteos

@router.post("/sorteos", response_model=RegistroSorteoConParticipantesResponse)
def crear_sorteo_con_participantes(request: RegistroSorteoConParticipantesRequest):
    """Crea un nuevo sorteo y registra participantes en él"""
    try:
        response = SorteoService.crear_sorteo_con_participantes(
            nombre_sorteo=request.nombre_sorteo,
            participantes=request.participantes,
            descripcion_sorteo=request.descripcion_sorteo
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/sorteos/{sorteo_id}", response_model=SorteoResponse)
def obtener_sorteo(sorteo_id: int):
    """Obtiene información de un sorteo específico"""
    try:
        sorteo = SorteoService.obtener_sorteo(sorteo_id)
        if not sorteo:
            raise HTTPException(status_code=404, detail="Sorteo no encontrado")
        return sorteo
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/sorteos/{sorteo_id}/participantes", response_model=List[DetalleSorteoResponse])
def obtener_participantes_sorteo(sorteo_id: int):
    """Obtiene todos los participantes de un sorteo"""
    try:
        # Verificar que el sorteo existe
        sorteo = SorteoService.obtener_sorteo(sorteo_id)
        if not sorteo:
            raise HTTPException(status_code=404, detail="Sorteo no encontrado")
        
        participantes = SorteoService.obtener_participantes_sorteo(sorteo_id)
        return participantes
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.delete("/sorteos/{sorteo_id}/participantes/{documento_participante}")
def eliminar_participante_sorteo(sorteo_id: int, documento_participante: str):
    """Elimina un participante de un sorteo"""
    try:
        # Verificar que el sorteo existe
        sorteo = SorteoService.obtener_sorteo(sorteo_id)
        if not sorteo:
            raise HTTPException(status_code=404, detail="Sorteo no encontrado")
        
        eliminado = SorteoService.eliminar_participante_sorteo(sorteo_id, documento_participante)
        if not eliminado:
            raise HTTPException(status_code=404, detail="Participante no encontrado en el sorteo")
        
        return {"mensaje": f"Participante {documento_participante} eliminado del sorteo {sorteo_id}"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.put("/sorteos/{sorteo_id}/participantes/{documento_participante}/estado")
def actualizar_estado_participante(sorteo_id: int, documento_participante: str, request: ActualizarEstadoRequest):
    """Actualiza el estado de participación de un participante en un sorteo"""
    try:
        # Verificar que el sorteo existe
        sorteo = SorteoService.obtener_sorteo(sorteo_id)
        if not sorteo:
            raise HTTPException(status_code=404, detail="Sorteo no encontrado")
        
        actualizado = SorteoService.actualizar_estado_participante(sorteo_id, documento_participante, request.nuevo_estado)
        if not actualizado:
            raise HTTPException(status_code=404, detail="Participante no encontrado en el sorteo")
        
        return {"mensaje": f"Estado del participante {documento_participante} actualizado a {request.nuevo_estado.value}"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.post("/sorteos/{sorteo_id}/realizar", response_model=SorteoResultResponse)
def realizar_sorteo(sorteo_id: int):
    """Realiza el sorteo y selecciona un ganador"""
    try:
        # Verificar que el sorteo existe
        sorteo = SorteoService.obtener_sorteo(sorteo_id)
        if not sorteo:
            raise HTTPException(status_code=404, detail="Sorteo no encontrado")
        
        documento_ganador = SorteoService.realizar_sorteo(sorteo_id)
        if not documento_ganador:
            raise HTTPException(status_code=400, detail="No se pudo realizar el sorteo. Verifique que esté activo y tenga participantes.")
        
        # Obtener información completa del ganador
        ganador = SorteoService.obtener_ganador_sorteo(sorteo_id)
        
        return SorteoResultResponse(
            ganador=ganador,
            mensaje=f"Sorteo realizado exitosamente. Ganador: {documento_ganador}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/sorteos/{sorteo_id}/ganador", response_model=DetalleSorteoResponse)
def obtener_ganador_sorteo(sorteo_id: int):
    """Obtiene el ganador de un sorteo finalizado"""
    try:
        # Verificar que el sorteo existe
        sorteo = SorteoService.obtener_sorteo(sorteo_id)
        if not sorteo:
            raise HTTPException(status_code=404, detail="Sorteo no encontrado")
        
        ganador = SorteoService.obtener_ganador_sorteo(sorteo_id)
        if not ganador:
            raise HTTPException(status_code=404, detail="No hay ganador para este sorteo")
        
        return ganador
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/sorteos/{sorteo_id}/ganadores", response_model=List[DetalleSorteoResponse])
def obtener_ganadores_sorteo(sorteo_id: int):
    """Obtiene todos los ganadores de un sorteo"""
    try:
        # Verificar que el sorteo existe
        sorteo = SorteoService.obtener_sorteo(sorteo_id)
        if not sorteo:
            raise HTTPException(status_code=404, detail="Sorteo no encontrado")
        
        ganadores = SorteoService.obtener_ganadores_sorteo(sorteo_id)
        return ganadores
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.put("/sorteos/{sorteo_id}/finalizar")
def finalizar_sorteo(sorteo_id: int):
    """Finaliza un sorteo cambiando su estado a finalizado"""
    try:
        # Verificar que el sorteo existe
        sorteo = SorteoService.obtener_sorteo(sorteo_id)
        if not sorteo:
            raise HTTPException(status_code=404, detail=f"El sorteo con ID {sorteo_id} no existe")
        
        # Permitir finalizar sorteos sin restricciones de estado
        # (El botón 'Eliminar' ahora funciona como finalizar)
        
        finalizado = SorteoService.finalizar_sorteo(sorteo_id)
        if not finalizado:
            raise HTTPException(status_code=400, detail=f"No se pudo finalizar el sorteo {sorteo_id}. El sorteo ya está finalizado o ocurrió un error.")
        
        return {"mensaje": f"Sorteo {sorteo_id} finalizado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.post("/admin/compact-detalle-ids")
def compact_detalle_sorteo_ids():
    """Compacta los IDs de detalle_sorteo para que sean consecutivos desde 1"""
    try:
        SorteoService._compact_detalle_sorteo_ids()
        return {"mensaje": "IDs de detalle_sorteo compactados exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error compactando IDs: {str(e)}")

class ParticipanteAleatorioResponse(BaseModel):
    ok: bool
    participante: Optional[dict]
    mensaje: str

@router.get("/obtener-participante-aleatorio/{sorteo_id}", response_model=ParticipanteAleatorioResponse)
def obtener_participante_aleatorio(sorteo_id: int):
    """Obtiene un participante aleatorio de un sorteo que no haya ganado"""
    try:
        # Verificar que el sorteo existe
        sorteo = SorteoService.obtener_sorteo(sorteo_id)
        if not sorteo:
            raise HTTPException(status_code=404, detail="Sorteo no encontrado")
        
        participante = SorteoService.obtener_participante_aleatorio(sorteo_id)
        
        if participante:
            return ParticipanteAleatorioResponse(
                ok=True,
                participante=participante,
                mensaje="Participante aleatorio obtenido exitosamente"
            )
        else:
            return ParticipanteAleatorioResponse(
                ok=False,
                participante=None,
                mensaje="No hay participantes disponibles para el sorteo"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.post("/sorteos/{sorteo_id}/marcar-ganador/{documento_participante}")
def marcar_participante_ganador(sorteo_id: int, documento_participante: str):
    """Marca un participante como ganador en un sorteo"""
    try:
        # Verificar que el sorteo existe
        sorteo = SorteoService.obtener_sorteo(sorteo_id)
        if not sorteo:
            raise HTTPException(status_code=404, detail="Sorteo no encontrado")
        
        marcado = SorteoService.marcar_participante_ganador(sorteo_id, documento_participante)
        
        if marcado:
            return {"mensaje": f"Participante {documento_participante} marcado como ganador exitosamente"}
        else:
            raise HTTPException(status_code=404, detail="Participante no encontrado en el sorteo")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.post("/sorteos/{sorteo_id}/finalizar")
def finalizar_sorteo(sorteo_id: int):
    """Finaliza un sorteo cambiando su estado a FINALIZADO"""
    try:
        # Verificar que el sorteo existe
        sorteo = SorteoService.obtener_sorteo(sorteo_id)
        if not sorteo:
            raise HTTPException(status_code=404, detail="Sorteo no encontrado")
        
        finalizado = SorteoService.finalizar_sorteo(sorteo_id)
        
        if finalizado:
            return {"mensaje": f"Sorteo {sorteo_id} finalizado exitosamente"}
        else:
            raise HTTPException(status_code=400, detail="No se pudo finalizar el sorteo")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")