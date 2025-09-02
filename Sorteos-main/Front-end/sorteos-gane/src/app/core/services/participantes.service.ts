import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, Subject } from 'rxjs';
import { tap, map } from 'rxjs/operators';
import { environment } from '../../environment';
import {
  Participante,
  RegistroParticipantesRequest,
  RegistroParticipantesResponse,
  ParticipanteResponse,
  RegistroSorteoConParticipantesRequest,
  RegistroSorteoConParticipantesResponse,
  SorteoListResponse,
  Ganador,
} from '../models';

@Injectable({ providedIn: 'root' })
export class ParticipantesService {
  private apiUrl = environment.apiUrl;
  private sorteoCreado = new Subject<void>();
  private ganadorMarcado = new Subject<void>();

  constructor(private http: HttpClient) {}

  get sorteoCreado$() { return this.sorteoCreado.asObservable(); }
  get ganadorMarcado$() { return this.ganadorMarcado.asObservable(); }

  registrarParticipantes(participantes: string[]): Observable<RegistroParticipantesResponse> {
    const participantesObjetos: Participante[] = participantes.map(linea => {
      const partes = linea.split(' - ');
      if (partes.length >= 2) {
        return { documento: partes[0].trim(), nombre: partes.slice(1).join(' - ').trim() };
      } else {
        return { documento: '', nombre: linea.trim() };
      }
    });

    const request: RegistroParticipantesRequest = { participantes: participantesObjetos };
    return this.http.post<RegistroParticipantesResponse>(`${this.apiUrl}/participantes`, request);
  }

  obtenerParticipantes(): Observable<ParticipanteResponse[]> {
    return this.http.get<ParticipanteResponse[]>(`${this.apiUrl}/participantes`);
  }

  obtenerParticipante(documento: string): Observable<ParticipanteResponse> {
    return this.http.get<ParticipanteResponse>(`${this.apiUrl}/participantes/${documento}`);
  }

  crearSorteoConParticipantes(nombreSorteo: string, participantes: string[]): Observable<RegistroSorteoConParticipantesResponse> {
    const participantesObjetos: Participante[] = participantes.map(linea => {
      const partes = linea.split(' - ');
      if (partes.length >= 2) {
        return { documento: partes[0].trim(), nombre: partes.slice(1).join(' - ').trim() };
      } else {
        return { documento: '', nombre: linea.trim() };
      }
    });

    const request: RegistroSorteoConParticipantesRequest = {
      nombre_sorteo: nombreSorteo,
      descripcion_sorteo: `Descripción ${nombreSorteo}`,
      participantes: participantesObjetos,
    };
    return this.http.post<RegistroSorteoConParticipantesResponse>(`${this.apiUrl}/sorteos`, request)
      .pipe(tap(response => { if (response.sorteo_id > 0) { this.sorteoCreado.next(); } }));
  }

  obtenerTodosLosSorteos(): Observable<SorteoListResponse[]> {
    return this.http.get<SorteoListResponse[]>(`${this.apiUrl}/sorteos`).pipe(
      map(sorteos => sorteos.filter(s => s.estado === 'activo' || s.estado === 'finalizado'))
    );
  }

  finalizarSorteo(sorteoId: number): Observable<{ mensaje: string }> {
    return this.http.post<{ mensaje: string }>(`${this.apiUrl}/sorteos/${sorteoId}/finalizar`, {})
      .pipe(tap(() => { this.sorteoCreado.next(); }));
  }

  eliminarSorteo(sorteoId: number): Observable<{ mensaje: string }> {
    return this.http.delete<{ mensaje: string }>(`${this.apiUrl}/sorteos/${sorteoId}`).pipe(tap(() => { this.sorteoCreado.next(); }));
  }

  obtenerGanadoresPorSorteo(sorteoId: number): Observable<Ganador[]> {
    return this.http.get<Ganador[]>(`${this.apiUrl}/sorteos/${sorteoId}/ganadores`);
  }

  marcarGanador(sorteoId: number, documento: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/sorteos/${sorteoId}/marcar-ganador/${documento}`, {}).pipe(tap(() => { this.ganadorMarcado.next(); }));
  }
}


