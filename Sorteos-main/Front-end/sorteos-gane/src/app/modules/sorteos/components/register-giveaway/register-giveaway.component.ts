import { Component } from '@angular/core';
import { ParticipantesService } from '../../../../core/services/participantes.service';
import { RegistroParticipantesResponse, RegistroSorteoConParticipantesResponse } from '../../../../core/models';

@Component({
  selector: 'app-register-giveaway',
  templateUrl: './register-giveaway.component.html',
  styleUrls: ['./register-giveaway.component.scss']
})
export class RegisterGiveawayComponent {
  showUploadModal: boolean = false;
  nombreSorteo: string = '';
  participantes: string = '';
  participantCount: number = 0;
  isRegistering: boolean = false;
  registrationMessage: string = '';

  constructor(private participantesService: ParticipantesService) {}

  openUploadModal(): void {
    this.showUploadModal = true;
  }

  closeUploadModal(): void {
    this.showUploadModal = false;
  }

  onFileUploaded(file: File): void {
    console.log('Archivo subido:', file.name);
    this.showUploadModal = false;
  }

  onParticipantsExtracted(participants: string[]): void {
    // Agregar los participantes al textarea
    const newParticipants = participants.join('\n');
    if (this.participantes.trim()) {
      this.participantes += '\n' + newParticipants;
    } else {
      this.participantes = newParticipants;
    }
    this.updateParticipantCount();
  }

  onParticipantesChange(): void {
    this.updateParticipantCount();
  }

  clearParticipants(): void {
    this.participantes = '';
    this.participantCount = 0;
  }

  private updateParticipantCount(): void {
    const lines = this.participantes.split('\n').filter(line => line.trim() !== '');
    this.participantCount = lines.length;
  }

  registrarParticipantes(): void {
    if (!this.nombreSorteo.trim()) {
      this.registrationMessage = 'Por favor, ingresa el nombre del sorteo.';
      return;
    }

    if (!this.participantes.trim()) {
      this.registrationMessage = 'Por favor, ingresa al menos un participante.';
      return;
    }

    this.isRegistering = true;
    this.registrationMessage = '';

    const participantesArray = this.participantes
      .split('\n')
      .map(line => line.trim())
      .filter(line => line !== '');

    this.participantesService.crearSorteoConParticipantes(this.nombreSorteo, participantesArray).subscribe({
      next: (response: RegistroSorteoConParticipantesResponse) => {
        this.isRegistering = false;
        this.registrationMessage = response.mensaje;
        
        if (response.errores && response.errores.length > 0) {
          console.warn('Errores durante el registro:', response.errores);
        }
        
        console.log('Sorteo creado exitosamente:', response);
        
        // Limpiar formulario después del éxito
        if (response.sorteo_id > 0) {
          this.nombreSorteo = '';
          this.participantes = '';
          this.participantCount = 0;
        }
      },
      error: (error) => {
        this.isRegistering = false;
        this.registrationMessage = 'Error al crear sorteo. Por favor, intenta nuevamente.';
        console.error('Error creando sorteo:', error);
      }
    });
  }
}