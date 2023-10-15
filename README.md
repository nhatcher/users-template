# A simple template for a app with users

If you're looking to kickstart your Django application and have it up and running in a production environment within a few hours, consider forking the code from this repository. For comprehensive step-by-step guidance and additional alternatives and options, check out the accompanying [blog post](https://www.nhatcher.com/post/a-cto-on-a-shoestring/). It provides in-depth insights into each of the steps, helping you make the most of your Django project.

## Local installation

First clone the repository.

```
$ git clone https://github.com/nhatcher/users-template.git
```

After that create a virtual environment and install requirements

```
$ cd users-template/
$ python -m venv venv
$ source venv/bin/activate
```

Then you need to apply the migrations. This will create an sqlite3 file in `server/`.

```
(venv) $ cd server
(venv) server $ pip install -r requirements.txt
(venv) server $ python manage.py migrate
```

Create a superuser
```
(venv) $ python manage.py createsuperuser
```

Install [caddy](https://caddyserver.com/), only the binary in necessary. Note in particular that caddy shouldn't be running as a daemon in your local machine.
I normally download the binary, copy it to `/opt/caddy/` and add the path to `PATH` so it can be run in a terminal.

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

That's it, you can visit now <http://localhost:2080/> and test your application locally!

## Running tests:

That will run the linter, formatter, type checker and tests

```
(venv) $ ./run_tests.sh
```

## Create necessary accounts

1. Get your own domain name with Namecheap (will cost you ~10€ per year)
2. Create a Zoho account and link it to your domain name (free).
   In your zoho account create two email accounts. One for you the superuser and one for 'support@example.com'
3. Create an account in Sentry (free).
4. Create an account on DigitalOcean. Free until we create a droplet.

## Server provision and initial setup

Get the cheapest droplet in DigitalOcean. At the time of writing this is 4$/month. Choose the Ubuntu OS with the latest version (at the time of writing 23.04 x64, but the LTS version will work as well).

Make sure the Authentication method is 'SSH Key' and not 'Password'.
You should setup the VPS in a way that you can ssh with your username only if ssh keys are correctly setup. Feel free to change the Hostname.

Once the droplet is created make sure the DNS is configured properly and points to your computer. You should be able to `ssh root@example.com`. This usually involves changing DNS settings in you domain registrar provider. Note that it might take some time for the DNS config to propagate. This is a good moment to make yourself some coffee or go for a stroll. If you are lucky it's just a few minutes.

Don't install anything on your VPS or modify config files.

Create an `install` directory in the remote machine and copy the contents of everything inside `deployment_scripts/` into that folder:

```
jsmith@local:~/$ scp -r * root@example.com:~/install/
```

(You could also `rsync -a deployment_scripts root@example.com:~/` but that command is a bit dangerous)

Create the file `/etc/server_config.ini` filling each entry carefully.

In the remote computer, as a superuser run:
```
root@remote:~/install# ./install.sh
```

After that reboot your system. Just (from any directory):
```
# reboot
```

That's it! You are now ready for deployment!

As a final configuration we should create a user in the machine that you will use to mange the machine. Add the user to the sudoers list. Choose a good password.
```
# adduser jsmith
# usermod -aG sudo jsmith
```

Copy the ssh keys from `root` to `jsmith` and setup the right permissions
```
# mkdir /home/jsmith/.ssh/
# cp ~/.ssh/authorized_keys /home/jsmith/.ssh/authorized_keys
# chown jsmith:jsmith /home/jsmith/.ssh/ -R
# chmod 700 /home/jsmith/.ssh/ -R
```

Make sure you can ssh as `jsmith` from your local machine and run sudo commands.

In the remote machine, as root, remove your authorized_keys:
```
# rm ~/.ssh/authorized_keys
```

Now `root@example.com` should not work but `jsmith@example.com` should.


## Production logs and troubleshooting

1. Issues with systemd
Please refer to our [Systemd services crash course](https://github.com/nhatcher/users-template/tree/main/deployment_scripts#systemd-services-crash-course)

2. Caddy and gunicorn logs

If configured correctly caddy access logs should be at `/var/log/caddy/access.log` and ``. A nice way to inspect those logs is [jq](https://jqlang.github.io/jq/):

```
# tail -f /var/log/caddy/access.log | jq .request.uri
```

Similarly logs created by gunicorn will be at `/var/log/django/access.log` and `/var/log/django/error.log`.

3. Application logs

This are the logs generated by your application and they will be sent to Sentry.

## Deployment

If everything has been correctly set up, deployment will be a matter of running one script.

First push the code you want to deploy to the main branch on GitHub

As root in the remote computer just run
```
root@remote:~# deploy.sh
```

That will pull the latest code, create the virtualevn, install the dependencies, make migrations if needed and copy all the files needed.

Your app should be up and running at `https://app.example.com`

## License

Licensed under either of

* Apache License, Version 2.0 ([LICENSE-APACHE](LICENSE-APACHE) or http://www.apache.org/licenses/LICENSE-2.0)
* MIT license ([LICENSE-MIT](LICENSE-MIT) or http://opensource.org/licenses/MIT)

at your option.
