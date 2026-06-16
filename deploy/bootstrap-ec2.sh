#!/usr/bin/env bash

set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/Rena41615/EVA3-Ing-Sol-IA.git}"
BRANCH="${BRANCH:-main}"
# Default target dir: /home/ec2-user/app so user can `cd ~/app/deploy` like in the guide
TARGET_DIR="${TARGET_DIR:-/home/ec2-user/app}"

echo "[bootstrap] Repo: $REPO_URL"
echo "[bootstrap] Branch: $BRANCH"
echo "[bootstrap] Target dir: $TARGET_DIR"

# Determine invoking user and home so the repo ends up in ~/app for that user
if [ -n "${SUDO_USER:-}" ]; then
  INVOKING_USER="$SUDO_USER"
else
  INVOKING_USER="$(whoami)"
fi
INVOKING_HOME=$(eval echo "~$INVOKING_USER")

# Use $HOME of the invoking user if TARGET_DIR not provided
TARGET_DIR="${TARGET_DIR:-$INVOKING_HOME/app}"

# Helper to run commands as root when necessary
if [ "$(id -u)" -ne 0 ]; then
  SUDO_CMD="sudo"
else
  SUDO_CMD=""
fi

echo "[bootstrap] Installing prerequisites..."

# Detect package manager and install git + docker
if command -v dnf >/dev/null 2>&1; then
  $SUDO_CMD dnf update -y
  $SUDO_CMD dnf install -y git docker
elif command -v apt-get >/dev/null 2>&1; then
  $SUDO_CMD apt-get update -y
  $SUDO_CMD apt-get install -y git docker.io curl
else
  echo "No supported package manager found (dnf/apt-get). Install git and docker manually." >&2
fi

echo "[bootstrap] Starting Docker..."
$SUDO_CMD systemctl enable docker
$SUDO_CMD systemctl start docker

echo "[bootstrap] Preparing application directory..."
echo "[bootstrap] Preparing application directory: $TARGET_DIR"
if [ -d "$TARGET_DIR" ]; then
  echo "[bootstrap] Target exists, pulling latest..."
  # Ensure ownership so pulls work without sudo for the invoking user
  $SUDO_CMD chown -R "$INVOKING_USER":"$INVOKING_USER" "$TARGET_DIR" || true
  if [ "$INVOKING_USER" = "$(whoami)" ]; then
    git -C "$TARGET_DIR" fetch --all --prune
    git -C "$TARGET_DIR" checkout "$BRANCH"
    git -C "$TARGET_DIR" pull origin "$BRANCH"
  else
    sudo -u "$INVOKING_USER" git -C "$TARGET_DIR" fetch --all --prune
    sudo -u "$INVOKING_USER" git -C "$TARGET_DIR" checkout "$BRANCH"
    sudo -u "$INVOKING_USER" git -C "$TARGET_DIR" pull origin "$BRANCH"
  fi
else
  # Ensure parent exists and is writable by the invoking user
  PARENT_DIR=$(dirname "$TARGET_DIR")
  $SUDO_CMD mkdir -p "$PARENT_DIR"
  $SUDO_CMD chown "$INVOKING_USER":"$INVOKING_USER" "$PARENT_DIR"
  # Clone as invoking user so the files are owned correctly
  sudo -u "$INVOKING_USER" git clone --depth 1 --branch "$BRANCH" "$REPO_URL" "$TARGET_DIR"
fi

# Ensure the target directory is owned by the invoking user
$SUDO_CMD chown -R "$INVOKING_USER":"$INVOKING_USER" "$TARGET_DIR" || true

cd "$TARGET_DIR"

echo "[bootstrap] Copying example env files (if present)..."
if [ -f backend/.env.example ] && [ ! -f backend/.env ]; then
  cp backend/.env.example backend/.env || true
fi

if [ -f .env.example ] && [ ! -f .env ]; then
  cp .env.example .env || true
fi

# Ensure .env contains required keys (SITE_ADDRESS, GITHUB_TOKEN, OPENAI_API_KEY)
ensure_key() {
  FILE="$1"
  KEY="$2"
  if [ -f "$FILE" ]; then
    if ! grep -qE "^${KEY}=" "$FILE"; then
      echo "${KEY}=" >> "$FILE"
      echo "[bootstrap] Added ${KEY} to ${FILE}"
    fi
  else
    echo "${KEY}=" > "$FILE"
    echo "[bootstrap] Created ${FILE} with ${KEY}"
  fi
}

ensure_key ".env" "SITE_ADDRESS"
ensure_key ".env" "GITHUB_TOKEN"
ensure_key ".env" "OPENAI_API_KEY"
ensure_key "backend/.env" "SITE_ADDRESS"
ensure_key "backend/.env" "OPENAI_API_KEY"

echo "[bootstrap] Checking Docker..."

docker --version

    if docker compose version >/dev/null 2>&1; then
        echo "[bootstrap] Building and starting services..."
        # Prefer a production compose file under deploy/ if present
        if [ -f ./deploy/docker-compose.prod.yml ]; then
            docker compose -f ./deploy/docker-compose.prod.yml up -d --build
        else
            docker compose up -d --build
        fi
    elif command -v docker-compose >/dev/null 2>&1; then
    echo "[bootstrap] Building and starting services with docker-compose..."
    if [ -f ./deploy/docker-compose.prod.yml ]; then
        docker-compose -f ./deploy/docker-compose.prod.yml up -d --build
    else
        docker-compose up -d --build
    fi
else
    echo "[ERROR] Docker Compose is not installed. Trying fallback: ./deploy/setup.sh"
    if [ -x ./deploy/setup.sh ]; then
        ./deploy/setup.sh install
        ./deploy/setup.sh docker-up
    else
        echo "[ERROR] No deploy/setup.sh found or not executable. Install docker-compose or provide a deploy script." >&2
        exit 1
    fi
fi

echo "[bootstrap] Deployment finished."
docker ps
