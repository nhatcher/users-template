#!/bin/bash
# makes sure the program ends if any of the comands produces an error
set -e

# update the system
apt update
apt upgrade

# setup firewall
apt install fail2ban
apt install ufw
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow http
ufw allow https
ufw enable

apt install python3.10-venv
apt install python-is-python3
apt install git

# Install caddy
mkdir downloads
cd downloads
wget https://github.com/caddyserver/caddy/releases/download/v2.7.4/caddy_2.7.4_linux_amd64.tar.gz
tar -xf caddy_2.7.4_linux_amd64.tar.gz
mkdir /opt/caddy/
cp caddy /opt/caddy/
cd ..
rm -r downloads/

# Create system under-priviledged users
groupadd --system caddy
useradd --system --gid caddy --create-home --home-dir /var/lib/caddy --shell /usr/sbin/nologin --comment "Caddy web server" caddy

groupadd --system django
useradd --system --gid django --create-home --home-dir /var/lib/django --shell /usr/sbin/nologin --comment "Django app runner" django


# Install Postgres and dependencies
apt install libpq-dev postgresql postgresql-contrib
apt install build-essential python3-dev

# Configure the database
python montyplate.py db_init.template.sql > db_init.sql
su postgres
psql -f db_init.sql
exit

# copy service files
cp caddy.service /etc/systemd/system/caddy.service
python montyplate.py gunicorn.template.service > /etc/systemd/system/gunicorn.service

# copy Caddyfile
mkdir /etc/caddy/
python montyplate.py Caddyfile.template > /etc/caddy/Caddyfile

# copy deploy script
python montyplate.py deploy.template.sh > /bin/deploy.sh
chown +x /bin/deploy.sh

systemctl daemon-reload

# start the caddy server
systemctl start caddy.service

# copy deploy script
cp deploy.sh /bin/deploy.sh