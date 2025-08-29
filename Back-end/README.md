# Backend (FastAPI)

Este repositorio contiene el backend del sistema de sorteos, desarrollado con **FastAPI (Python)**. El sistema optimiza la ejecución y grabación de sorteos periódicos, permitiendo la precarga de sorteos para reducir el tiempo de preparación en grabaciones o transmisiones en vivo. Está diseñado para entornos tanto virtuales como presenciales, lo que facilita su uso para operadores técnicos y usuarios con mínima experiencia.

Este proyecto fue desarrollado de manera independiente por Christian Hoyos Salazar para la empresa Gane Super Giros.

---

## Funcionalidades Principales

El backend gestiona toda la **lógica de negocio**, incluyendo:

* **Gestión** de participantes y sorteos.
* **Ejecución** de sorteos y almacenamiento de resultados.
* **Integración** con una base de datos **MySQL** para la persistencia de datos.

---

## Requisitos

* **Python:** 3.8 o superior
* **FastAPI**
* **MySQL Server:** Debe estar instalado y en ejecución (por ejemplo, a través de XAMPP).

---

## Instalación

1.  **Instala FastAPI y Uvicorn:** Se recomienda hacerlo en un entorno virtual.
    ```sh
    pip install fastapi uvicorn
    ```
2.  **Instala el conector de MySQL:**
    ```sh
    pip install mysql-connector-python
    ```
3.  **Asegúrate de que el servidor MySQL esté corriendo** (p.ej., a través de XAMPP).
4.  **Ejecuta el backend:** Desde el directorio que contiene `main.py`, ejecuta el siguiente comando:
    ```sh
    python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001
    ```
    La API estará disponible en [http://localhost:8001/](http://localhost:8001/).

---

## Conexión con Frontend y Base de Datos

* El frontend consume esta API en el **puerto 8001**.
* La conectividad a la base de datos **MySQL** se gestiona a través de consultas SQL directas o un ORM (Object-Relational Mapper).

---

## Consideraciones Adicionales

* Es una **API RESTful de alto rendimiento** con validaciones automáticas.
* Está integrado con un frontend desarrollado en **Angular** y una base de datos **MySQL**.
* Diseñado para un **uso continuo** en sesiones de grabación o transmisión.




# Sistema de Gestión de Sorteos

Este documento describe la estructura de la base de datos utilizada para gestionar sorteos y participantes. El sistema se basa en un esquema de **MySQL** compuesto por tres tablas principales diseñadas para manejar la relación entre sorteos, participantes y sus resultados.

---

### Estructura de la Base de Datos

El sistema está organizado en un modelo de datos relacional para garantizar la integridad y la coherencia. A continuación, se detallan las tablas y sus campos.

#### **`participantes`**
Esta tabla almacena la información básica de cada persona que participa en los sorteos. El campo `documento` actúa como identificador único.

```sql
CREATE TABLE `participantes` (
  `documento` varchar(50) NOT NULL,
  `nombre` varchar(255) NOT NULL,
  `fecha_registro` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`documento`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
```

---

#### **`sorteo`**
Esta tabla centraliza la información de cada sorteo, incluyendo su configuración y estado. El campo `id` es el identificador principal.

```sql
CREATE TABLE `sorteo` (
  `id` int(11) NOT NULL,
  `nombre` varchar(255) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `estado` enum('activo','finalizado') DEFAULT 'activo',
  `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp(),
  `fecha_finalizacion` timestamp NULL DEFAULT NULL,
  `cantidad_premio` int(11) DEFAULT 1,
  `imagen` varchar(500) DEFAULT NULL,
  `ganadores_simultaneos` int(11) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
```

---

#### **`detalle_sorteo`**
Esta tabla de unión, o tabla intermedia, vincula a los participantes con los sorteos. Aquí se registra la participación de cada individuo y su resultado final en un sorteo específico.

```sql
CREATE TABLE `detalle_sorteo` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_sorteo` int(11) NOT NULL,
  `documento_participante` varchar(50) NOT NULL,
  `estado` enum('participando','ganador','perdedor','eliminado','descalificado') DEFAULT 'participando',
  `fecha_asignacion` timestamp NOT NULL DEFAULT current_timestamp(),
  `fecha_ganador` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_sorteo_participante` (`id_sorteo`,`documento_participante`),
  UNIQUE KEY `uq_sorteo_participante` (`id_sorteo`,`documento_participante`),
  KEY `fk_detalle_sorteo_participante` (`documento_participante`),
  CONSTRAINT `fk_detalle_sorteo_participante` FOREIGN KEY (`documento_participante`) REFERENCES `participantes` (`documento`) ON DELETE CASCADE,
  CONSTRAINT `fk_detalle_sorteo_sorteo` FOREIGN KEY (`id_sorteo`) REFERENCES `sorteo` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3528 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
```

> Se han implementado **claves foráneas** para mantener la integridad referencial entre las tablas `participantes`, `sorteo`, y `detalle_sorteo`. Además, se utiliza una restricción `UNIQUE` en la combinación de `id_sorteo` y `documento_participante` para asegurar que un participante no pueda ser registrado más de una vez en el mismo sorteo.
