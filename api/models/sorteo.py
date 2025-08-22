from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class EstadoSorteo(str, Enum):
    ACTIVO = "activo"
    FINALIZADO = "finalizado"
    CANCELADO = "cancelado"

class EstadoParticipacion(str, Enum):
    PARTICIPANDO = "participando"
    GANADOR = "ganador"
    PERDEDOR = "perdedor"
    ELIMINADO = "eliminado"
    DESCALIFICADO = "descalificado"

class Sorteo(BaseModel):
    id: Optional[int] = None
    nombre: str
    descripcion: str
    estado: EstadoSorteo = EstadoSorteo.ACTIVO
    fecha_creacion: Optional[datetime] = None
    fecha_finalizacion: Optional[datetime] = None
    cantidad_premio: Optional[int] = None

class SorteoResponse(BaseModel):
    id: int
    nombre: str
    descripcion: str
    estado: EstadoSorteo
    fecha_creacion: datetime
    fecha_finalizacion: Optional[datetime]
    cantidad_premio: Optional[int]

class DetalleSorteo(BaseModel):
    id: Optional[int] = None
    id_sorteo: int
    documento_participante: str
    estado: EstadoParticipacion = EstadoParticipacion.PARTICIPANDO
    fecha_asignacion: Optional[datetime] = None
    fecha_ganador: Optional[datetime] = None

class DetalleSorteoResponse(BaseModel):
    id: int
    id_sorteo: int
    documento_participante: str
    estado: EstadoParticipacion
    fecha_asignacion: datetime
    fecha_ganador: Optional[datetime]
    nombre_participante: str

class CrearSorteoRequest(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    participantes: list[str]  # Lista de strings en formato "documento - nombre"

class CrearSorteoResponse(BaseModel):
    sorteo: SorteoResponse
    participantes_registrados: int
    participantes_existentes: int
    errores: list[str]
    mensaje: str

class SorteoListResponse(BaseModel):
    id: int
    nombre: str
    descripcion: str
    estado: EstadoSorteo
    fecha_creacion: datetime
    cantidad_participantes: int