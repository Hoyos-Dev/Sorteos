import { Component, OnInit, HostListener } from '@angular/core';
import { Location } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { ParticipantesService, SorteoListResponse } from '../../services/participantes.service';

interface Participante {
  documento: string;
  nombre: string;
}

@Component({
  selector: 'app-play-giveaways',
  templateUrl: './play-giveaways.component.html',
  styleUrls: ['./play-giveaways.component.scss']
})
export class PlayGiveawaysComponent implements OnInit {
  participanteActual: Participante | null = null;
  juegoIniciado: boolean = false;
  nombreAnimado: string = '';
  nombreAnimadoHTML: string = '';
  animacionEnCurso: boolean = false;
  private abecedario: string[] = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');
  sorteoId: string | null = null;
  sorteoInfo: SorteoListResponse | null = null;
  ganadoresActuales: number = 0;
  sorteoImagen: string | null = null;
  
  // Nuevas propiedades para múltiples ganadores
  ganadoresSimultaneos: (Participante | null)[] = [];
  nombresAnimados: string[] = [];
  nombresAnimadosHTML: string[] = [];
  cuadrosGanadores: number = 1;

  constructor(
    private location: Location,
    private route: ActivatedRoute,
    private participantesService: ParticipantesService,
    private http: HttpClient
  ) { }

  ngOnInit(): void {
    // Obtener el ID del sorteo desde la ruta
    this.sorteoId = this.route.snapshot.paramMap.get('id');
    
    if (this.sorteoId) {
      this.cargarSorteoInfo();
    }
    
    if (!this.sorteoId) {
      console.error('No se encontró el ID del sorteo en los parámetros de ruta');
    }
  }

  private cargarSorteoInfo(): void {
    if (this.sorteoId) {
      // Obtener todos los sorteos y filtrar por ID
      this.participantesService.obtenerTodosLosSorteos().subscribe({
        next: (sorteos) => {
          this.sorteoInfo = sorteos.find(s => s.id.toString() === this.sorteoId) || null;
          
          if (this.sorteoInfo) {
            // Configurar número de cuadros según ganadores_simultaneos
            this.cuadrosGanadores = this.sorteoInfo.ganadores_simultaneos || 1;
            
            // Inicializar arrays para múltiples ganadores
            this.ganadoresSimultaneos = new Array(this.cuadrosGanadores).fill(null);
            this.nombresAnimados = new Array(this.cuadrosGanadores).fill('');
            this.nombresAnimadosHTML = new Array(this.cuadrosGanadores).fill('');
            
            this.cargarGanadoresActuales();
            this.cargarImagenSorteo();
          } else {
            console.error('No se encontró el sorteo con ID:', this.sorteoId);
          }
        },
        error: (error) => {
          console.error('Error cargando información del sorteo:', error);
        }
      });
    }
  }

  private cargarGanadoresActuales(): void {
    if (this.sorteoId) {
      console.log('Cargando ganadores para sorteo:', this.sorteoId);
      this.participantesService.obtenerGanadoresPorSorteo(Number(this.sorteoId)).subscribe({
        next: (ganadores) => {
          this.ganadoresActuales = ganadores.length;
          console.log('Ganadores actuales cargados:', this.ganadoresActuales, 'Lista:', ganadores);
          console.log('Cantidad de premios del sorteo:', this.sorteoInfo?.cantidad_premio);
        },
        error: (error) => {
          console.error('Error cargando ganadores:', error);
          this.ganadoresActuales = 0;
        }
      });
    }
  }

  @HostListener('document:keydown', ['$event'])
  handleKeyboardEvent(event: KeyboardEvent) {
    if (event.key === 'a' || event.key === 'A') {
      this.location.back();
    } else if (event.key === 'j' || event.key === 'J') {
      // Verificar si el sorteo está finalizado antes de permitir iniciar el juego
      if (this.sorteoInfo && this.sorteoInfo.estado === 'finalizado') {
        console.log('El sorteo está finalizado, no se puede iniciar el juego');
        return;
      }
      
      this.iniciarJuego();
    }
  }

