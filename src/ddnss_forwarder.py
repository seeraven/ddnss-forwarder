#!/usr/bin/env python3
"""DDNSS-Forwarder.
"""


# -----------------------------------------------------------------------------
# Module Import
# -----------------------------------------------------------------------------
import argparse
import logging

from flask_forwarder import create_app

# -----------------------------------------------------------------------------
# Argument parsing
# -----------------------------------------------------------------------------
DESCRIPTION = """
DDNSS-Forwarder
===============

This small flask application listens to GET requests on the
`http://<hostname>:<port>/forward` URL with the following parameters:
  - key        - the key of https://www.ddnss.de/upd.php for authorization
  - host       - the host to update
  - ip         - the current IPv4 address
  - ip6prefix  - the current IPv6 prefix as a netmask
  - ip6        - the IPv6 suffix to construct the official address

It constructs the full IPv6 address by using the ip6prefix and the ip6
address by first removing the netmask suffix from the prefix. It then
connects to `https://www.ddnss.de/upd.php` and returns the result back
to the client.
"""


def get_parser() -> argparse.ArgumentParser:
    """Construct the parser.

    Return:
      Returns the constructed parser.
    """
    arg_parser = argparse.ArgumentParser(description=DESCRIPTION, formatter_class=argparse.RawTextHelpFormatter)
    arg_parser.add_argument("-p", "--port", help="Port to bind to. Default: %(default)s", type=int, default=8080)
    arg_parser.add_argument("-i", "--ip", help="IP to bind to. Default: %(default)s", default="0.0.0.0")
    arg_parser.add_argument("-d", "--debug", help="Enable debug output.", action="store_true", default=False)
    return arg_parser


# -----------------------------------------------------------------------------
# Main Function
# -----------------------------------------------------------------------------
def ddnss_forwarder() -> None:
    """Web interface main function."""
    parser = get_parser()
    args = parser.parse_args()

    logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.WARNING)

    web_app = create_app()
    web_app.run(host=args.ip, port=args.port, debug=args.debug, use_reloader=False)


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    ddnss_forwarder()
