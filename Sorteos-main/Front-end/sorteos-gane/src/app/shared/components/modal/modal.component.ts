import { Component, EventEmitter, Input, Output } from '@angular/core';

type ModalType = 'info' | 'success' | 'warning' | 'error' | 'confirm';

@Component({
  selector: 'app-shared-modal',
  templateUrl: './modal.component.html',
  styleUrls: ['./modal.component.scss']
})
export class ModalComponent {
  @Input() visible: boolean = false;
  @Input() title: string = '';
  @Input() message: string = '';
  @Input() type: ModalType = 'info';
  @Input() confirmText: string = 'Aceptar';
  @Input() cancelText: string = 'Cancelar';
  @Input() showCancel: boolean = false; // solo para confirmaciones

  @Output() confirm = new EventEmitter<void>();
  @Output() cancel = new EventEmitter<void>();
  @Output() closed = new EventEmitter<void>();

  get icon(): string {
    switch (this.type) {
      case 'success': return 'check_circle';
      case 'warning': return 'warning';
      case 'error': return 'error';
      case 'confirm': return 'help';
      default: return 'info';
    }
  }

  get primaryBtnClass(): string {
    switch (this.type) {
      case 'success': return 'btn-success';
      case 'warning': return 'btn-warning';
      case 'error': return 'btn-error';
      default: return 'btn-primary';
    }
  }

  onConfirm() {
    this.confirm.emit();
    this.onClose();
  }

  onCancel() {
    this.cancel.emit();
    this.onClose();
  }

  onBackdropClick(event: Event) {
    if (event.target === event.currentTarget) {
      this.onClose();
    }
  }

  onClose() {
    this.visible = false;
    this.closed.emit();
  }
}


