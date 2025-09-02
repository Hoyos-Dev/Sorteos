import { Component, Input, Output, EventEmitter, OnInit, OnChanges, SimpleChanges, OnDestroy } from '@angular/core';
import { ParticipantesService } from '../../../../core/services/participantes.service';
import { Ganador } from '../../../../core/models';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-info-giveaway',
  templateUrl: './info-giveaway.component.html',
  styleUrls: ['./info-giveaway.component.scss']
})
export class InfoGiveawayComponent implements OnInit, OnChanges, OnDestroy {
  @Input() mostrar: boolean = false;
  @Input() sorteo: any;
  @Input() sorteoDetalle: any;
  @Output() closeModal = new EventEmitter<void>();

  ganadores: Ganador[] = [];
  private subscription: Subscription = new Subscription();

  constructor(private participantesService: ParticipantesService) { }

  ngOnInit(): void {
    // Cargar ganadores cuando se inicializa el componente
    const sorteoId = this.sorteoDetalle?.id || this.sorteo?.id;
    if (sorteoId) {
      this.cargarGanadores();
    }
    
    // Suscribirse a las notificaciones de ganador marcado
    this.subscription.add(
      this.participantesService.ganadorMarcado$.subscribe(() => {
        this.cargarGanadores();
      })
    );
  }

  ngOnChanges(changes: SimpleChanges): void {
    if ((changes['sorteo'] && this.sorteo) || (changes['sorteoDetalle'] && this.sorteoDetalle)) {
      console.log('Info-giveaway - sorteo completo:', JSON.stringify(this.sorteo, null, 2));
      console.log('Info-giveaway - sorteoDetalle completo:', JSON.stringify(this.sorteoDetalle, null, 2));
      console.log('Info-giveaway - cantidad_premio del sorteo:', this.sorteo?.cantidad_premio);
      console.log('Info-giveaway - cantidadPremio del sorteo:', this.sorteo?.cantidadPremio);
      this.cargarGanadores();
    }
  }

  cargarGanadores(): void {
    const sorteoId = this.sorteoDetalle?.id || this.sorteo?.id;
    if (sorteoId) {
      this.participantesService.obtenerGanadoresPorSorteo(sorteoId)
        .subscribe({
          next: (ganadores) => {
            this.ganadores = ganadores;
            // Si sorteoDetalle existe, actualizar sus ganadores
            if (this.sorteoDetalle) {
              this.sorteoDetalle.ganadores = ganadores;
            }
          },
          error: (error) => {
            console.error('Error al cargar ganadores:', error);
            this.ganadores = [];
          }
        });
    }
  }

  formatearFecha(fecha: string | Date): string {
    if (!fecha) return 'No disponible';
    
    try {
      const fechaObj = typeof fecha === 'string' ? new Date(fecha) : fecha;
      return fechaObj.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (error) {
      return 'Fecha inválida';
    }
  }

  onClose(): void {
    this.closeModal.emit();
  }

  onBackdropClick(event: Event): void {
    if (event.target === event.currentTarget) {
      this.onClose();
    }
  }

  ngOnDestroy(): void {
    this.subscription.unsubscribe();
  }
}