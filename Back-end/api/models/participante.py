from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class Participante(BaseModel):
    """Modelo base para un participante"""
    documento: str
    nombre: str


class ParticipanteResponse(BaseModel):
    """Modelo de respuesta para un participante con información completa"""
    documento: str
    nombre: str
    fecha_registro: datetime


class RegistroParticipantesRequest(BaseModel):
    """Modelo de request para registrar múltiples participantes"""
    participantes: List[Participante]  # Lista de objetos Participante


class RegistroParticipantesResponse(BaseModel):
    """Modelo de respuesta para el registro de participantes"""
    mensaje: str
    participantes_registrados: int
    participantes_existentes: int
    errores: List[str]


class RegistroSorteoConParticipantesRequest(BaseModel):
    nombre_sorteo: str
    descripcion_sorteo: Optional[str] = None
    participantes: List[Participante]


class RegistroSorteoConParticipantesResponse(BaseModel):
    sorteo_id: int
    nombre_sorteo: str
    participantes_registrados: int
    participantes_existentes: int
    errores: List[str]
    mensaje: Optional[str] = None