#!/usr/bin/env bash
# deploy.sh — собрать и запустить iHuman Manager на хосте.
# Запускать ИЗ корня репозитория. Требует .env рядом (не коммитится).

set -euo pipefail

if [ ! -f .env ]; then
  echo "[deploy] .env not found. Скопируйте .env.example в .env и заполните." >&2
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "[deploy] Устанавливаю Docker..."
  curl -fsSL https://get.docker.com | sh
  sudo usermod -aG docker "$USER" || true
  echo "[deploy] Docker установлен. Выйдите из сессии и зайдите заново, затем повторно запустите ./deploy.sh"
  exit 0
fi

COMPOSE="docker compose"
if ! $COMPOSE version >/dev/null 2>&1; then
  COMPOSE="docker-compose"
fi

echo "[deploy] Подтягиваю latest..."
git pull --ff-only || true

echo "[deploy] Билд и запуск..."
$COMPOSE pull postgres || true
$COMPOSE build
$COMPOSE up -d

echo "[deploy] Статус:"
$COMPOSE ps

echo "[deploy] Логи бота (Ctrl+C чтобы выйти):"
$COMPOSE logs -f --tail=80 bot
