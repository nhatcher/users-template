#!/bin/bash
# makes sure the program ends if any of the comands produces an error
set -e

# stop the service
systemctl stop gunicorn.service

# remove folder
rm -r /var/lib/django/users-template

# Set django shell to bash
chsh django -s /bin/bash

# change to django
sudo -i -u django /bin/bash << EOF
cd /var/lib/django/
git clone https://github.com/nhatcher/users-template.git
cd users-template
python -m venv venv
source venv/bin/activate
pip install -r production_requirements.txt
cd server
export DJANGO_SETTINGS_MODULE=settings.settings.production
python manage.py migrate
python manage.py collectstatic --settings=settings.settings.production --no-input
EOF

# Set django shell to nologin back
chsh django -s /usr/sbin/nologin

# copy files for the front end
rm -rf /var/www/users-template/
mkdir /var/www/users-template/
cp -r /var/lib/django/users-template/frontend_test/* /var/www/users-template/

# copy files for the admin pannel
mkdir /var/www/users-template/static/
cp -r /var/lib/django/static/* /var/www/users-template/static/

# make sure all is own by caddy user
chown caddy:caddy /var/www/ -R

# start the service again
systemctl start gunicorn.service
