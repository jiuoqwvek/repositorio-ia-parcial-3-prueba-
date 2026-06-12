#!/bin/bash

# ========================================================================
# Script de Instalación y Ejecución
# Agente Inteligente del Metro de Santiago - EP3
# ========================================================================

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   AGENTE INTELIGENTE DEL METRO DE SANTIAGO - EP3              ║"
echo "║   Script de Instalación y Ejecución                           ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Verificar argumentos
if [ $# -eq 0 ]; then
    echo "Uso: ./setup.sh [opción]"
    echo ""
    echo "Opciones disponibles:"
    echo "  install              Instalar dependencias"
    echo "  agent                Ejecutar agente"
    echo "  dashboard            Ejecutar dashboard"
    echo "  docker-up            Levantar con Docker"
    echo "  docker-down          Detener Docker"
    echo "  test                 Probar instalación"
    echo "  clean                Limpiar logs y caché"
    echo ""
    exit 1
fi

# ========================================================================
# Función: Instalar dependencias
# ========================================================================

install_dependencies() {
    echo "📦 Instalando dependencias..."
    
    # Verificar Python
    if ! command -v python3 &> /dev/null; then
        echo "✗ Python 3 no está instalado"
        exit 1
    fi
    
    echo "✓ Python $(python3 --version) detectado"
    
    # Crear entorno virtual
    if [ ! -d "venv" ]; then
        echo "📂 Creando entorno virtual..."
        python3 -m venv venv
        echo "✓ Entorno virtual creado"
    fi
    
    # Activar entorno virtual
    source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null
    
    # Instalar dependencias
    echo "📥 Instalando paquetes..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    echo "✓ Dependencias instaladas correctamente"
}

# ========================================================================
# Función: Verificar configuración
# ========================================================================

check_configuration() {
    echo "🔍 Verificando configuración..."
    
    if [ ! -f ".env" ]; then
        echo "⚠️  No se encontró archivo .env"
        echo "   Creando desde .env.example..."
        cp .env.example .env
        echo "   ⚠️  IMPORTANTE: Edita .env y agrega tu OPENAI_API_KEY"
        echo "   Continúa cuando hayas configurado:"
        read -p "   Presiona Enter..."
    fi
    
    # Verificar que OPENAI_API_KEY está configurada
    if grep -q "sk-" .env; then
        echo "✓ Configuración detectada"
    else
        echo "✗ OPENAI_API_KEY no parece estar configurada correctamente"
        exit 1
    fi
}

# ========================================================================
# Función: Ejecutar agente
# ========================================================================

run_agent() {
    echo ""
    echo "🤖 Iniciando Agente Inteligente del Metro..."
    echo ""
    
    # Activar entorno virtual
    source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null
    
    # Verificar configuración
    check_configuration
    
    # Crear directorio de logs
    mkdir -p logs vector_db
    
    # Ejecutar agente
    python agente_metro.py
}

# ========================================================================
# Función: Ejecutar dashboard
# ========================================================================

run_dashboard() {
    echo ""
    echo "📊 Iniciando Dashboard de Monitoreo..."
    echo ""
    
    # Activar entorno virtual
    source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null
    
    # Verificar que existan logs
    if [ ! -f "logs/agent_logs.jsonl" ]; then
        echo "⚠️  No se encontraron logs del agente"
        echo "   Por favor, ejecuta el agente primero en otra terminal:"
        echo "   ./setup.sh agent"
        exit 1
    fi
    
    echo "✓ Accede al dashboard en: http://localhost:8501"
    echo ""
    
    # Ejecutar dashboard
    streamlit run dashboard.py
}

# ========================================================================
# Función: Docker Up
# ========================================================================

docker_up() {
    echo "🐳 Levantando servicios con Docker..."
    
    # Verificar que Docker existe
    if ! command -v docker-compose &> /dev/null; then
        echo "✗ docker-compose no está instalado"
        echo "   Instálalo desde: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    # Verificar .env
    check_configuration
    
    # Levantar servicios
    docker-compose up --build
}

# ========================================================================
# Función: Docker Down
# ========================================================================

docker_down() {
    echo "🛑 Deteniendo servicios Docker..."
    docker-compose down
    echo "✓ Servicios detenidos"
}

# ========================================================================
# Función: Test
# ========================================================================

test_installation() {
    echo "🧪 Probando instalación..."
    
    # Activar entorno virtual
    source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null
    
    # Probar importaciones
    echo "   Verificando importaciones..."
    python3 -c "import langchain; print('   ✓ langchain')"
    python3 -c "import openai; print('   ✓ openai')"
    python3 -c "import streamlit; print('   ✓ streamlit')"
    python3 -c "import pandas; print('   ✓ pandas')"
    python3 -c "import plotly; print('   ✓ plotly')"
    python3 -c "import psutil; print('   ✓ psutil')"
    
    echo ""
    echo "✓ Todas las dependencias están instaladas correctamente"
}

# ========================================================================
# Función: Clean
# ========================================================================

clean() {
    echo "🧹 Limpiando archivos..."
    
    # Limpiar cache de Python
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    
    # Limpiar .env (opcional)
    # rm -f .env
    
    echo "✓ Limpieza completada"
}

# ========================================================================
# Ejecutar opción seleccionada
# ========================================================================

case "$1" in
    install)
        install_dependencies
        ;;
    agent)
        run_agent
        ;;
    dashboard)
        run_dashboard
        ;;
    docker-up)
        docker_up
        ;;
    docker-down)
        docker_down
        ;;
    test)
        install_dependencies
        test_installation
        ;;
    clean)
        clean
        ;;
    *)
        echo "❌ Opción no válida: $1"
        exit 1
        ;;
esac

echo ""
echo "✓ Operación completada"
