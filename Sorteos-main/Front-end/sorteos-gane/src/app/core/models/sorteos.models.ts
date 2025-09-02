export interface UpdateSorteoRequest {
  cantidad_premio?: number;
  ganadores_simultaneos?: number;
  nombre?: string;
  descripcion?: string;
}

export interface SorteoResponse {
  id: number;
  nombre: string;
  descripcion: string;
  estado: string;
  fecha_creacion: string;
  fecha_finalizacion?: string;
  cantidad_premio?: number;
  ganadores_simultaneos?: number;
  imagen_url?: string;
}

export interface ParticipanteSorteo {
  id: number;
  documento: string;
  nombre: string;
  estado: 'participando' | 'ganador' | 'perdedor' | 'eliminado' | 'descalificado';
  fecha_asignacion: string;
  fecha_ganador?: string;
}


