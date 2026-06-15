@echo off
REM ========================================================================
REM Script de Instalación y Ejecución (Windows)
REM Agente Inteligente del Metro de Santiago - EP3
REM ========================================================================

setlocal enabledelayedexpansion

echo ╔════════════════════════════════════════════════════════════════╗
echo ║   AGENTE INTELIGENTE DEL METRO DE SANTIAGO - EP3              ║
echo ║   Script de Instalación y Ejecución (Windows)                 ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

if "%1"=="" (
    echo Uso: setup.bat [opción]
    echo.
    echo Opciones disponibles:
    echo   install              Instalar dependencias
    echo   agent                Ejecutar agente
    echo   dashboard            Ejecutar dashboard
    echo   docker-up            Levantar con Docker
    echo   docker-down          Detener Docker
    echo   test                 Probar instalación
    echo   clean                Limpiar logs y caché
    echo.
    exit /b 1
)

REM ========================================================================
REM Función: Instalar dependencias
REM ========================================================================

if "%1"=="install" (
    echo 📦 Instalando dependencias...
    
    if not exist "venv" (
        echo 📂 Creando entorno virtual...
        python -m venv venv
        echo ✓ Entorno virtual creado
    )
    
    echo Activando entorno virtual...
    call venv\Scripts\activate.bat
    
    echo 📥 Instalando paquetes...
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    
    echo ✓ Dependencias instaladas correctamente
    goto end
)

REM ========================================================================
REM Función: Ejecutar agente
REM ========================================================================

if "%1"=="agent" (
    echo.
    echo 🤖 Iniciando Agente Inteligente del Metro...
    echo.
    
    if not exist "venv" (
        echo ✗ Entorno virtual no encontrado
        echo   Ejecuta: setup.bat install
        exit /b 1
    )
    
    call venv\Scripts\activate.bat
    
    if not exist ".env" (
        echo ⚠️  No se encontró archivo .env
        echo    Creando desde .env.example...
        copy .env.example .env
        echo    ⚠️  IMPORTANTE: Edita .env y agrega tu OPENAI_API_KEY
        pause
    )
    
    if not exist "logs" mkdir logs
    if not exist "vector_db" mkdir vector_db
    
    python agente_metro.py
    goto end
)

REM ========================================================================
REM Función: Ejecutar dashboard
REM ========================================================================

if "%1"=="dashboard" (
    echo.
    echo 📊 Iniciando Dashboard de Monitoreo...
    echo.
    
    if not exist "venv" (
        echo ✗ Entorno virtual no encontrado
        echo   Ejecuta: setup.bat install
        exit /b 1
    )
    
    call venv\Scripts\activate.bat
    
    if not exist "logs\agent_logs.jsonl" (
        echo ⚠️  No se encontraron logs del agente
        echo    Por favor, ejecuta el agente primero en otra terminal:
        echo    setup.bat agent
        exit /b 1
    )
    
    echo ✓ Accede al dashboard en: http://localhost:8501
    echo.
    
    streamlit run dashboard.py
    goto end
)

REM ========================================================================
REM Función: Docker Up
REM ========================================================================

if "%1"=="docker-up" (
    echo 🐳 Levantando servicios con Docker...
    
    if not exist ".env" (
        echo ⚠️  No se encontró archivo .env
        copy .env.example .env
        echo    Edita .env con tus credenciales
        pause
    )
    
    docker-compose up --build
    goto end
)

REM ========================================================================
REM Función: Docker Down
REM ========================================================================

if "%1"=="docker-down" (
    echo 🛑 Deteniendo servicios Docker...
    docker-compose down
    echo ✓ Servicios detenidos
    goto end
)

REM ========================================================================
REM Función: Test
REM ========================================================================

if "%1"=="test" (
    echo 🧪 Probando instalación...
    
    if not exist "venv" (
        call :install_dependencies
    )
    
    call venv\Scripts\activate.bat
    
    echo    Verificando importaciones...
    python -c "import langchain; print('   ✓ langchain')"
    python -c "import openai; print('   ✓ openai')"
    python -c "import streamlit; print('   ✓ streamlit')"
    python -c "import pandas; print('   ✓ pandas')"
    python -c "import plotly; print('   ✓ plotly')"
    python -c "import psutil; print('   ✓ psutil')"
    
    echo.
    echo ✓ Todas las dependencias están instaladas correctamente
    goto end
)

REM ========================================================================
REM Función: Clean
REM ========================================================================

if "%1"=="clean" (
    echo 🧹 Limpiando archivos...
    
    for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
    del /s /q *.pyc 2>nul || true
    
    echo ✓ Limpieza completada
    goto end
)

REM ========================================================================
REM Opción no válida
REM ========================================================================

echo ❌ Opción no válida: %1
exit /b 1

REM ========================================================================
REM Fin del script
REM ========================================================================

:end
echo.
echo ✓ Operación completada
