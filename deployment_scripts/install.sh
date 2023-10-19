#!/bin/bash
# makes sure the program ends if any of the comands produces an error
set -e

# makes sure we are root
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root" 1>&2
    exit 1
fi

function help() {
    echo "Ussage install.sh -h -f <firewal> - c <caddyfile-template>"
    echo "options"
    echo "h    Prints this help and exists."
    echo "f    Select firewal: ufw, iptables or none (Default ufw)"
    echo "c    Select Caddyfile template (default Caddyfile.template)"
}

# Copy config file and smoke test that config file is ok
cp server_config.ini /etc/server_config.ini
python3 check_config.py

# We support x86_64 or aarch64 for now
platform=$(uname -m)
if [[ "${platform}" == "x86_64" ]]; then
	caddy_file="caddy_2.7.5_linux_amd64.tar.gz"
elif [[ "${platform}" == "aarch64" ]]; then
	caddy_file="caddy_2.7.5_linux_arm64.tar.gz"
else
	echo "Platform not supported ${platform}"
	exit 1
fi

# By default we will use Ubuntu's Uncomplicated FireWall.
firewall="ufw"
caddy_template="Caddyfile.template"

while getopts h:p:c: option; do
    case "${option}" in
        h)
            help
            exit;;
        f)
            firewall="${OPTARG}";;
        c)
            caddy_template="${OPTARG}";;
        \?)
            echo "Unsuported option: -${option}"
            help
            exit;;
    esac
done

# Set DEBIAN_FRONTEND to noninteractive so it doesn't bug us that much
export DEBIAN_FRONTEND=noninteractive

# update the system
apt update
# -y assumes yes if there are questions
# --force-confdef and --force-confold chose default config if there is otherwise old
apt upgrade -y -o "Dpkg::Options::=--force-confdef" -o "Dpkg::Options::=--force-confold"

# setup fail2ban
apt install -y fail2ban

# setup firewall
if [[ "${firewall}" == "ufw" ]]; then
    apt install -y ufw
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow ssh
    ufw allow http
    ufw allow https
    ufw --force enable
elif [[ "${firewall}" == "iptables" ]]; then
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

# install some dependencies
apt install -y python3-venv python-is-python3 git

# Install caddy
rm -rf downloads/
mkdir downloads
cd downloads
wget https://github.com/caddyserver/caddy/releases/download/v2.7.5/"${caddy_file}"
tar -xf "${caddy_file}"
mkdir -p /opt/caddy/
cp caddy /opt/caddy/
cd ..
rm -r downloads/

# Create system under-priviledged users
groupadd --system --force caddy
useradd --system --gid caddy --create-home --home-dir /var/lib/caddy --shell /usr/sbin/nologin --comment "Caddy web server" caddy || echo "User caddy already exists"

groupadd --system --force django
useradd --system --gid django --create-home --home-dir /var/lib/django --shell /usr/sbin/nologin --comment "Django app runner" django  || echo "User django already exists"

# create sshkey for the django user
su - django -s /bin/bash -c 'ssh-keygen -t ed25519 -C "Deployment key" -N "" -f ~/.ssh/id_ed25519'


# Install Postgres and dependencies
apt install -y libpq-dev postgresql postgresql-contrib build-essential python3-dev

# Configure the database
python montyplate.py db_init.template.sql > /var/lib/postgresql/db_init.sql
chown postgres:postgres /var/lib/postgresql/db_init.sql
su - postgres -c 'psql -f /var/lib/postgresql/db_init.sql'

# Create www directory if it does not exist
mkdir -p /var/www/

# copy Caddyfile
mkdir -p /etc/caddy/
python montyplate.py "${caddy_template}" > /etc/caddy/Caddyfile

if [[ "${caddy_template}" == "Caddyfile.template" ]]; then
    mkdir -p /var/www/site/
    echo "This is the main landing page" > "/var/www/site/index.html"
fi
chown caddy:caddy /var/www/ -R

# Create django log directory
mkdir -p /var/log/django
chown django:django /var/log/django/

# Create caddy log directory
mkdir -p /var/log/caddy
chown caddy:caddy /var/log/caddy/

# copy deploy script
python montyplate.py deploy.template.sh > /bin/deploy.sh
chmod +x /bin/deploy.sh


# copy service files
cp services/caddy.service /etc/systemd/system/caddy.service
python montyplate.py services/gunicorn.template.service > /etc/systemd/system/gunicorn.service

systemctl daemon-reload

# enable the services
systemctl enable caddy
systemctl enable gunicorn

# start the caddy server
systemctl start caddy

echo -e "\n\n\n"
echo "*********************************************************"
echo "✨ ✨ System installed succesfully! ✨ ✨"
echo "Please reboot your system."
echo "If your remote repository is private, please add the key:"
echo -e "\n"
cat /var/lib/django/.ssh/id_ed25519.pub
echo -e "\n"
echo "To your GitHub repo with read access. Find more information at:"
echo "https://docs.github.com/en/authentication/connecting-to-github-with-ssh/managing-deploy-keys#deploy-keys"
echo -e "\n"
echo "Once those two things are done. Just run as root:"
echo "deploy.sh"
