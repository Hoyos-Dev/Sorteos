# Base de Datos - Sistema de Sorteos

Este directorio contiene los scripts SQL necesarios para crear y configurar la base de datos MySQL del sistema de sorteos.

## Contenido de las tablas principales

- **participantes**: Datos de los participantes.
- **sorteo**: Información de los sorteos.
- **detalle_sorteo**: Relación entre participantes y sorteos, con estados.

## Scripts para crear tablas

```sql
CREATE TABLE `participantes` (
  `documento` varchar(50) NOT NULL,
  `nombre` varchar(255) NOT NULL,
  `fecha_registro` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`documento`)
);

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
);

CREATE TABLE `detalle_sorteo` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_sorteo` int(11) NOT NULL,
  `documento_participante` varchar(50) NOT NULL,
  `estado` enum('participando','ganador','perdedor','eliminado','descalificado') DEFAULT 'participando',
  `fecha_asignacion` timestamp NOT NULL DEFAULT current_timestamp(),
  `fecha_ganador` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_sorteo_participante` (`id_sorteo`,`documento_participante`),
  FOREIGN KEY (`documento_participante`) REFERENCES `participantes` (`documento`) ON DELETE CASCADE,
  FOREIGN KEY (`id_sorteo`) REFERENCES `sorteo` (`id`) ON DELETE CASCADE
);
