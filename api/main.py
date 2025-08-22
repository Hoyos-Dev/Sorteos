from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import uvicorn

from controllers.participante_controller import router as participante_router
from controllers.sorteo_controller import router as sorteo_router
from config.database import DatabaseConnection

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear la aplicación FastAPI
app = FastAPI(
    title="API Sorteos",
    description="API para gestión de participantes en sorteos",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://localhost:4201"],  # URLs del frontend Angular
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(participante_router)
app.include_router(sorteo_router)

@app.get("/")
async def root():
    """Endpoint raíz de la API"""
    return {"mensaje": "API de Sorteos funcionando correctamente"}


@app.get("/health")
async def health_check():
    """Endpoint para verificar el estado de la API y la base de datos"""
    try:
        # Probar conexión a la base de datos
        db_status = DatabaseConnection.test_connection()
        
        if db_status:
            return {
                "status": "healthy",
                "database": "connected",
                "timestamp": "2024-01-01T00:00:00"
            }
        else:
            return {
                "status": "unhealthy",
                "database": "disconnected",
                "timestamp": "2024-01-01T00:00:00"
            }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "error",
            "database": "error",
            "timestamp": "2024-01-01T00:00:00"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)