  iniciarJuego() {
    console.log('Tecla J presionada - Iniciando juego');
    console.log('Estado actual - Ganadores:', this.ganadoresActuales, 'Cantidad premio:', this.sorteoInfo?.cantidad_premio);
    
    if (this.animacionEnCurso) {
      console.log('Animación en curso, ignorando tecla J');
      return;
    }
    
    if (!this.sorteoId) {
      console.error('No se encontró el ID del sorteo');
      return;
    }

    // Recargar información del sorteo antes de verificar su estado
    this.participantesService.obtenerTodosLosSorteos().subscribe({
      next: (sorteos) => {
        const sorteoActualizado = sorteos.find(s => s.id.toString() === this.sorteoId);
        if (sorteoActualizado) {
          this.sorteoInfo = sorteoActualizado;
          console.log('Información del sorteo recargada. Estado:', this.sorteoInfo.estado);
          
          // Verificar si el sorteo ya está finalizado
          if (this.sorteoInfo.estado === 'finalizado') {
            alert('Este sorteo ya ha sido finalizado.');
            // Limpiar la pantalla del juego
            this.participanteActual = null;
            this.nombreAnimado = '';
            this.nombreAnimadoHTML = '';
            this.juegoIniciado = false;
            return;
          }
          
          // Continuar con el resto de la lógica del juego
          this.continuarInicioJuego();
        }
      },
      error: (error) => {
        console.error('Error recargando información del sorteo:', error);
        // Continuar con la información actual si hay error
        this.continuarInicioJuego();
      }
    });
  }

  private continuarInicioJuego(): void {
    // Verificar si el sorteo ya está finalizado
    if (this.sorteoInfo && this.sorteoInfo.estado === 'finalizado') {
      alert('Este sorteo ya ha sido finalizado.');
      // Limpiar la pantalla del juego
      this.participanteActual = null;
      this.nombreAnimado = '';
      this.nombreAnimadoHTML = '';
      this.juegoIniciado = false;
      return;
    }
    
    console.log('Iniciando juego para sorteo:', this.sorteoId);
    console.log('URL del endpoint:', `http://localhost:8001/obtener-participante-aleatorio/${this.sorteoId}`);

    // Obtener múltiples participantes según la configuración
    this.obtenerMultiplesParticipantes();
  }

  private obtenerMultiplesParticipantes(): void {
    const participantesObtenidos: Participante[] = [];
    let participantesRestantes = this.cuadrosGanadores;
    
    const obtenerSiguienteParticipante = () => {
      if (participantesRestantes <= 0) {
        // Todos los participantes obtenidos, iniciar animaciones
        this.procesarGanadoresSimultaneos(participantesObtenidos);
        return;
      }
      
      this.http.get<any>(`http://localhost:8001/obtener-participante-aleatorio/${this.sorteoId}`).subscribe({
        next: (response) => {
          console.log('Respuesta del servidor:', response);
          if (response.ok && response.participante) {
            console.log('Participante obtenido:', response.participante);
            participantesObtenidos.push(response.participante);
            participantesRestantes--;
            // Obtener siguiente participante
            setTimeout(() => obtenerSiguienteParticipante(), 100);
          } else {
            // No hay más participantes disponibles
            console.log('No hay más participantes disponibles para el sorteo');
            this.procesarGanadoresSimultaneos(participantesObtenidos);
          }
        },
        error: (error) => {
          console.error('Error al obtener participante:', error);
          participantesRestantes--;
          // Continuar con el siguiente aunque haya error
          setTimeout(() => obtenerSiguienteParticipante(), 100);
        }
      });
    };
    
    obtenerSiguienteParticipante();
  }

  private procesarGanadoresSimultaneos(participantes: Participante[]): void {
    if (participantes.length === 0) {
      // No hay participantes, limpiar pantalla
      this.limpiarPantalla();
      return;
    }
    
    // Asignar participantes a los cuadros
    for (let i = 0; i < this.cuadrosGanadores; i++) {
      if (i < participantes.length) {
        this.ganadoresSimultaneos[i] = participantes[i];
        this.nombresAnimados[i] = '';
        this.nombresAnimadosHTML[i] = '';
      } else {
        this.ganadoresSimultaneos[i] = null;
        this.nombresAnimados[i] = '';
        this.nombresAnimadosHTML[i] = '';
      }
    }
    
    // Para sorteos individuales, también actualizar las variables del sorteo único
    if (this.cuadrosGanadores === 1 && participantes.length > 0) {
      this.participanteActual = participantes[0];
      this.nombreAnimado = '';
      this.nombreAnimadoHTML = '';
    }
    
    this.juegoIniciado = true;
    
    // Iniciar animaciones para todos los participantes
    participantes.forEach((participante, index) => {
      if (participante) {
        console.log(`Iniciando animación para cuadro ${index + 1}:`, participante.nombre);
        if (this.cuadrosGanadores === 1) {
          // Para sorteos individuales, usar la animación original
          this.animarNombre(participante.nombre.toUpperCase());
        } else {
          // Para sorteos múltiples, usar la animación por cuadro
          this.animarNombreEnCuadro(participante.nombre.toUpperCase(), index);
        }
      }
    });
    
    // Marcar todos como ganadores
    if (this.cuadrosGanadores === 1 && participantes.length > 0) {
      // Para sorteos individuales, usar el método original
      this.marcarGanador();
    } else {
      // Para sorteos múltiples, usar el método múltiple
      this.marcarMultiplesGanadores(participantes);
    }
  }

