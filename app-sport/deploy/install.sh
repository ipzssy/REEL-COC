#!/usr/bin/env bash
# Debian/Ubuntu, en root. Usage : ./install.sh <url-git-du-depot>
set -euo pipefail
apt-get update && apt-get install -y nodejs git caddy   # vérifier node >= 18 (node -v) ; sinon installer via NodeSource
id fitbeat &>/dev/null || useradd --system --home /opt/fitbeat fitbeat
[ -d /opt/fitbeat ] && git -C /opt/fitbeat pull || git clone "$1" /opt/fitbeat
install -m 600 /dev/null /etc/fitbeat.env
grep -q ANTHROPIC /etc/fitbeat.env || echo "ANTHROPIC_API_KEY=A_REMPLIR" >> /etc/fitbeat.env
cp /opt/fitbeat/app-sport/deploy/fitbeat.service /etc/systemd/system/
systemctl daemon-reload && systemctl enable --now fitbeat
echo "Édite /etc/fitbeat.env (clé API) puis /etc/caddy/Caddyfile (voir deploy/Caddyfile), puis : systemctl restart fitbeat caddy"
