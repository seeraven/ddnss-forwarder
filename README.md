# Simple FritzBox to DDNSS Forwarder for IP Updates

This simple [flask] based server allows you to forward the DnyDNS update
requests of your [fritzbox] to the [ddnss] DynDNS service while adjusting
the IPv6 address correctly. This is necessary if you want to publish the
IPv6 address of a server and not the [fritzbox] itself.


## Motivation

When you expose a server on the internet using your [fritzbox] you do
usually configure a port forwarding in the [fritzbox] for dedicated
ports. For example, a web server uses the ports 80 for http and 443
for https.

For IPv4 the [fritzbox] is the only actor with an IP address reachable
from the internet, so a DNS record must use the IPv4 address of the
[fritzbox]. The [fritzbox] itself forwards the traffic depending on the
port and its configuration to the server.

For IPv6 however, things are different and no network address translation
(NAT) is performed. This can be seen if you check your IPv6 address with
the one reported on web sites showing your current IP address. The
reason for this is that for IPv6 the [fritzbox] actually gets a subnet
identified by the so called IPv6 prefix. This prefix is the first part
of the IPv6 address whereas the lower 64-bit part is the so called
interface identifier.

So the IPv6 address for a DNS record must be set to the combination of
the IPv6 prefix and the interface identifier!


## Installation

The prefered way of running this simple server is to use docker. First, we
build the docker image:

    $ git clone https://github.com/seeraven/ddnss-forwarder
    $ cd ddnss-forwarder
    $ git submodule update --init
    $ make build-docker

Then we start the docker container on the server using a port of your choice:

    $ docker run -d --restart=always -p 1234:8080 ddnss-forwarder:0.0.1


## Configuration of the Fritz!Box

In the configuration of the [fritzbox] you now use the following target URL
for the DynDNS update:

    http://<SERVER IP>:<PORT>/forward?key=<DDNSS KEY>&host=<HOST>&ip=<ipaddr>&ip6prefix=<ip6lanprefix>&ip6=<IPv6 SUFFIX>

Here, you have to replace the server ip, port, ddnss key, host and the ipv6 suffix
with your actual values. An example of the URL looks like

    http://192.168.100.2:1234/forward?key=secretkey&host=myhost.ddnss.org&&ip=<ipaddr>&ip6prefix=<ip6lanprefix>&ip6=a236:bcff:fee7:7b14


## Configuration of active Monitoring

ddnss-forwarder now supports also active monitoring of your domains. This is
configured using a `config.yaml` file. You should copy the `config.example.yaml`
file and adapt it to your needs. Then, you use the `-c` command line option
of ddnss-forwarder. When you use docker, don't forget to bind mount the file:

    $ docker run -d --restart=always -p 1234:8080 -v $PWD/config.yaml:/config.yaml ddnss-forwarder:0.0.1 -c /config.yaml


[flask]: https://flask.palletsprojects.com/en/3.0.x/
[fritzbox]: https://avm.de/produkte/fritzbox/
[ddnss]: https://www.ddnss.de/