import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, Subject } from 'rxjs';
import { tap, map } from 'rxjs/operators';

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

@Injectable({
  providedIn: 'root'
})
export class ParticipantesService {
  private apiUrl = 'http://localhost:8001';
  private sorteoCreado = new Subject<void>();
  private ganadorMarcado = new Subject<void>();

  constructor(private http: HttpClient) { }

  // Observable para notificar cuando se crea un nuevo sorteo
  get sorteoCreado$() {
    return this.sorteoCreado.asObservable();
  }

  // Observable para notificar cuando se marca un ganador
  get ganadorMarcado$() {
    return this.ganadorMarcado.asObservable();
  }

  registrarParticipantes(participantes: string[]): Observable<RegistroParticipantesResponse> {
    // Procesar las líneas del textarea en formato "documento - nombre"
    const participantesObjetos: Participante[] = participantes.map(linea => {
      const partes = linea.split(' - ');
      if (partes.length >= 2) {
        return {
          documento: partes[0].trim(),
          nombre: partes.slice(1).join(' - ').trim()
        };
      } else {
        // Si no tiene el formato correcto, usar toda la línea como nombre
        return {
          documento: '',
          nombre: linea.trim()
        };
      }
    });

    const request: RegistroParticipantesRequest = {
      participantes: participantesObjetos
    };
    return this.http.post<RegistroParticipantesResponse>(`${this.apiUrl}/participantes`, request);
  }

  obtenerParticipantes(): Observable<ParticipanteResponse[]> {
    return this.http.get<ParticipanteResponse[]>(`${this.apiUrl}/participantes`);
  }

  obtenerParticipante(documento: string): Observable<ParticipanteResponse> {
    return this.http.get<ParticipanteResponse>(`${this.apiUrl}/participantes/${documento}`);
  }

  crearSorteoConParticipantes(nombreSorteo: string, participantes: string[]): Observable<RegistroSorteoConParticipantesResponse> {
    // Procesar las líneas del textarea en formato "documento - nombre"
    const participantesObjetos: Participante[] = participantes.map(linea => {
      const partes = linea.split(' - ');
      if (partes.length >= 2) {
        return {
          documento: partes[0].trim(),
          nombre: partes.slice(1).join(' - ').trim()
        };
      } else {
        // Si no tiene el formato correcto, usar toda la línea como nombre
        return {
          documento: '',
          nombre: linea.trim()
        };
      }
    });

    const request: RegistroSorteoConParticipantesRequest = {
      nombre_sorteo: nombreSorteo,
      descripcion_sorteo: `Descripción ${nombreSorteo}`,
      participantes: participantesObjetos
    };
    return this.http.post<RegistroSorteoConParticipantesResponse>(`${this.apiUrl}/sorteos`, request)
      .pipe(
        tap(response => {
          if (response.sorteo_id > 0) {
            this.sorteoCreado.next();
          }
        })
      );
  }

  obtenerTodosLosSorteos(): Observable<SorteoListResponse[]> {
    return this.http.get<SorteoListResponse[]>(`${this.apiUrl}/sorteos`)
      .pipe(
        map(sorteos => {
          // Mostrar sorteos activos y finalizados (para poder eliminar finalizados)
          return sorteos.filter(sorteo => sorteo.estado === 'activo' || sorteo.estado === 'finalizado');
        })
      );
  }

  finalizarSorteo(sorteoId: number): Observable<{mensaje: string}> {
    return this.http.post<{mensaje: string}>(`${this.apiUrl}/sorteos/${sorteoId}/finalizar`, {})
      .pipe(
        tap(() => {
          // Notificar que se ha finalizado un sorteo para actualizar la lista
          this.sorteoCreado.next();
        })
      );
  }

  eliminarSorteo(sorteoId: number): Observable<{mensaje: string}> {
    return this.http.delete<{mensaje: string}>(`${this.apiUrl}/sorteos/${sorteoId}`)
      .pipe(
        tap(() => {
          // Notificar que se ha eliminado un sorteo para actualizar la lista
          this.sorteoCreado.next();
        })
      );
  }

  obtenerGanadoresPorSorteo(sorteoId: number): Observable<Ganador[]> {
    return this.http.get<Ganador[]>(`${this.apiUrl}/sorteos/${sorteoId}/ganadores`);
  }

  marcarGanador(sorteoId: number, documento: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/sorteos/${sorteoId}/marcar-ganador/${documento}`, {})
      .pipe(
        tap(() => {
          // Notificar que se ha marcado un ganador para actualizar las listas
          this.ganadorMarcado.next();
        })
      );
  }
}