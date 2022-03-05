# autovpn
Gets OpenVPN server list, distributes by country and establishes connection.

Educational use only.

In case of connecting via proxy the use of VPN as a default gateway will be disabled. You'll have to add your routes manually.

## Usage

```
usage: autovpn4.py [-h] [-c COUNTRY] [-r] [-p PROXY:PORT]

Gets OpenVPN server list, distributes by country and establishes connection

optional arguments:
  -h, --help     show this help message and exit
  -c COUNTRY     Country short code
  -r             Random server
  -p PROXY:PORT  Connect via socks5 proxy. Format: <ip:port>.The use of VPN as a default gateway will
                 be disabled in this case. You'll have to add your routes manually
```

## Examples

`./autovpn.py -c US -r`

`./autovpn.py -p example.com:1080`
