from fastapi import APIRouter, HTTPException, UploadFile, File
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

# Request model for updating sorteo
class UpdateSorteoRequest(BaseModel):
    cantidad_premio: Optional[int] = None
    ganadores_simultaneos: Optional[int] = None
    imagen_fondo: Optional[str] = None
    nombre: Optional[str] = None
    descripcion: Optional[str] = None

@router.put("/sorteos/{sorteo_id}", response_model=SorteoResponse)
def actualizar_sorteo(sorteo_id: int, request: UpdateSorteoRequest):
    """Actualiza la configuración de un sorteo"""
    try:
        # Verificar que el sorteo existe
        sorteo = SorteoService.obtener_sorteo(sorteo_id)
        if not sorteo:
            raise HTTPException(status_code=404, detail="Sorteo no encontrado")
        
        # Actualizar el sorteo
        sorteo_actualizado = SorteoService.actualizar_sorteo(
            sorteo_id, 
            request.cantidad_premio,
            request.ganadores_simultaneos,
            request.imagen_fondo,
            request.nombre,
            request.descripcion
        )
        
        if sorteo_actualizado:
            return sorteo_actualizado
        else:
            print(f"Error: sorteo_actualizado es None para sorteo_id: {sorteo_id}")
            print(f"Request data: cantidad_premio={request.cantidad_premio}, imagen_fondo={request.imagen_fondo}, nombre={request.nombre}, descripcion={request.descripcion}")
            raise HTTPException(status_code=400, detail="No se pudo actualizar el sorteo")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en actualizar_sorteo controller: {e}")
        print(f"Tipo de error: {type(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.post("/sorteos/{sorteo_id}/imagen")
def subir_imagen_sorteo(sorteo_id: int, file: UploadFile = File(...)):
    """Sube una imagen para un sorteo"""
    try:
        print(f"=== SUBIENDO IMAGEN PARA SORTEO {sorteo_id} ===")
        print(f"Archivo recibido: {file.filename}")
        print(f"Content type: {file.content_type}")
        print(f"Tamaño: {file.size if hasattr(file, 'size') else 'desconocido'}")
        
        # Verificar que el sorteo existe
        sorteo = SorteoService.obtener_sorteo(sorteo_id)
        if not sorteo:
            raise HTTPException(status_code=404, detail="Sorteo no encontrado")
        
        # Validar tipo de archivo
        if not file.content_type.startswith('image/'):
            print(f"Error: Tipo de archivo inválido: {file.content_type}")
            raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")
        
        # Guardar la imagen
        imagen_guardada = SorteoService.guardar_imagen_sorteo(sorteo_id, file)
        
        if imagen_guardada:
            print(f"Imagen guardada exitosamente en: {imagen_guardada}")
            return {"mensaje": "Imagen subida exitosamente", "ruta": imagen_guardada}
        else:
            print("Error: No se pudo guardar la imagen")
            raise HTTPException(status_code=400, detail="No se pudo guardar la imagen")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en subir_imagen_sorteo controller: {e}")
        print(f"Tipo de error: {type(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/sorteos/{sorteo_id}/imagen")
def obtener_imagen_sorteo(sorteo_id: int):
    """Obtiene la imagen de un sorteo"""
    try:
        # Verificar que el sorteo existe
        sorteo = SorteoService.obtener_sorteo(sorteo_id)
        if not sorteo:
            raise HTTPException(status_code=404, detail="Sorteo no encontrado")
        
        imagen = SorteoService.obtener_imagen_sorteo(sorteo_id)
        
        if imagen:
            return {"imagen": imagen}
        else:
            raise HTTPException(status_code=404, detail="Imagen no encontrada")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.delete("/sorteos/{sorteo_id}/imagen")
def eliminar_imagen_sorteo(sorteo_id: int):
    """Elimina la imagen de un sorteo"""
    try:
        # Verificar que el sorteo existe
        sorteo = SorteoService.obtener_sorteo(sorteo_id)
        if not sorteo:
            raise HTTPException(status_code=404, detail="Sorteo no encontrado")
        
        eliminada = SorteoService.eliminar_imagen_sorteo(sorteo_id)
        
        if eliminada:
            return {"mensaje": "Imagen eliminada exitosamente"}
        else:
            raise HTTPException(status_code=404, detail="Imagen no encontrada")
    except HTTPException:
        raise
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

class MultiplesParticipantesResponse(BaseModel):
    ok: bool
    participantes: List[dict]
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

@router.get("/obtener-participantes-aleatorios/{sorteo_id}/{cantidad}", response_model=MultiplesParticipantesResponse)
def obtener_multiples_participantes_aleatorios(sorteo_id: int, cantidad: int):
    """Obtiene múltiples participantes aleatorios únicos de un sorteo que no hayan ganado"""
    try:
        # Verificar que el sorteo existe
        sorteo = SorteoService.obtener_sorteo(sorteo_id)
        if not sorteo:
            raise HTTPException(status_code=404, detail="Sorteo no encontrado")
        
        # Validar que la cantidad sea válida
        if cantidad < 1 or cantidad > 10:  # Límite de 10 participantes por solicitud
            raise HTTPException(status_code=400, detail="La cantidad de participantes debe estar entre 1 y 10")
        
        # Obtener múltiples participantes únicos
        participantes = SorteoService.obtener_multiples_participantes_aleatorios(sorteo_id, cantidad)
        
        if participantes:
            return MultiplesParticipantesResponse(
                ok=True,
                participantes=participantes,
                mensaje=f"Se obtuvieron {len(participantes)} participantes aleatorios"
            )
        else:
            return MultiplesParticipantesResponse(
                ok=False,
                participantes=[],
                mensaje="No hay suficientes participantes disponibles para el sorteo"
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