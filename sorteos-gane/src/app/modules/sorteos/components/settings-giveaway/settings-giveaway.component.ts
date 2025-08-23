import { Component, Input, Output, EventEmitter, OnChanges, ViewEncapsulation } from '@angular/core';
import { SorteosService } from '../../services/sorteos.service';

@Component({
  selector: 'app-settings-giveaway',
  templateUrl: './settings-giveaway.component.html',
  styleUrls: ['./settings-giveaway.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class SettingsGiveawayComponent implements OnChanges {
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

  onSaveSettings(): void {
    console.log('=== MÉTODO onSaveSettings EJECUTADO ===');
    
    if (!this.sorteoId) {
      console.error('No hay sorteoId disponible');
      return;
    }

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