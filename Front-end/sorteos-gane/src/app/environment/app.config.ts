import { environment } from './environment';

export const appConfig = {
  // Configuración de la API
  api: {
    baseUrl: environment.apiUrl,
    version: environment.apiVersion,
    timeout: 30000, // 30 segundos
    retryAttempts: 3,
  },
  
  // Configuración de la aplicación
  app: {
    name: environment.appName,
    version: environment.appVersion,
    defaultLanguage: 'es',
    supportedLanguages: ['es', 'en'],
  },
  
  // Configuración de paginación
  pagination: {
    defaultPageSize: 10,
    pageSizeOptions: [5, 10, 25, 50],
  },
  
  // Configuración de archivos
  fileUpload: {
    maxSize: 5 * 1024 * 1024, // 5MB
    allowedTypes: ['image/jpeg', 'image/png', 'image/gif'],
  },
  
  // Configuración de notificaciones
  notifications: {
    defaultDuration: 5000, // 5 segundos
    position: 'top-right',
  }
};
