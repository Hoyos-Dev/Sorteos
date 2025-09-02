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

