#!/usr/bin/env bash

set -e

echo "Setup script (root) - instala y ejecuta el proyecto"

usage(){
  cat <<EOF
Uso: ./setup.sh <opción>

Opciones:
  install     Instalar dependencias (crea venv y pip install -r requirements.txt si existe)
  agent       Ejecutar agente (backend/agente_metro.py)
  dashboard   Ejecutar dashboard (monitoring/dashboard.py)
  test        Ejecutar pruebas básicas (scripts/ejemplos.py)
  clean       Limpiar cachés (__pycache__, .pyc)
  help        Mostrar esta ayuda
EOF
}

install_dependencies(){
  echo "Instalando dependencias..."
  if ! command -v python3 &>/dev/null; then
    echo "Python3 no encontrado"
    exit 1
  fi

  if [ ! -d .venv ]; then
    python3 -m venv .venv
    echo "Entorno virtual creado en .venv"
  fi

  # Activar entorno
  # shellcheck source=/dev/null
  source .venv/bin/activate || source .venv/Scripts/activate || true

  pip install --upgrade pip
  if [ -f requirements.txt ]; then
    pip install -r requirements.txt
  else
    echo "Aviso: requirements.txt no encontrado en la raíz. Instala dependencias manualmente si hace falta."
  fi

  echo "Instalación finalizada"
}

run_agent(){
  echo "Iniciando agente (backend/agente_metro.py)..."
  source .venv/bin/activate 2>/dev/null || true
  mkdir -p logs vector_db
  python backend/agente_metro.py
}

run_dashboard(){
  echo "Iniciando dashboard (monitoring/dashboard.py)..."
  source .venv/bin/activate 2>/dev/null || true
  if [ ! -f logs/agent_logs.jsonl ]; then
    echo "Advertencia: logs/agent_logs.jsonl no encontrado. Ejecuta el agente para generar datos."
  fi
  streamlit run monitoring/dashboard.py
}

run_tests(){
  echo "Ejecutando pruebas (scripts/ejemplos.py)..."
  source .venv/bin/activate 2>/dev/null || true
  python scripts/ejemplos.py verificar_instalacion || python -c "print('Ejecutar pruebas manualmente: python scripts/ejemplos.py')"
}

clean(){
  echo "Limpiando caches..."
  find . -type d -name __pycache__ -exec rm -rf {} + || true
  find . -type f -name "*.pyc" -delete || true
  echo "Limpieza completada"
}

if [ $# -lt 1 ]; then
  usage
  exit 0
fi

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
  test)
    run_tests
    ;;
  clean)
    clean
    ;;
  help|--help|-h)
    usage
    ;;
  *)
    echo "Opción desconocida: $1"
    usage
    exit 1
    ;;
esac
