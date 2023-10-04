# A CTO on a shoestring. <br><span style="font-size:14px">How to setup a minimal app with almost no money</span>

All the code in this blog post is in [github](https://github.com/nhatcher/users-template).



## Getting a domain name (~10€ a year)

You can buy a domain name from places like [namecheap](https://www.namecheap.com/), but there are many other vendors. Just make sure that they only sell you the domain name and nothing else. It should cost you around 10€ a year.

## Getting an email account

There are several paid vendor like Google. But we will use [Zoho](https://www.zoho.com/mail/zohomail-pricing.html) that for now is free.

To setup your email, you will need to follow the steps in one of these guides, [namecheap](https://www.namecheap.com/support/knowledgebase/article.aspx/9758/2208/how-to-set-up-zoho-email-for-my-domain/) or [zoho](https://www.zoho.com/mail/help/adminconsole/namecheap.html).

With this done you should be able to send a receive emails with your new fancy email address. You can up to 5 email accounts, for instance `hello@example.com` and `support@example.com` but you can configure zoho to get all emails on `hello@example.com`. You can also now send emails programmatically.

Now you should be able to send an email programmatically:
```python
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

# Configure in zoho
password = "my secret password"
domain = "example.com"
sender_user = f"support@{domain}"


def send_email(email):
    # Define to/from
    subject = "First email ever!"
    sender_title = "Example App Support"

    # Create message
    msg = MIMEText(
        "Hello world!",
        "plain",
        "utf-8",
    )
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = formataddr((str(Header(sender_title, "utf-8")), sender_user))
    msg["To"] = email

    # Create server object with SSL option
    server = smtplib.SMTP_SSL("smtp.zoho.com", 465)

    # Perform operations via server
    server.login(user, password)
    server.sendmail(user, [email], msg.as_string())
    server.quit()

if __name__ == "__main__":
    # who do you want to send the email to:
    to_address = "jsmith@example.com"
    send_email(to_address)
```

## Server provision (~5€ a month)

This is by far the most complicated bit. But you only have to do it once.

Before even getting a VPS you need a pair of ssh keys. You probably have already done it for GitHub.

Your cloud provider will probably let you [upload your public key](https://docs.digitalocean.com/products/droplets/how-to/add-ssh-keys/to-team/) so that every new VPS will have the ssh key installed.

I am using an instance in [DigitalOcean](https://www.digitalocean.com/) basic droplets that at the time of writing are advertised as 4$/month but because of billing issues turns out to be around 4.5€ a month. This is enough for our purposes.
Other options are [Scaleway](https://www.scaleway.com/en/), [Linode](https://www.linode.com/), [Hetzner](https://www.hetzner.com/), and many others.

1. Secure the server

Log into the remote server. That is normally done by:

```
$ ssh root@93.184.216.34
```
Where `93.184.216.34` is just the example IP.


Install `fail2ban`:
```
# apt install fail2ban
```

Make sure you can only ssh with a key and not with a password. So `ssh root@93.184.216.34` only works form your computer with the private ssh key.

Install the firewall:
```
root@remote# apt install ufw
root@remote# ufw disable
root@remote# ufw default deny incoming
root@remote# ufw default allow outgoing
root@remote# ufw allow ssh
root@remote# ufw allow http
root@remote# ufw allow https
root@remote# ufw enable
```

Create a user and add it to the sudoers list. Make sure you can ssh with that user and remove ssh root access to the machine.

```
root@remote# adduser username
```

Where username is your username, for instance 'jsmith'. Add it to the sudoers list:

```
root@remote# usermod -aG sudo jsmith
```

As `jsmith` copy the contents of the root's `authorized_keys` file (usually at `/root/.ssh/authorized_keys`) to the username's `authorized_keys` file (`/home/username/.ssh/authorized_keys`). In a different terminal test that you can ssh as the new username:

```
$ ssh jsmith@93.184.216.34
```

Once in the remote computer check that you can become a superuser by typing `sudo su` and entering your password. Now keep your password safe and delete the contents of the root's `authorized_keys` file. The contents not the file.

Congratulations, you have secured your server. You should not be able to ssh as root anymore.

Now, there are still services running on your computer you might not be aware of. One of them is the OSI layer 3 echo ICMP server built in the operative system. For your laptop at home try:

```
$ ping -c 5 example.com
PING example.com (93.184.216.34) 56(84) bytes of data.
64 bytes from example.com (93.184.216.34): icmp_seq=1 ttl=52 time=26.0 ms
64 bytes from example.com (93.184.216.34): icmp_seq=2 ttl=52 time=30.1 ms
64 bytes from example.com (93.184.216.34): icmp_seq=3 ttl=52 time=24.4 ms
64 bytes from example.com (93.184.216.34): icmp_seq=4 ttl=52 time=25.7 ms
64 bytes from example.com (93.184.216.34): icmp_seq=5 ttl=52 time=27.8 ms

--- example.com ping statistics ---
5 packets transmitted, 5 received, 0% packet loss, time 4006ms
rtt min/avg/max/mdev = 24.359/26.784/30.122/1.988 ms
```

This is helpful to test if your computer is up and the network is listening. Note that we have not allowed the service in the firewall, yet it is there running. This is telling you that a round trip time for  ping request to your machine is around 26 milliseconds.

Your cloud provider might also feature some firewall settings. I don't think that setting a firewall both at the os level and at the cloud provider level would break anything but it's probably not a great idea since it might lead to difficult to debug issues. But you should go ahead and read about the firewall in your cloud provider and play with it a little bit. If you are using DigitalOcean in the control panel select Networking->Firewalls->Create Firewall. Once created you can _assign_ the firewall to the droplet in the firewall page. As usual DigitalOcean shines on good documentation. You could set some rules and see how they affect your droplet. Generally speaking though you should accept the ssh, https and icmp inbound rules and allow all outbound communication.


2. Point your domain name to your computer

We want your ip to point to your computer, this will buy us two things:

* We will be able to do `ssh jsmith@example.com` instead of using the ip
* Your friends will be able to visit `www.example.com` and land to your webpage!

We do this by configuring the DNS records in your DNS host provider. This is not difficult, but I bet you will have some stories to tell if you spend enough time configuring those.
Normally your domain registar will provide you with a full featured GUI to config those DNS records in the _zone file_.

The only thing you have to do is to add a couple of `A Record`'s in your advanced DNS settings. If you are using Namecheap will look something like:
![namecheap config](images/namecheap_config.png "Configuring DNS records")

Note that we are adding three `A record`s:
* *`@` Record* directs the root domain ('example.com') to your IP
* *`www` Record* directs the subdomain 'www.example.com' to your IP
* *`app` Record* directs the 'app.example.com' to your IP 

We will do that to have our webpage sitting in <https://www.example.com> and our web application sitting in <https://app.example.com>.

You don't need to do this. You can have everything in the root domain <https://example.com> like <https://twitter.com> or <https://stackoverflow.com>. Having a different subdomain for the application can help with a number of issues:
* You can have other services in other subdomains independent of the application
* The webpage subdomain and the application subdomain do not share any cookies

On the other hand if you don't have other services or you have other domains for them and you don't need a flashy landing page you can go and use the root domain.

At the end of the day wether you want to have the application sitting in your root domain or a subdomain is your decision.


3. Set up a simple TLS secured webserver.

We will now install a webserver in your VPS capable of serving static webpages and redirecting traffic. Apache and nginx are fine options but will be using [caddy](https://caddyserver.com).

First thing you should do is download the latest binary for your computer architecture. You can follow the instructions [in the caddy documentation](https://caddyserver.com/docs/install) but we will install the latest binary here:

```
root@remote# wget https://github.com/caddyserver/caddy/releases/download/v2.7.4/caddy_2.7.4_linux_amd64.tar.gz
root@remote# tar -xf caddy_2.7.4_linux_amd64.tar.gz
root@remote# cp caddy /opt/caddy/
root@remote# chmod +x /opt/caddy/caddy
```

Remember that if you do this you will ned to maintain caddy version's yourself and be specially aware of security updates.

We will follow [caddy](https://caddyserver.com/docs/running).

Add an underprivileged user

```
root@remote# groupadd --system caddy
root@remote# useradd --system --gid caddy --create-home --home-dir /var/lib/caddy --shell /usr/sbin/nologin --comment "Caddy web server" caddy 
```

Create two directories:
```
root@remote# mkdir /var/www/api/
root@remote# mkdir /var/www/website/
```

Now get an `index.html` file in each of them:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Website/App</title>
</head>
<body>
The app is sitting in the website/app endpoint
</body>
</html>
```

Make sure that everything is readable by caddy:

```
root@remote# chmown -R caddy:caddy /var/www/
```

Create a Caddyfile:
```
example.com {
    redir https://www.example.com{uri}
}

www.example.com {
	root * /var/www/website/

	file_server
}

app.example.com {
	root * /var/www/app/

	file_server
}
```
This is redirecting all traffic from 'example.com' to 'www.example.com'. Anything coming from 'www.example.com' is being served from the directory `/var/www/website/` and 'app.example.com' is being served from `/var/www/app/`. As simple as that. In this case both subdomains are served from the same VPS, but that doesn't need to be the case. <https://www.example.com> could be served form a different machine, maybe done in wordpress or in modern days in webflow or anything else. You could use a static site generator like [Hugo](https://gohugo.io/) or [Zola](https://www.getzola.org/) or build it yourself if you are brave and host it in GitHub or [Neocities](https://neocities.org/) 

Finally run caddy:
```
root@remote# /opt/caddy/caddy run
```

If you did everything alright and I didn't forget any instruction by visiting <https://example.com> you should be redirected to <https://www.example.com>. If you visit <https://www.example.com> or <https://api.example.com> you should see your two different html files.

Big congratulations! Note: everything should be out of the box https and not http. This is one of the big advantages of using caddy. You can, of course, use other webservers like nginx and configurations will not be much more difficult.

This is all good and dandy. But we can't keep running caddy from the terminal like we are doing now, we need to run it as a service.

To do that create a `/etc/systemd/system/caddy.service` with the following content:
```
[Unit]
Description=Caddy
Documentation=https://caddyserver.com/docs/
After=network.target network-online.target
Requires=network-online.target

[Service]
Type=notify
User=caddy
Group=caddy
ExecStart=/opt/caddy/caddy run --environ --config /etc/caddy/Caddyfile
ExecReload=/opt/caddy/caddy reload --config /etc/caddy/Caddyfile --force
TimeoutStopSec=5s
LimitNOFILE=1048576
LimitNPROC=512
PrivateTmp=true
ProtectSystem=full
AmbientCapabilities=CAP_NET_ADMIN CAP_NET_BIND_SERVICE

[Install]
WantedBy=multi-user.target
```

Copy the Caddyfile to `/etc/caddy/Caddyfile`.

Then run to reload the system daemons and the caddy daemon
```
root@remote# systemctl daemon-reload
root@remote# systemctl start caddy.service
```

Now you are running caddy as a service and can shut down your laptop and go for pizza or beer because you had your first deployment. Your system is up and running!

One final note. In this post we are only interested in the 'app.example.com' part. But for us it will be a bit more complicated because we will not be just serving plain static html files. We will need Caddy to work as a proxy server. We will fix that issue in the coming sections.

## Local development and architecture

During development we will have three servers running. A proxy server will route all frontend requests to the frontend server and all api calls to the application server. This is very useful because then we will support HMR (Hot Module Reloading).

It works in the following way. A remote machine (a browser) will make requests to our server sitting in <https://app.example.com> for example. There are two kinds of requests:

1. Static content like JavaScript files, HTML, CSS, images that are public
2. API calls that will need to be processed by the server

There are many websites, most of them in fact, that are only of the first kind. They will just serve you the content you asked for. Personal websites and blogs are mostly of that kind.
You can host them for free on GitHub or [Neocities](https://neocities.org/) or many other places. You cannot login in those pages or consult a database or buy stuff. Those are called static websites and they are fairly easy to do.

The second kind of requests need a server, a program, to process some data and send some other data back. For instance a search engine will need to send a lits of URLs that contain some information. Many of those API calls are public, meaning everybody can use the service. Some might be private and only accessible if a user has logged in into the system


## The app design and the wrireframes

Our web application will be as simple as possible. Users can:

* Log in and see, update and delete their personal data
* Log out
* Create accounts
* Recover password via email

Just the bare minimum that a world changing app needs to have. The frontend will be all done in HTML, modern JavaScript and CSS. No frills.

![example app wireframes](images/ExampleApp.svg "Wireframe for a simple App")
## The database design

Tables in the database.
* Users
* PendingUsers
* RecoverPassword

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

Python is showing it's age. We will use pyright, black and flake8

## The backend IV: Tests and the test runner

We will use pytest and pytest-cov

## The backend V: The different environments

We will use different django setting for local development, deployment and tests

## Running the tests with GitHub actions

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

In your production machine install Postgres and dependencies

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


## Extra A: A VPN with Wireguard

## Extra B: Deployments on tagging


## Extra C: Code defines infrastructure.

Using Terraform and Puppet



