# Deployment scripts

Generally speaking you should just scp the contents of this folder to your VPS:

```
(local)$ rsync -a deployment_scripts/ root@example.com:~/
(local)$ scp ~/secrets/server_config.ini root@example.com:~/deployment_scripts/
```

The just run:

```bash
# ./install.sh
```

## Templates

Instead of using environmental variables we have all our secrets and settings in an ini file. Scripts that require information from this file are marked as 'templates' and are pre processed with `montyplate.py`. So if you have an error of sorts always remember to montiplate the templates.

## Firewall

We use the uncomplicated firewall. There are a number of reason that might be not ok for your use case. If you want to use `iptables` directly run
```bash
# ./install.sh -p
```

## Caddyfile.template

The present `Caddyfile` will also assume that your website is being served from this computer. If you just want to serve the application:

```
# ./install -c
```

## Systemd services crash course
Systemd is responsible for initializing and managing the system, including the startup and shutdown of services and daemons. It's widely used in modern Linux distributions to manage system processes and services. Makes sure some programs are run at startup and restarts them if something happens, doing also the role of a supervisor.
        
The basic building blocks in systemd are "units." Units can represent services devices, mount points, sockets, and more.
Service units are the most common and are used to manage system services and daemons.

We will be mostly interested in 'Unit Files', configuration files that define how systemd should manage a unit. They reside in the /etc/systemd/system directory.

To interact with systemd, you use commands like systemctl:
* `systemctl start caddy`.  Starts a service.
* `systemctl stop caddy`. Stops a service.
* `systemctl restart caddy`. Restarts a service.
* `systemctl enable caddy`. Enables a service to start at boot.
* `systemctl disable caddy`. Disables a service from starting at boot.
* `systemctl status caddy`. Checks the status of a service.
* `systemctl list-units`. Lists all active units.

Systemd has its own logging system called the Journal, which collects and stores log messages. You can use the journalctl command to view and search through logs. For instance:

```bash
# journalctl -u caddy
```


A typical unit file will have three sections:

* The `[Unit]` section where you provide metadata about the unit
* The `[Service]` section where the commands to start/stop/reload the service are set. Also you can specify the user the service is going to be run as.
* The `[Install]` section for us will be `WantedBy=multi-user.target` in all cases. That is similar to the old runlevel 3 of SystemV init, if you ever had to work with it.


```
[Unit]
Description=Caddy Server Daemon
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

For instance a good command to reload service is: `ExecReload=/bin/kill -s HUP $MAINPID` that basically send the HIP (Hangup signal) to the main process.