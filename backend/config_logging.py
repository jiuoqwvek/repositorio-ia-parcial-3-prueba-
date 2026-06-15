"""
Configuración de Logging para el Agente Inteligente del Metro de Santiago
"""

import logging
import logging.handlers
from pathlib import Path
from datetime import datetime

# ============================================================================
# CREAR DIRECTORIO DE LOGS
# ============================================================================

LOGS_DIR = Path("./logs")
LOGS_DIR.mkdir(exist_ok=True)

# ============================================================================
# CONFIGURAR LOGGER
# ============================================================================

def configurar_logging(nombre_modulo: str = __name__, nivel=logging.INFO):
    """
    Configura el logger con handlers a archivo y consola.
    
    Args:
        nombre_modulo: Nombre del módulo (usualmente __name__)
        nivel: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Logger configurado
    """
    
    logger = logging.getLogger(nombre_modulo)
    logger.setLevel(nivel)
    
    # Remover handlers previos para evitar duplicados
    logger.handlers.clear()
    
    # ========================================================================
    # Handler: Consola (stdout)
    # ========================================================================
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(nivel)
    
    console_format = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # ========================================================================
    # Handler: Archivo (rotativo)
    # ========================================================================
    
    log_file = LOGS_DIR / "agente_metro.log"
    
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)  # Archivo captura TODO
    
    file_format = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    
    # ========================================================================
    # Handler: Archivo de Errores (solo errores)
    # ========================================================================
    
    error_log_file = LOGS_DIR / "agente_metro_errors.log"
    
    error_handler = logging.FileHandler(
        filename=error_log_file,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    
    error_format = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d\n%(message)s\n',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    error_handler.setFormatter(error_format)
    logger.addHandler(error_handler)
    
    return logger

# ============================================================================
# LOGGER POR DEFECTO
# ============================================================================

logger = configurar_logging("agente_metro", logging.INFO)

# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def log_inicio_ejecucion(nombre_modulo: str):
    """Registra el inicio de la ejecución del módulo."""
    logger.info(f"{'='*70}")
    logger.info(f"INICIANDO: {nombre_modulo}")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info(f"{'='*70}")

def log_fin_ejecucion(nombre_modulo: str, exitoso: bool = True):
    """Registra el fin de la ejecución del módulo."""
    estado = "EXITOSO" if exitoso else "CON ERRORES"
    logger.info(f"{'='*70}")
    logger.info(f"FINALIZANDO: {nombre_modulo} ({estado})")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info(f"{'='*70}")

def log_error_critico(mensaje: str, excepcion: Exception = None):
    """Registra un error crítico."""
    logger.critical(f"ERROR CRÍTICO: {mensaje}")
    if excepcion:
        logger.critical(f"Excepción: {type(excepcion).__name__}: {str(excepcion)}")
        logger.exception("Traceback completo:")

# ============================================================================
# EXPORTAR
# ============================================================================

__all__ = [
    'logger',
    'configurar_logging',
    'log_inicio_ejecucion',
    'log_fin_ejecucion',
    'log_error_critico',
    'LOGS_DIR'
]
