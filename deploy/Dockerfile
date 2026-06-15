FROM python:3.11-slim

# ========================================================================
# Configuración del contenedor
# ========================================================================

WORKDIR /app

# Actualizar paquetes del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# ========================================================================
# Instalar dependencias Python
# ========================================================================

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ========================================================================
# Copiar archivos de la aplicación
# ========================================================================

COPY . .

# Crear directorios necesarios
RUN mkdir -p /app/logs /app/vector_db /app/data

# ========================================================================
# Variables de entorno
# ========================================================================

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# ========================================================================
# Comando por defecto
# ========================================================================

CMD ["python", "agente_metro.py"]