  private limpiarPantalla(): void {
    this.participanteActual = null;
    this.nombreAnimado = '';
    this.nombreAnimadoHTML = '';
    this.ganadoresSimultaneos = new Array(this.cuadrosGanadores).fill(null);
    this.nombresAnimados = new Array(this.cuadrosGanadores).fill('');
    this.nombresAnimadosHTML = new Array(this.cuadrosGanadores).fill('');
    this.juegoIniciado = false;
    console.log('No hay más participantes disponibles para el sorteo');
  }

  animarNombre(nombreCompleto: string): void {
    this.animacionEnCurso = true;
    // Inicializar con letras aleatorias diferentes para cada posición
    this.nombreAnimado = '';
    const posicionesIniciales: number[] = [];
    for (let i = 0; i < nombreCompleto.length; i++) {
      if (nombreCompleto[i] === ' ') {
        this.nombreAnimado += ' ';
        posicionesIniciales.push(-1); // -1 para espacios
      } else {
        const posicionAleatoria = Math.floor(Math.random() * this.abecedario.length);
        this.nombreAnimado += this.abecedario[posicionAleatoria];
        posicionesIniciales.push(posicionAleatoria);
      }
    }
    
    let cicloActual = 0;
    const ciclosPorLetra = 5; // Ciclos antes de que cada letra se detenga (más rápido)
    let letrasFijas: boolean[] = new Array(nombreCompleto.length).fill(false);
    
    const animarTodasLasLetras = () => {
      if (cicloActual < nombreCompleto.length * ciclosPorLetra) {
        let nombreTemporal = '';
        
        for (let i = 0; i < nombreCompleto.length; i++) {
          if (nombreCompleto[i] === ' ') {
            nombreTemporal += ' ';
          } else {
            // Calcular si esta letra ya debe estar fija
            const cicloParaDetener = i * ciclosPorLetra;
            if (cicloActual >= cicloParaDetener) {
              nombreTemporal += nombreCompleto[i];
              letrasFijas[i] = true;
            } else {
              // Generar letra aleatoria
              const nuevaPosicion = Math.floor(Math.random() * this.abecedario.length);
              nombreTemporal += this.abecedario[nuevaPosicion];
            }
          }
        }
        
        this.nombreAnimado = nombreTemporal;
        this.actualizarHTML();
        cicloActual++;
        
        setTimeout(animarTodasLasLetras, 100); // Velocidad de animación
      } else {
        // Animación completada
        this.nombreAnimado = nombreCompleto;
        this.actualizarHTML();
        this.animacionEnCurso = false;
      }
    };
    
    animarTodasLasLetras();
  }

  actualizarHTML(): void {
    let html = '';
    for (let i = 0; i < this.nombreAnimado.length; i++) {
      if (this.nombreAnimado[i] === ' ') {
        html += '<span class="letra">&nbsp;</span>';
      } else {
        html += `<span class="letra">${this.nombreAnimado[i]}</span>`;
      }
    }
    this.nombreAnimadoHTML = html;
  }

  private marcarGanador(): void {
    if (this.participanteActual && this.sorteoId) {
      console.log('Marcando ganador:', this.participanteActual.documento);
      this.participantesService.marcarGanador(Number(this.sorteoId), this.participanteActual.documento).subscribe({
        next: (response) => {
          console.log('Participante marcado como ganador:', response);
          
          // Recargar el conteo real de ganadores desde el servidor
          this.cargarGanadoresActuales();
          
          // Validar que la fecha_ganador se actualizó correctamente
          this.validarFechaGanador();
        },
        error: (error) => {
          console.error('Error marcando participante como ganador:', error);
        }
      });
    }
  }

  private marcarMultiplesGanadores(participantes: Participante[]): void {
    if (!this.sorteoId) return;
    
    participantes.forEach(participante => {
      if (participante) {
        console.log('Marcando ganador:', participante.documento);
        this.participantesService.marcarGanador(Number(this.sorteoId), participante.documento).subscribe({
          next: (response) => {
            console.log('Participante marcado como ganador:', response);
          },
          error: (error) => {
            console.error('Error marcando participante como ganador:', error);
          }
        });
      }
    });
    
    // Recargar el conteo real de ganadores desde el servidor
    setTimeout(() => {
      this.cargarGanadoresActuales();
    }, 1000);
  }

