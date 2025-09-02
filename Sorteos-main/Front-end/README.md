# Frontend (Angular)

Este repositorio contiene el frontend para un sistema de sorteos, desarrollado con **Angular v16**. El sistema optimiza la ejecución y grabación de sorteos periódicos, permitiendo la precarga de sorteos para reducir el tiempo de preparación en grabaciones o transmisiones en vivo. Está diseñado para entornos tanto virtuales como presenciales, lo que facilita su uso para operadores técnicos y usuarios con mínima experiencia.

Este proyecto fue desarrollado de manera independiente por Christian Hoyos Salazar para la empresa Gane Super Giros.

---

##  Funcionalidades Principales

###  Gestión de Participantes

* **Carga vía archivo:** Sube listas de participantes en formato `.xlsx` o `.xls`.
* **Ingreso manual:** Un área de texto te permite ingresar participantes directamente.

###  Creación y Configuración de Sorteos

* Puedes crear múltiples sorteos con anticipación.
* Configura cada sorteo: la cantidad total de ganadores y cuántos ganadores se muestran en pantalla.

###  Ejecución del Sorteo

* **Iniciar:** Usa las teclas **Enter**, **J**, o **→** (Flecha derecha).
* **Salir:** Usa las teclas **A** o **Esc**.

###  Resultados e Historial

* **Visualización inmediata:** Haz clic en la tarjeta del sorteo para ver la lista de ganadores al instante.
* **Exportación:** Descarga el historial en un archivo Excel (`.xlsx`).

###  Personalización

* Modifica el fondo de la pantalla de juego desde el panel de configuración.

---

##  Requisitos

* **Node.js:** v16.x.x
* **npm:** Viene incluido con Node.js.
* **Angular CLI:** Compatible con Angular 16.

---

##  Instalación

1.  **Instala Node.js (versión 16):** Descárgalo desde [https://nodejs.org](https://nodejs.org).
2.  **Clona o descarga** el proyecto.
3.  **Instala las dependencias** del proyecto:
    ```sh
    npm install
    ```
4.  **Ejecuta en modo de desarrollo:**
    ```sh
    ng serve
    ```
    Por defecto, se ejecutará en [http://localhost:4200/](http://localhost:4200/).

---

##  Conexión con el Backend

Asegúrate de que el frontend esté configurado para consumir la API en el puerto **8001**. Puedes realizar esta configuración en el archivo `environment.ts`.

---

##  Consideraciones Adicionales

* El sistema minimiza errores durante la ejecución gracias a la precarga de sorteos.
* Todas las acciones se realizan sin necesidad de recargar la página.
* Está integrado con un backend desarrollado en **FastAPI** y una base de datos **MySQL**.

