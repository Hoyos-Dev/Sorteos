import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environment';
import { UpdateSorteoRequest, SorteoResponse, ParticipanteSorteo } from '../models';

@Injectable({ providedIn: 'root' })
export class SorteosService {
  private apiUrl = environment.apiUrl;
  constructor(private http: HttpClient) {}

  updateSorteo(sorteoId: number, data: UpdateSorteoRequest): Observable<SorteoResponse> {
    return this.http.put<SorteoResponse>(`${this.apiUrl}/sorteos/${sorteoId}`, data);
  }

  uploadSorteoImage(sorteoId: number, imageFile: File): Observable<{ mensaje: string; imagen_url: string }> {
    const formData = new FormData();
    formData.append('file', imageFile);
    return this.http.post<{ mensaje: string; imagen_url: string }>(`${this.apiUrl}/sorteos/${sorteoId}/imagen`, formData);
  }

  getSorteoImage(sorteoId: number): Observable<{ imagen_url: string }> {
    return this.http.get<{ imagen_url: string }>(`${this.apiUrl}/sorteos/${sorteoId}/imagen`);
  }

  deleteSorteoImage(sorteoId: number): Observable<{ mensaje: string }> {
    return this.http.delete<{ mensaje: string }>(`${this.apiUrl}/sorteos/${sorteoId}/imagen`);
  }

  getParticipantesSorteo(sorteoId: number): Observable<ParticipanteSorteo[]> {
    return this.http.get<ParticipanteSorteo[]>(`${this.apiUrl}/sorteos/${sorteoId}/participantes`);
  }
}


