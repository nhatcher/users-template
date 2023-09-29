# A simple template for a app with users

## Installation

First git pull the code. After create a virtual environment and install requirements

```
$ python -m venv venv
$ source venv/bin/activate
(venv) $ pip install -r requirements.txt
(venv) $ python manage.py makemigrations
(venv) $ python manage.py migrate
```

You need a file 'server/.env' with the correct environmental variables set:

```
DEBUG=True
SECRET_KEY="..."
FEIROU_SUPPORT_PASSWORD="..."
APP_URL="http://localhost:2080/"
SUPPORT_ENGINEER_EMAIL="..."
```

Create a superuser
```
(venv) $ python manage.py createsuperuser
```

## Running in a development environment


You need to have three servers running:

A proxy server:
```
$ caddy run
```

The front end:
```
frontend_test$ python -m http.server 5173
```

The django server:
```
(venv) server$ python manage.py runserver
```

## Running tests:

That will run the linter, formatter, type checker and tests

(venv) $ ./run_tests.sh

## Server setup

### Setup. One time only

1. Setup Caddy (or a different proxy server)

Install the caddy binary in your remote computer. I will assume it is on `/opt/caddy/caddy`.

Create a `caddy` user with no power :O.

Add it as a daemon. For instance with `systemd` this usually involves copying over the file `caddy.service` to `/etc/systemd/system/caddy.service`

Copy the `Caddyfile` to `/etc/caddy/Caddyfile`.

And then:
```
root@remote:~# systemctl start caddy
```

2. Setup the django app


## Production logs and troubleshooting

1. Issues with systemd

journalctl is your friend

2. Access logs

If configured correctly caddy access logs should be at `/var/log/caddy/access.log`. A nice way to inspect those logs is [jq](https://jqlang.github.io/jq/):

```
:~# tail -f /var/log/caddy/access.log | jq .request.uri
```

## Deployment

First push the code you want to deploy to the main branch.

As root in the remote computer just run
```
root@remote:~# deploy.sh
```

That will pull the latest code, create the virtualevn, install the dependencies, make migrations if needed and copy all the files needed.


## License

Licensed under either of

* Apache License, Version 2.0 ([LICENSE-APACHE](LICENSE-APACHE) or http://www.apache.org/licenses/LICENSE-2.0)
* MIT license ([LICENSE-MIT](LICENSE-MIT) or http://opensource.org/licenses/MIT)

at your option.
