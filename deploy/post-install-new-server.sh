#!/bin/sh
# Idempotent bootstrap for a clean Ubuntu 24.04 application VPS.
# This script installs only the platform. It never copies production data,
# secrets, credentials, DNS records, or application releases.

set -eu

if [ "$(id -u)" -ne 0 ]; then
    echo "Run this post-install script as root." >&2
    exit 1
fi

export DEBIAN_FRONTEND=noninteractive
SSH_PORT=22

echo "[1/8] Base packages"
apt-get update
apt-get install -y \
    ca-certificates \
    caddy \
    curl \
    git \
    jq \
    openssl \
    postgresql-16 \
    postgresql-client-16 \
    python3 \
    python3-pip \
    python3-venv \
    rsync \
    sqlite3 \
    ufw \
    unattended-upgrades

echo "[2/8] Clock"
timedatectl set-timezone Europe/Moscow
timedatectl set-ntp true

ensure_system_user() {
    account="$1"
    home_dir="$2"
    if ! id "$account" >/dev/null 2>&1; then
        useradd \
            --system \
            --user-group \
            --create-home \
            --home-dir "$home_dir" \
            --shell /usr/sbin/nologin \
            "$account"
    fi
}

echo "[3/8] Service accounts"
ensure_system_user deploy /var/lib/sewing-deploy
ensure_system_user team-messenger /var/lib/shagaem-team-messenger
ensure_system_user sewing-monitor /var/lib/sewing-monitor

echo "[4/8] Private runtime directories"
install -d -m 0755 -o root -g root \
    /opt/sewing-web \
    /opt/sewing-web/releases \
    /opt/shagaem-team-messenger-releases
install -d -m 0750 -o deploy -g deploy \
    /var/lib/sewing-web \
    /var/backups/sewing-web
install -d -m 0750 -o postgres -g postgres \
    /var/backups/sewing-wms
install -d -m 0750 -o team-messenger -g team-messenger \
    /var/lib/shagaem-team-messenger \
    /var/backups/shagaem-team-messenger
install -d -m 0750 -o root -g deploy /etc/sewing-web
install -d -m 0750 -o root -g team-messenger /etc/shagaem-team-messenger
install -d -m 0755 -o root -g root /mnt/sewing-offsite

echo "[5/8] PostgreSQL loopback only"
install -d -m 0755 -o postgres -g postgres /etc/postgresql/16/main/conf.d
cat > /etc/postgresql/16/main/conf.d/99-sewing-network.conf <<'EOF'
# Managed by the Shagaem server bootstrap.
listen_addresses = '127.0.0.1,::1'
password_encryption = 'scram-sha-256'
ssl = on
EOF
chown postgres:postgres /etc/postgresql/16/main/conf.d/99-sewing-network.conf
chmod 0644 /etc/postgresql/16/main/conf.d/99-sewing-network.conf
systemctl enable postgresql
systemctl restart postgresql

echo "[6/8] SSH key-only access"
install -d -m 0755 -o root -g root /etc/ssh/sshd_config.d
cat > /etc/ssh/sshd_config.d/60-shagaem-hardening.conf <<'EOF'
PubkeyAuthentication yes
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin prohibit-password
X11Forwarding no
AllowAgentForwarding no
EOF
sshd -t
systemctl reload ssh

echo "[7/8] Host firewall"
ufw default deny incoming
ufw default allow outgoing
ufw allow "$SSH_PORT/tcp"
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

echo "[8/8] Service policy"
# Caddy must not request certificates or expose a default page before the
# reviewed production configuration and DNS cutover are ready.
systemctl disable --now caddy
systemctl enable --now unattended-upgrades

cat > /root/SHAGAEM_BOOTSTRAP_STATUS.txt <<'EOF'
Base server bootstrap completed.
Application code, production databases, env files, backups and DNS are NOT installed.
Continue with SERVER_MIGRATION.md and run the bootstrap readiness gate.
EOF
chmod 0600 /root/SHAGAEM_BOOTSTRAP_STATUS.txt

echo "Bootstrap complete. Reconnect using the SSH key and continue with SERVER_MIGRATION.md."
