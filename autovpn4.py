#!/usr/bin/python

import requests
import random
import base64
import subprocess
import os
import argparse
import time

vpnurl = "https://www.vpngate.net/api/iphone/"
tmpfile = "/tmp/autovpntmp.conf"
#proxyip = "127.0.0.1"
#proxyport = 9050


argparser = argparse.ArgumentParser(description="Gets OpenVPN server list, distributes by country and establishes connection")
argparser.add_argument("-c", metavar="COUNTRY", help="Country short code", type=str)
argparser.add_argument("-r", help="Random server", action="store_true")
argparser.add_argument("-p", metavar="PROXY:PORT", help="Connect via socks5 proxy. Format: <ip:port>.The use of VPN as a default gateway will be disabled in this case. You'll have to add your routes manually", type=str)
args = argparser.parse_args()

if args.c:
    country = args.c.upper()
else:
    country = False
if args.r:
    server = "R"
else:
    server = 0

if args.p:
    proxyip, proxyport = args.p.split(":")
    

def GetVPNList():
    
    try:
        vpnlist = requests.get(vpnurl).text.splitlines()
        return vpnlist
    except:
        return False

def ParseVPNList(vpnlist):
    header = {}
    servers = {}
    header = vpnlist[1].split(",")
    for i, v in enumerate(vpnlist):
        if i > 1 and i < len(vpnlist) - 2:
            items = v.split(",")
            if not items[6] in servers:
                servers[items[6]] = []
            server = {}
            for item, value in enumerate(items):
                server[header[item]] = value
            servers[items[6]].append(server)
    return servers

def SaveConfig(country, server):
    if os.path.isfile(tmpfile):
        os.remove(tmpfile)
    with open(tmpfile, "w") as conffile:
        decoded = base64.b64decode(vpnlist[country][server]["OpenVPN_ConfigData_Base64"])
        conffile.write(decoded.decode("utf-8"))

 
def PickRandomServer(country):
    if len(vpnlist[country]) > 1:
        return random.randrange(1, len(vpnlist[country]))
    else:
        return 0



def Connect(proxy):
    if proxy:
        vpn = subprocess.call(["openvpn", "--pull-filter", "ignore", "redirect-gateway", "--socks-proxy", proxyip, str(proxyport), "--daemon",  "--connect-retry-max", "1", "--config", tmpfile])
    else:
        vpn = subprocess.call(["openvpn", "--daemon", "--connect-retry-max", "1", "--config", tmpfile])
    if not vpn:
        time.sleep(10)
        if CheckConnection():
            return True
    return False

def CheckConnection():
    ipa = subprocess.Popen(["ip", "a"],stdout = subprocess.PIPE).communicate()[0]
    if "tun0" in str(ipa):
        return True
    else:
        return False

    

print("Getting list of VPN servers...", end="", flush=True)
vpnlist = GetVPNList()     
if vpnlist:
    print("Success")
else:
    print("Failed\nExiting.")
    exit(0)

vpnlist = ParseVPNList(vpnlist)

if not country:

    for country in vpnlist:
        print(str(len(vpnlist[country])) + "\t" + country + " ("+ vpnlist[country][0]["CountryLong"] + ")")

    while True:
        print("Enter country code: ", end ="")
        country = input().upper()
        if country in vpnlist:
            break
        else:
            print("Country code not found")

if server != "R":

    for i, server in enumerate(vpnlist[country]):
        print(str(i+1) + "\tIP: " + server["IP"]  + \
                "\t | Ping: " + server["Ping"] + \
                "\t | Speed: " + server["Speed"] + \
                "\t | Sessions: " + server["NumVpnSessions"] + \
                "\t | Message: \"" + server["Message"] + "\"")

    server = False

    if len(vpnlist[country]) == 1:
        while True:
            print("One server in list. Use it? (Y/n): ", end="")
            answer = input().upper()
            if answer == "N":
                print("Ok. Exiting.")
                exit(0)
            elif answer == "Y" or answer == "":
                server = 1
                break

else:
    if len(vpnlist[country]) > 1:
        server = random.randrange(1, len(vpnlist[country]))
    else:
        server = 1


if not server:
    while True:
        print("Enter server number. 'R' for random:  ", end ="")
        server = input().upper()
        try:
            server = int(server)
            if server > 0 and server <= len(vpnlist[country]):
                break
        except:
            if server == "R":
                server = random.randrange(len(vpnlist[country])-1)
                break
        print("Wrong input")


try:
    while True:
        print("Trying " + vpnlist[country][server-1]["IP"] + "...", end="", flush=True)
        SaveConfig(country, server-1)
        if Connect(args.p):
            print("Success")
        else:
            print("Fail")
            server = PickRandomServer(country)
            continue

        print("Press Ctrl+C to drop vpn and exit")
        while True:
            time.sleep(10)
            if not CheckConnection():
                print("Connection to " + vpnlist[country][server-1]["IP"] + " lost.")
                break
except KeyboardInterrupt:
    subprocess.call(["killall", "-9", "openvpn"])
    
    if os.path.isfile(tmpfile):
        os.remove(tmpfile)
