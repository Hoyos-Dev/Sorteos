import { Component, OnInit, Output, EventEmitter, Input } from '@angular/core';
import * as XLSX from 'xlsx';

@Component({
  selector: 'app-upload-file',
  templateUrl: './upload-file.component.html',
  styleUrls: ['./upload-file.component.scss']
})
export class UploadFileComponent implements OnInit {
  @Input() isVisible: boolean = false;
  @Output() closeModal = new EventEmitter<void>();
  @Output() fileUploaded = new EventEmitter<File>();
  @Output() participantsExtracted = new EventEmitter<string[]>();

  selectedFile: File | null = null;
  isDragOver: boolean = false;
  uploadProgress: number = 0;
  isUploading: boolean = false;

  constructor() { }

  ngOnInit(): void {
  }

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      this.selectedFile = file;
    }
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    this.isDragOver = true;
  }

  onDragLeave(event: DragEvent): void {
    event.preventDefault();
    this.isDragOver = false;
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    this.isDragOver = false;
    
    const files = event.dataTransfer?.files;
    if (files && files.length > 0) {
      this.selectedFile = files[0];
    }
  }

  uploadFile(): void {
    if (!this.selectedFile) return;

    this.isUploading = true;
    this.uploadProgress = 0;

    // Leer el archivo Excel
    const reader = new FileReader();
    reader.onload = (e: any) => {
      try {
        const data = new Uint8Array(e.target.result);
        const workbook = XLSX.read(data, { type: 'array' });
        const firstSheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[firstSheetName];
        const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
        
        const participants = this.extractParticipants(jsonData);
        
        // Simular progreso de subida
        const interval = setInterval(() => {
          this.uploadProgress += 10;
          if (this.uploadProgress >= 100) {
            clearInterval(interval);
            this.isUploading = false;
            this.participantsExtracted.emit(participants);
            this.fileUploaded.emit(this.selectedFile!);
            this.resetModal();
          }
        }, 200);
      } catch (error) {
        console.error('Error al leer el archivo Excel:', error);
        this.isUploading = false;
        alert('Error al procesar el archivo Excel. Verifique que el formato sea correcto.');
      }
    };
    reader.readAsArrayBuffer(this.selectedFile);
  }

  removeFile(): void {
    this.selectedFile = null;
  }

  closeModalHandler(): void {
    this.resetModal();
    this.closeModal.emit();
  }

  onCloseModal(): void {
    this.closeModal.emit();
  }

  private resetModal(): void {
    this.selectedFile = null;
    this.uploadProgress = 0;
    this.isUploading = false;
    this.isDragOver = false;
  }

  onBackdropClick(event: Event): void {
    if (event.target === event.currentTarget) {
      this.closeModalHandler();
    }
  }

  triggerFileInput() {
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    if (fileInput) {
      fileInput.click();
    }
  }

  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  private extractParticipants(data: any[]): string[] {
    if (data.length === 0) return [];
    
    // Buscar las columnas DOCUMENTO y NOMBRE en la primera fila (headers)
    const headers = data[0] as string[];
    const documentoIndex = headers.findIndex(header => 
      header && header.toString().toUpperCase().includes('DOCUMENTO')
    );
    const nombreIndex = headers.findIndex(header => 
      header && header.toString().toUpperCase().includes('NOMBRE')
    );
    
    if (documentoIndex === -1 || nombreIndex === -1) {
      alert('El archivo debe contener las columnas DOCUMENTO y NOMBRE');
      return [];
    }
    
    const participants: string[] = [];
    
    // Procesar las filas de datos (saltando la primera fila que son los headers)
    for (let i = 1; i < data.length; i++) {
      const row = data[i] as any[];
      const documento = row[documentoIndex];
      const nombre = row[nombreIndex];
      
      if (documento && nombre) {
        const participantText = `${documento} - ${nombre}`;
        participants.push(participantText);
      }
    }
    
    return participants;
  }
}