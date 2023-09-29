# A CTO on a shoestring: How to setup a minimal app with almost no money

All the code in this blog post is in [github](https://github.com/nhatcher/users-template)

## Getting a domain name (~10€ a year)

You can buy a domain name from places like [namecheap](https://www.namecheap.com/), but there are many other vendors. Just make sure that they only sell you the domain name and nothing else. It should cost you around 10€ a year.
## Getting an email account

There are several paid vendor like Google. But we will use [Zoho](https://www.zoho.com/mail/zohomail-pricing.html) that for now is free.

## Server provision (~10€ a month)

You can buy a server from [Digital Ocean](https://www.namecheap.com/), [Scaleway](https://www.scaleway.com/en/) and many others. It should cost you around ~10€ a month.

Firewall:
```
 root@remote# apt install fail2ban
 root@remote# apt update
 root@remote# apt upgrade 
 root@remote# apt install ufw
 root@remote# ufw disable 
 root@remote# ufw default deny incoming+
 root@remote# ufw default deny incoming
 root@remote# ufw default allow outgoing
 root@remote# ufw allow ssh
 root@remote# ufw allow http
 root@remote# ufw allow https
 root@remote# ufw enable
```

Install and configure [caddy](https://caddyserver.com/docs/running):

```
root@remote# groupadd --system caddy
root@remote# useradd --system --gid caddy --create-home --home-dir /var/lib/caddy --shell /usr/sbin/nologin --comment "Caddy web server" caddy 
```

## Architecture

During development we will have three servers running. A proxy server will route all frontend requests to the frontend server and all api calls to the application server. This is very useful because then we will support HMR (Hot Module Reloading).

It works in the following way. A remote machine (a browser) will make requests to our server sitting in <https://www.example.com> for example. There are two kinds of requests:

1. Static content like JavaScript files, HTML, CSS, images that are public
2. API calls that will need to be processed by the server

There are many websites, most of them in fact, that are only of the first kind. They will just serve you the content you asked for. Personal websites and blogs are mostly of that kind.
You can host them for free on GitHub or [Neocities](https://neocities.org/) or many other places. You cannot login in those pages or consult a database or buy stuff. Those are called static websites and they are fairly easy to do.

The second kind of requests need a server, a program, to process some data and send some other data back. For instance a search engine will need to send a lits of URLs that contain some information. Many of those API calls are public, meaning everybody can use the service. Some might be private and only accessible if a user has logged in into the system



## The app design

Our web application will be as simple as possible. Users can:

* Log in and see, update and delete their personal data
* Log out
* Create accounts
* Recover password via email

Just the bare minimum that a world changing app needs to have. The frontend will be all done in HTML, modern JavaScript and CSS. No frills.

## The backend I: Setting up the django project

To begin with let's create a new folder for our application:

```
jsmith@example:~/Projects/$ mkdir feirou
jsmith@example:~/Projects/$ cd feirou
```

Now create a virtual environment for the project:

```
jsmith@example:~/Projects/feirou$ python -m venv venv
```

Where the second venv could be any name you like

Activate the virtual environment:

```
jsmith@example:~/Projects/feirou$ source venv/bin/activate
```

Install django:
```
(venv) $ pip install django
```
You will need to think a bit about the directory structure you want. In our case we want two fdirectories in the root directory of out project ‘frontend’ or client and ‘server’. We will go ahead and create those two directories and move to the sever directory:
```
(venv) $ mkdir server
(venv) $ cd server
```

Now we create a django project in that directory:
```
(venv) $ django-admin startproject settings .
```

Note two things. We call the project ‘settings’. That is because we want to have a settings directory for the django admin. Also note the period and the end. This is to create the project in our current directory. We call it settings so that django places all admit stuff in there.

Then we create the users app:
```
(venv) $ python manage.py startapp users
```

We want to create an app that lets users login with some credentials, create accounts, ask for forgotten passwords, etc. django manages some of this for us and we can use their auth system and not re-discover the wheel again. Although django’s user model solves many things for us, it is not very flexible. For instance you cannot add new fields to a user like a nickname or a telephone number or you can’t log in.

Create the `.env` file. NOT to be committed in github with the secret key and the support password

Extra packages:
```
(venv) $ pip install django-environment
```

## The backend II: The users or accounts app

## The backend III: The type checker, the formatter and the linter

We will use pyright, black and flake8

## The backend IV: Tests and the test runner

We will use pytest and pytest-cov

## The backend V: The different environments

We will use different django setting for local development, deployment and tests

## Logs, alerts, notifications and stats

Logs are messages emitted by the application or the operative system that can help us trace back errors or issues that happened through an event or series of events.
It can be informative, signal a warning or be worrisome errors.

Alerts are messages that we receive in our phones. We probably need to act on them. They signal a house on fire event.
Notifications are also messages that we receive in our movil devices that are just for our information, for example new accounts created.

Some logs may be updated to alerts or notifications depending on their importance.

Stats are numbers of certain occurrences that we feel are important. Like number of accounts created or the number of times people logged in into the system.


## Remote computer setup and deployment

Create a django user:
```
root@remote# groupadd --system django
root@remote# useradd --system --gid django --create-home --home-dir /var/lib/django --shell /usr/sbin/nologin --comment "Django app runner" django
```

## Setup the Postgres database

Install Postgres

```
# apt install libpq-dev postgresql postgresql-contrib
# apt install build-essential python3-dev
```

Log into an interactive Postgres session by typing:

```
# su postgres
$ psql
```

Create a database in the Postgres prompt. Words in angle brackets ("<>" symbols) are placeholders that you should replace with actual values. For example, "<users>" could become "jsmith":

```
postgres=# CREATE DATABASE <database-name>;
postgres=# CREATE USER <user> WITH PASSWORD '<password>';
postgres=# ALTER ROLE <user> SET client_encoding TO 'utf8';
postgres=# ALTER ROLE <user> SET default_transaction_isolation TO 'read committed';
postgres=# ALTER ROLE <user> SET timezone TO 'UTC';
postgres=# GRANT ALL PRIVILEGES ON DATABASE <database-name> TO <user>;

```



