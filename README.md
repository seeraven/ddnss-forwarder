# Simple FritzBox to DDNSS Forwarder for IP Updates

This simple [flask] based server allows you to forward the DnyDNS update
requests of your [fritzbox] to the [ddnss] DynDNS service while adjusting
the IPv6 address correctly. This is necessary if you want to publish the
IPv6 address of a server and not the [fritzbox] itself.


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


[flask]: https://flask.palletsprojects.com/en/3.0.x/
[fritzbox]: https://avm.de/produkte/fritzbox/
[ddnss]: https://www.ddnss.de/