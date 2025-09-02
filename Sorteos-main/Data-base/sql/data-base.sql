-- junio5.participantes
 
CREATE TABLE `participantes` (
  `documento` varchar(50) NOT NULL,
  `nombre` varchar(255) NOT NULL,
  `fecha_registro` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`documento`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
 
-- junio5.sorteo 
 
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
 
-- junio5.detalle_sorteo 
 
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
 