import { Component, OnInit, OnDestroy } from '@angular/core';
import { Router } from '@angular/router';
import { Subscription } from 'rxjs';
import { ParticipantesService, SorteoListResponse } from '../../services/participantes.service';

@Component({
  selector: 'app-list-giveaways',
  templateUrl: './list-giveaways.component.html',
  styleUrls: ['./list-giveaways.component.scss']
})
export class ListGiveawaysComponent implements OnInit, OnDestroy {
  sorteos: SorteoListResponse[] = [];
  private subscription: Subscription = new Subscription();
  isModalVisible: boolean = false;
  selectedSorteo: SorteoListResponse | null = null;

  constructor(
    private router: Router,
    private participantesService: ParticipantesService
  ) { }

  ngOnInit(): void {
    this.cargarSorteos();
    
    // Suscribirse al evento de sorteo creado para recargar la lista
    this.subscription.add(
      this.participantesService.sorteoCreado$.subscribe(() => {
        this.cargarSorteos();
      })
    );
  }

  ngOnDestroy(): void {
    this.subscription.unsubscribe();
  }

  cargarSorteos(): void {
    this.participantesService.obtenerTodosLosSorteos().subscribe({
      next: (sorteos) => {
        this.sorteos = sorteos;
      },
      error: (error) => {
        console.error('Error al cargar sorteos:', error);
      }
    });
  }

  onPlayClick(sorteoId: number): void {
    this.router.navigate(['/sorteo', sorteoId]);
  }

  onDeleteClick(sorteoId: number): void {
    if (confirm('¿Estás seguro de que quieres eliminar este sorteo?')) {
      this.participantesService.finalizarSorteo(sorteoId).subscribe({
        next: (response) => {
          console.log('Sorteo finalizado:', response.mensaje);
          alert('Sorteo eliminado exitosamente');
          // La lista se actualizará automáticamente gracias al Subject
        },
        error: (error) => {
          console.error('Error al finalizar sorteo:', error);
          let errorMessage = 'Error al eliminar el sorteo. Por favor, inténtalo de nuevo.';
          
          if (error.status === 404) {
            errorMessage = error.error?.detail || 'El sorteo no existe.';
          } else if (error.status === 400) {
            errorMessage = error.error?.detail || 'No se puede eliminar este sorteo.';
          }
          
          alert(errorMessage);
        }
      });
    }
  }

  onCardClick(sorteo: SorteoListResponse): void {
    this.selectedSorteo = sorteo;
    this.isModalVisible = true;
  }

  onCloseModal(): void {
    this.isModalVisible = false;
    this.selectedSorteo = null;
  }

}