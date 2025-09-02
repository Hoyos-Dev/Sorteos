import { Component, Input, Output, EventEmitter, OnChanges, ViewEncapsulation, ViewChild } from '@angular/core';
import { SorteosService } from '../../../../core/services/sorteos.service';
import { ModalComponent } from 'src/app/shared/components/modal/modal.component';

@Component({
  selector: 'app-settings-giveaway',
  templateUrl: './settings-giveaway.component.html',
  styleUrls: ['./settings-giveaway.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class SettingsGiveawayComponent implements OnChanges {
  @ViewChild('winnersModal') winnersModal!: ModalComponent;
  @Input() mostrar: boolean = false;
  @Input() sorteo: any;
  @Output() closeModal = new EventEmitter<void>();
  @Output() sorteoUpdated = new EventEmitter<any>();

  cantidadPremio: number = 1;
  ganadoresSimultaneos: number = 1;
  selectedImage: File | null = null;
  imagePreview: string | null = null;
  isLoading: boolean = false;

  constructor(private sorteosService: SorteosService) {}

  ngOnChanges(): void {
    if (this.sorteo) {
      this.cantidadPremio = this.sorteo.cantidad_premio || 1;
      this.ganadoresSimultaneos = this.sorteo.ganadores_simultaneos || 1;
    }
  }

  get sorteoId(): number | null {
    return this.sorteo?.id || null;
  }

  onImageSelected(event: any): void {
    const file = event.target.files[0];
    if (file && file.type.startsWith('image/')) {
      this.selectedImage = file;
      
      // Crear preview de la imagen
      const reader = new FileReader();
      reader.onload = (e: any) => {
        this.imagePreview = e.target.result;
      };
      reader.readAsDataURL(file);
    }
  }

  async onSaveSettings(): Promise<void> {
    console.log('=== MÉTODO onSaveSettings EJECUTADO ===');
    
    if (!this.sorteoId) {
      console.error('No hay sorteoId disponible');
      return;
    }

    // Verificar si ya hay ganadores
    try {
      const participantes = await this.sorteosService.getParticipantesSorteo(this.sorteoId).toPromise();
      const ganadoresCount = participantes?.filter((p: any) => p.estado === 'ganador').length || 0;
      
      // Si ya hay ganadores y se intenta reducir la cantidad de premios por debajo de los ganadores actuales
      if (ganadoresCount > 0 && this.cantidadPremio < ganadoresCount) {
        this.winnersModal.title = 'Error en configuración';
        this.winnersModal.message = `No se puede reducir la cantidad de premios a ${this.cantidadPremio} porque ya hay ${ganadoresCount} ganadores registrados.`;
        this.winnersModal.type = 'error';
        this.winnersModal.confirmText = 'Entendido';
        this.winnersModal.showCancel = false;
        this.winnersModal.visible = true;
        return;
      }
      
      // Si se intenta configurar ganadores simultáneos mayor a los premios restantes
      const premiosRestantes = this.cantidadPremio - ganadoresCount;
      if (this.ganadoresSimultaneos > premiosRestantes && premiosRestantes > 0) {
        this.winnersModal.title = 'Ajuste necesario';
        this.winnersModal.message = `Solo quedan ${premiosRestantes} premios por sortear. Se ajustará la cantidad de ganadores simultáneos a ${premiosRestantes}.`;
        this.winnersModal.type = 'warning';
        this.winnersModal.confirmText = 'Aceptar';
        this.winnersModal.showCancel = true;
        this.winnersModal.visible = true;
        
        // Configurar el manejador de confirmación para continuar con el ajuste
        this.winnersModal.confirm.subscribe(() => {
          this.ganadoresSimultaneos = premiosRestantes;
          this.continueSaving();
          this.winnersModal.visible = false;
        });
        
        this.winnersModal.cancel.subscribe(() => {
          this.winnersModal.visible = false;
        });
        
        return;
      }
    } catch (error) {
      console.error('Error al verificar ganadores:', error);
    }
    
    // Si todo está bien, continuar con el guardado
    this.continueSaving();
  }
  
  private continueSaving(): void {
    if (!this.sorteoId) return;
    
    console.log('Iniciando guardado de configuración:', {
      sorteoId: this.sorteoId,
      cantidadPremio: this.cantidadPremio,
      sorteo: this.sorteo
    });

    this.isLoading = true;
    
    // Actualizar cantidad de premio y ganadores simultáneos
    this.sorteosService.updateSorteo(this.sorteoId, {
      cantidad_premio: this.cantidadPremio,
      ganadores_simultaneos: this.ganadoresSimultaneos
    }).subscribe({
      next: (response) => {
        console.log('Sorteo actualizado:', response);
        
        // Si hay imagen seleccionada, subirla
        if (this.selectedImage) {
          this.sorteosService.uploadSorteoImage(this.sorteoId!, this.selectedImage).subscribe({
            next: (imageResponse) => {
              console.log('Imagen subida:', imageResponse);
              this.finalizarActualizacion();
            },
            error: (error) => {
              console.error('Error al subir imagen:', error);
              this.finalizarActualizacion();
            }
          });
        } else {
          this.finalizarActualizacion();
        }
      },
      error: (error) => {
        console.error('Error al actualizar sorteo:', error);
        this.isLoading = false;
      }
    });
  }

  // Manejadores para el modal
  onModalConfirm(): void {
    // Se ejecuta cuando el usuario confirma en el modal
    this.winnersModal.visible = false;
  }

  onModalCancel(): void {
    // Se ejecuta cuando el usuario cancela en el modal
    this.winnersModal.visible = false;
  }

  onModalClose(): void {
    // Se ejecuta cuando se cierra el modal
    this.winnersModal.visible = false;
  }

  private finalizarActualizacion(): void {
    // Emitir evento de actualización
    this.sorteoUpdated.emit({
      ...this.sorteo,
      cantidad_premio: this.cantidadPremio,
      cantidadPremio: this.cantidadPremio,  // Para compatibilidad con el frontend
      ganadores_simultaneos: this.ganadoresSimultaneos
    });

    this.isLoading = false;
    this.onClose();
  }

  onClose(): void {
    this.closeModal.emit();
  }

  onBackdropClick(event: Event): void {
    if (event.target === event.currentTarget) {
      this.onClose();
    }
  }
}