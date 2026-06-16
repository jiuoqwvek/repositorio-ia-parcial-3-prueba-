#!/usr/bin/env bash
# Bootstrap idempotente para Amazon Linux 2023: instala Docker + Compose,
# clona el repo y deja listo el stack. Uso: bash bootstrap-ec2.sh [URL_REPO]
set -euo pipefail

REPO_URL="${1:-https://github.com/TU-USUARIO/TU-REPO.git}"
APP_DIR="$HOME/app"

echo ">> Instalando Docker…"
if ! command -v docker >/dev/null 2>&1; then
  sudo dnf install -y docker
  sudo systemctl enable --now docker
  sudo usermod -aG docker "$USER" || true
fi

echo ">> Instalando plugin docker compose…"
if ! docker compose version >/dev/null 2>&1; then
  sudo mkdir -p /usr/local/lib/docker/cli-plugins
  ARCH="$(uname -m)"
  sudo curl -fsSL "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-${ARCH}" \
    -o /usr/local/lib/docker/cli-plugins/docker-compose
  sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
fi

echo ">> Clonando repo…"
if [ ! -d "$APP_DIR/.git" ]; then
  git clone "$REPO_URL" "$APP_DIR"
else
  git -C "$APP_DIR" pull --ff-only
fi

echo ">> Listo. Siguiente:"
echo "   cd $APP_DIR/deploy && cp .env.example .env && nano .env"
echo "   sudo docker compose -f docker-compose.prod.yml up --build -d"
