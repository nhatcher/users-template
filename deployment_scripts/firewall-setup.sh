#!/bin/bash

# Flush existing rules
iptables -F

# Allow incoming SSH (port 22) traffic
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Allow established connections
iptables -A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT

# Allow incoming HTTP (port 80) traffic
iptables -A INPUT -p tcp --dport 80 -j ACCEPT

# Allow incoming HTTPS (port 443) traffic
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Allow loopback (localhost) traffic
iptables -A INPUT -i lo -j ACCEPT

# Allow ICMP (ping) traffic
iptables -A INPUT -p icmp --icmp-type echo-request -j ACCEPT

# Set the default policies to DROP (block all other incoming traffic)
iptables -P INPUT DROP
iptables -P FORWARD DROP

# Allow all outgoing traffic
iptables -P OUTPUT ACCEPT
