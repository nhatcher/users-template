#!/bin/bash
# makes sure the program ends if any of the comands produces an error
set -e

REPOSITORY_URL=<github.url>
REPOSITORY_NAME=<github.name>

# stop the service
systemctl stop gunicorn.service

# remove old directory if exists
rm -rf "/var/lib/django/$REPOSITORY_NAME"

# Set django shell to bash
chsh django -s /bin/bash

# change to django
sudo -i -u django /bin/bash << EOF
set -e
cd /var/lib/django/
git clone $REPOSITORY_URL  
cd $REPOSITORY_NAME
git log -n 1 --format="%H" > ../deployed_commit_id.txt
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
rm -rf /var/www/$REPOSITORY_NAME/
mkdir /var/www/$REPOSITORY_NAME/
cp -r /var/lib/django/$REPOSITORY_NAME/frontend_test/* /var/www/$REPOSITORY_NAME/

# copy files for the admin pannel
mkdir /var/www/$REPOSITORY_NAME/static/
cp -r /var/lib/django/static/* /var/www/$REPOSITORY_NAME/static/

# make sure all is own by caddy user
chown caddy:caddy /var/www/ -R

# start the service again
systemctl start gunicorn.service
