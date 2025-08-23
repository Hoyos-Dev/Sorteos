import { Component, OnInit, OnDestroy, HostListener } from '@angular/core';
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
  isConfigModalVisible: boolean = false;
  selectedSorteo: SorteoListResponse | null = null;
  selectedSorteoForConfig: SorteoListResponse | null = null;
  openDropdownId: number | null = null;
  ganadoresPorSorteo: { [sorteoId: number]: number } = {}; // Almacena cantidad de ganadores por sorteo

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
    
    // Suscribirse al evento de ganador marcado para actualizar los colores
    this.subscription.add(
      this.participantesService.ganadorMarcado$.subscribe(() => {
        this.cargarGanadoresPorSorteo();
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
        // Cargar información de ganadores para cada sorteo
        this.cargarGanadoresPorSorteo();
      },
      error: (error) => {
        console.error('Error al cargar sorteos:', error);
      }
    });
  }

  cargarGanadoresPorSorteo(): void {
    this.sorteos.forEach(sorteo => {
      this.participantesService.obtenerGanadoresPorSorteo(sorteo.id).subscribe({
        next: (ganadores) => {
          this.ganadoresPorSorteo[sorteo.id] = ganadores.length;
        },
        error: (error) => {
          console.error(`Error al cargar ganadores del sorteo ${sorteo.id}:`, error);
          this.ganadoresPorSorteo[sorteo.id] = 0;
        }
      });
    });
  }

  onPlayClick(sorteoId: number): void {
    this.router.navigate(['/sorteo', sorteoId]);
  }

  toggleDropdown(sorteoId: number): void {
    this.openDropdownId = this.openDropdownId === sorteoId ? null : sorteoId;
  }

  isDropdownOpen(sorteoId: number): boolean {
    return this.openDropdownId === sorteoId;
  }

  onConfigClick(sorteoId: number): void {
    // Cerrar el dropdown primero
    this.openDropdownId = null;
    // Encontrar el sorteo seleccionado
    this.selectedSorteoForConfig = this.sorteos.find(s => s.id === sorteoId) || null;
    // Mostrar el modal de configuraciones
    this.isConfigModalVisible = true;
  }

  onDeleteClick(sorteoId: number): void {
    // Cerrar el dropdown primero
    this.openDropdownId = null;
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

  onCloseConfigModal(): void {
    this.isConfigModalVisible = false;
    this.selectedSorteoForConfig = null;
  }

  onSorteoUpdated(sorteoActualizado: any): void {
    // Actualizar el sorteo en la lista local
    const index = this.sorteos.findIndex(s => s.id === sorteoActualizado.id);
    if (index !== -1) {
      this.sorteos[index] = { ...this.sorteos[index], ...sorteoActualizado };
    }
    
    // Si el sorteo actualizado es el que se está mostrando en el modal, actualizarlo también
    if (this.selectedSorteo && this.selectedSorteo.id === sorteoActualizado.id) {
      this.selectedSorteo = { ...this.selectedSorteo, ...sorteoActualizado };
    }
    
    // Recargar ganadores para actualizar los colores de estado
    this.cargarGanadoresPorSorteo();
    
    // También recargar la lista completa para asegurar consistencia
    this.cargarSorteos();
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: Event): void {
    const target = event.target as HTMLElement;
    if (!target.closest('.dropdown-container')) {
      this.openDropdownId = null;
    }
  }

  // Método para determinar el color del borde izquierdo según el estado del sorteo
  getStatusBorderColor(sorteo: SorteoListResponse): string {
    // Sorteo finalizado → Rojo
    if (sorteo.estado === 'finalizado') {
      return '#d32f2f';
    }
    
    // Sorteo sin configurar (cantidad_premio = 0 o null) → Azul
    if (!sorteo.cantidad_premio || sorteo.cantidad_premio === 0) {
      return '#003594';
    }
    
    const cantidadGanadores = this.ganadoresPorSorteo[sorteo.id] || 0;
    
    // Sorteo completo (ganadores >= premios) → Rojo
    if (cantidadGanadores >= sorteo.cantidad_premio) {
      return '#d32f2f';
    }
    
    // Sorteo sin ganadores (0/N) → Azul (no iniciado)
    if (cantidadGanadores === 0) {
      return '#003594';
    }
    
    // Sorteo con ganadores pero no completo (X/N donde X > 0 y X < N) → Verde
    return '#4caf50';
  }

}