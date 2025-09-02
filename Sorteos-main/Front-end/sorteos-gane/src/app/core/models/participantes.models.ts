export interface Participante {
  documento: string;
  nombre: string;
  telefono?: string;
  email?: string;
}

export interface RegistroParticipantesRequest {
  participantes: Participante[];
}

export interface RegistroParticipantesResponse {
  mensaje: string;
  participantes_registrados: number;
  participantes_existentes: number;
  errores: string[];
}

export interface ParticipanteResponse {
  documento: string;
  nombre: string;
  fecha_registro: string;
}

export interface RegistroSorteoConParticipantesRequest {
  nombre_sorteo: string;
  descripcion_sorteo?: string;
  participantes: Participante[];
}

export interface RegistroSorteoConParticipantesResponse {
  sorteo_id: number;
  nombre_sorteo: string;
  participantes_registrados: number;
  participantes_existentes: number;
  errores: string[];
  mensaje: string;
}

export interface SorteoListResponse {
  id: number;
  nombre: string;
  descripcion: string;
  estado: string;
  fecha_creacion: string;
  cantidad_participantes: number;
  cantidad_premio: number;
  ganadores_simultaneos: number;
}

export interface Ganador {
  documento_participante: string;
  nombre_participante: string;
  fecha_ganador: string;
  id: number;
  id_sorteo: number;
  estado: string;
  fecha_asignacion: string;
}


