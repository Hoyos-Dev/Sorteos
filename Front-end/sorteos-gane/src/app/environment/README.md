# Configuración de Environment

Esta carpeta contiene toda la configuración centralizada de la aplicación Sorteos Gane.

## Archivos

### `environment.ts`
Configuración para desarrollo local:
- `apiUrl`: `http://localhost:8001`
- `production`: `false`

### `environment.prod.ts`
Configuración para producción:
- `apiUrl`: URL de tu API en producción
- `production`: `true`

### `app.config.ts`
Configuración adicional de la aplicación:
- Configuración de API (timeout, reintentos)
- Configuración de la app (idioma, paginación)
- Configuración de archivos (tamaño máximo, tipos permitidos)
- Configuración de notificaciones

### `index.ts`
Archivo de exportación centralizada.

## Uso

### En servicios:
```typescript
import { environment } from '../../environment';

export class MiServicio {
  private apiUrl = environment.apiUrl;
  
  constructor() {
    // Usar this.apiUrl para las llamadas a la API
  }
}
```

### En componentes:
```typescript
import { appConfig } from '../../environment';

export class MiComponente {
  maxFileSize = appConfig.fileUpload.maxSize;
  pageSize = appConfig.pagination.defaultPageSize;
}
```

## Cambios de Environment

### Desarrollo:
- Usa `environment.ts` por defecto
- `ng serve` usa la configuración de desarrollo

### Producción:
- `ng build --prod` automáticamente reemplaza `environment.ts` con `environment.prod.ts`
- Configurado en `angular.json` con `fileReplacements`

## Personalización

Para cambiar la URL de producción:
1. Edita `environment.prod.ts`
2. Cambia `apiUrl` a tu URL de producción
3. Haz build con `ng build --prod`

## Notas Importantes

- **NUNCA** hardcodear URLs en los servicios
- **SIEMPRE** usar `environment.apiUrl`
- Para desarrollo local: `http://localhost:8001`
- Para producción: Cambiar en `environment.prod.ts`