  animarNombreEnCuadro(nombreCompleto: string, cuadroIndex: number): void {
    // Inicializar con letras aleatorias diferentes para cada posición
    this.nombresAnimados[cuadroIndex] = '';
    const posicionesIniciales: number[] = [];
    for (let i = 0; i < nombreCompleto.length; i++) {
      if (nombreCompleto[i] === ' ') {
        this.nombresAnimados[cuadroIndex] += ' ';
        posicionesIniciales.push(-1); // -1 para espacios
      } else {
        const posicionAleatoria = Math.floor(Math.random() * this.abecedario.length);
        this.nombresAnimados[cuadroIndex] += this.abecedario[posicionAleatoria];
        posicionesIniciales.push(posicionAleatoria);
      }
    }
    
    let cicloActual = 0;
    const ciclosPorLetra = 5; // Ciclos antes de que cada letra se detenga
    let letrasFijas: boolean[] = new Array(nombreCompleto.length).fill(false);
    
    const animarTodasLasLetras = () => {
      if (cicloActual < nombreCompleto.length * ciclosPorLetra) {
        let nombreTemporal = '';
        
        for (let i = 0; i < nombreCompleto.length; i++) {
          if (nombreCompleto[i] === ' ') {
            nombreTemporal += ' ';
          } else {
            // Calcular si esta letra ya debe estar fija
            const cicloParaDetener = i * ciclosPorLetra;
            if (cicloActual >= cicloParaDetener) {
              nombreTemporal += nombreCompleto[i];
              letrasFijas[i] = true;
            } else {
              // Generar letra aleatoria
              const nuevaPosicion = Math.floor(Math.random() * this.abecedario.length);
              nombreTemporal += this.abecedario[nuevaPosicion];
            }
          }
        }
        
        this.nombresAnimados[cuadroIndex] = nombreTemporal;
        this.actualizarHTMLCuadro(cuadroIndex);
        cicloActual++;
        
        setTimeout(animarTodasLasLetras, 100); // Velocidad de animación
      } else {
        // Animación completada
        this.nombresAnimados[cuadroIndex] = nombreCompleto;
        this.actualizarHTMLCuadro(cuadroIndex);
      }
    };
    
    animarTodasLasLetras();
  }

  actualizarHTMLCuadro(cuadroIndex: number): void {
    let html = '';
    const nombreAnimado = this.nombresAnimados[cuadroIndex];
    for (let i = 0; i < nombreAnimado.length; i++) {
      if (nombreAnimado[i] === ' ') {
        html += '<span class="letra">&nbsp;</span>';
      } else {
        html += `<span class="letra">${nombreAnimado[i]}</span>`;
      }
    }
    this.nombresAnimadosHTML[cuadroIndex] = html;
  }

  private validarFechaGanador(): void {
    if (this.participanteActual && this.sorteoId) {
      // Esperar un momento para que se complete la actualización
      setTimeout(() => {
        this.participantesService.obtenerGanadoresPorSorteo(Number(this.sorteoId)).subscribe({
          next: (ganadores) => {
            const ganadorActual = ganadores.find(g => g.documento_participante === this.participanteActual?.documento);
            
            if (ganadorActual) {
              if (ganadorActual.fecha_ganador) {
                console.log('✅ Validación exitosa - Fecha ganador actualizada:', ganadorActual.fecha_ganador);
              } else {
                console.error('❌ ERROR: fecha_ganador es NULL para el ganador:', ganadorActual.documento_participante);
                // Mostrar alerta al usuario
                alert('Error: La fecha del ganador no se actualizó correctamente. Por favor, contacte al administrador.');
              }
            } else {
              console.error('❌ ERROR: No se encontró el ganador en la lista de ganadores');
            }
          },
          error: (error) => {
            console.error('Error validando fecha_ganador:', error);
          }
        });
      }, 1000); // Esperar 1 segundo
    }
  }

  private cargarImagenSorteo(): void {
    if (this.sorteoId) {
      this.http.get<any>(`http://localhost:8001/sorteos/${this.sorteoId}/imagen`).subscribe({
        next: (response) => {
          if (response && response.imagen) {
            this.sorteoImagen = `data:image/jpeg;base64,${response.imagen}`;
            console.log('Imagen del sorteo cargada exitosamente');
          }
        },
        error: (error) => {
          console.log('No se encontró imagen para el sorteo o error al cargar:', error);
          this.sorteoImagen = null;
        }
      });
    }
  }
}