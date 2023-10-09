#!/bin/bash
# makes sure the program ends if any of the comands produces an error
set -e

help()
{
    echo "Ussage install.sh [-p|-h]"
    echo "options"
    echo "h    UPrints this help and exists."
    echo "p    Use iptables firewall instead of ufw"
}

# We support x86_64 or aarch64 for now
platform=$(uname -m)
if [ "$platform" == "x86_64" ]
then
	caddy_file="caddy_2.7.4_linux_amd64.tar.gz"
elif [ "$platform" == "aarch64" ]
then
	caddy_file="caddy_2.7.4_linux_arm64.tar.gz"
else
	echo "Platform not supported $platform"
	exit 1
fi

# By default we will use Ubuntu's Uncomplicated FireWall.
firewall="ufw"

while getopts ":h" option; do
    case $option in
        h)
            help
            exit;;
        p)
            firewall="iptables";;
        *)
            echo "Unsuported option: $option"
            help
            exit;;
    esac
done


# update the system
apt update
apt upgrade

# setup fail2ban
apt install fail2ban

# setup firewall
if [ "$firewall" == "ufw" ]
then
    apt install ufw
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow ssh
    ufw allow http
    ufw allow https
    ufw enable
else
    # Run the firewall rules
    ./firewall-setup.sh

    # creates the restore script
    mkdir -p /opt/util/
    echo "#!/bin/sh" > /opt/util/restore-iptables.sh
    echo "/usr/bin/flock /run/.iptables-restore /opt/util/iptables-restore /etc/iptables/rules.v4" >> /opt/util/restore-iptables.sh

    # save current rules
    iptables-save > /etc/iptables/rules.v4

    # Creates the service and eanbles it
    cp services/iptables-persistent.service /etc/systemd/system/iptables-persistent.service
    systemctl enable iptables-persistent.service
fi

apt install python3.10-venv
apt install python-is-python3
apt install git

# Install caddy
mkdir downloads
cd downloads
wget https://github.com/caddyserver/caddy/releases/download/v2.7.4/$caddy_file
tar -xf $caddy_file
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
python montyplate.py db_init.template.sql > /var/lib/postgresql/db_init.sql
chown postgres:postgres /var/lib/postgresql/db_init.sql
su - postgres -c 'psql -f /var/lib/postgresql/db_init.sql'

# copy service files
cp services/caddy.service /etc/systemd/system/caddy.service
python montyplate.py services/gunicorn.template.service > /etc/systemd/system/gunicorn.service

# copy Caddyfile
mkdir /etc/caddy/
python montyplate.py Caddyfile.template > /etc/caddy/Caddyfile

# Create www directory if it does not exist
mkdir -p /var/wwww/

# Create django log directory
mkdir /var/log/django
chown django:django /var/log/django/

# copy deploy script
python montyplate.py deploy.template.sh > /bin/deploy.sh
chmod +x /bin/deploy.sh

systemctl daemon-reload

# enable the services
systemctl enable caddy.servive
systemctl enable gunicorn.service

# start the caddy server
systemctl start caddy.service