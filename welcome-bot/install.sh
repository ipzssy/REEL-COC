#!/usr/bin/env bash
# Installe le bot de bienvenue Clash Center sur le serveur (Ubuntu) et le lance en service.
set -e
DIR="$HOME/clash-welcome-bot"
BASE="https://raw.githubusercontent.com/ipzssy/REEL-COC/welcome-bot/welcome-bot"

if ! command -v node >/dev/null 2>&1 || [ "$(node -p 'process.versions.node.split(".")[0]')" -lt 18 ]; then
  echo "Installation de Node.js..."
  curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
  sudo apt-get install -y nodejs
fi

mkdir -p "$DIR"
cd "$DIR"
curl -fsSL "$BASE/bot.js" -o bot.js
curl -fsSL "$BASE/package.json" -o package.json
npm install --omit=dev --no-audit --no-fund

if [ ! -f .env ]; then
  read -r -s -p "Colle le token du bot puis appuie sur Entree (rien ne s'affiche) : " TOKEN </dev/tty
  echo
  printf 'DISCORD_TOKEN=%s\n' "$TOKEN" > .env
  chmod 600 .env
fi

sudo tee /etc/systemd/system/clash-welcome-bot.service >/dev/null <<UNIT
[Unit]
Description=Bot de bienvenue Clash Center
After=network-online.target
Wants=network-online.target

[Service]
User=$(whoami)
WorkingDirectory=$DIR
EnvironmentFile=$DIR/.env
ExecStart=$(command -v node) bot.js
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT

sudo systemctl daemon-reload
sudo systemctl enable clash-welcome-bot
sudo systemctl restart clash-welcome-bot
sleep 4
sudo systemctl --no-pager --lines=8 status clash-welcome-bot || true
echo "Termine."
