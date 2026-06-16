#!/usr/bin/env bash

set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/Rena41615/EVA3-Ing-Sol-IA.git}"
BRANCH="${BRANCH:-main}"
# Default target dir: /home/ec2-user/app so user can `cd ~/app/deploy` like in the guide
TARGET_DIR="${TARGET_DIR:-/home/ec2-user/app}"

echo "[bootstrap] Repo: $REPO_URL"
echo "[bootstrap] Branch: $BRANCH"
echo "[bootstrap] Target dir: $TARGET_DIR"

if [ "$(id -u)" -ne 0 ]; then
  echo "This script must be run as root or with sudo. Re-run with sudo." >&2
  exit 1
fi

echo "[bootstrap] Installing prerequisites..."

# Detect package manager and install git + docker
if command -v dnf >/dev/null 2>&1; then
  dnf update -y
  dnf install -y git docker
elif command -v apt-get >/dev/null 2>&1; then
  apt-get update -y
  apt-get install -y git docker.io curl
else
  echo "No supported package manager found (dnf/apt-get). Install git and docker manually." >&2
fi

echo "[bootstrap] Starting Docker..."
systemctl enable docker
systemctl start docker

echo "[bootstrap] Preparing application directory..."
if [ -d "$TARGET_DIR" ]; then
  echo "[bootstrap] Target exists, pulling latest..."
  git -C "$TARGET_DIR" fetch --all --prune
  git -C "$TARGET_DIR" checkout "$BRANCH"
  git -C "$TARGET_DIR" pull origin "$BRANCH"
else
  git clone --depth 1 --branch "$BRANCH" "$REPO_URL" "$TARGET_DIR"
fi

cd "$TARGET_DIR"

echo "[bootstrap] Copying example env files (if present)..."
if [ -f backend/.env.example ] && [ ! -f backend/.env ]; then
  cp backend/.env.example backend/.env || true
fi

if [ -f .env.example ] && [ ! -f .env ]; then
  cp .env.example .env || true
fi

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
