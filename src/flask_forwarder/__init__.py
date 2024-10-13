"""Flask application put into a module.
"""

# ----------------------------------------------------------------------------
# Module Import
# ----------------------------------------------------------------------------
import logging

import requests
from flask import Flask, request

# ----------------------------------------------------------------------------
# Internal Constants
# ----------------------------------------------------------------------------
LOGGER = logging.getLogger()
_HELP_PAGE = """
<h1>Help on DDNSS Forwarder</h1>
<p>Please use the <a href="/forward">/forward</a> URL with the following
parameters:
<ul>
  <li><b>key:</b> the key of https://www.ddnss.de/upd.php for authorization</li>
  <li><b>host:</b> the host to update</li>
  <li><b>ip:</b> the current IPv4 address</li>
  <li><b>ip6prefix:</b> the current IPv6 prefix as a netmask</li>
  <li><b>ip6:</b> the IPv6 suffix to construct the official address</li>
</ul>
</p>
"""


# ----------------------------------------------------------------------------
# Exported Functions
# ----------------------------------------------------------------------------
def create_app() -> Flask:
    """Create the flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile("config.py", silent=True)

    @app.route("/")
    def help_page():
        return _HELP_PAGE

    @app.route("/forward")
    def forward():  # pylint: disable=too-many-return-statements
        key = request.args.get("key", "")
        if not key:
            return "argument 'key' not provided", 400

        host = request.args.get("host", "")
        if not host:
            return "argument 'host' not provided", 400

        ip = request.args.get("ip", "")
        if not ip:
            return "argument 'ip' not provided", 400

        ip6prefix = request.args.get("ip6prefix", "")
        if not ip6prefix:
            return "argument 'ip6prefix' not provided", 400
        if "::" not in ip6prefix:
            return "argument 'ip6prefix' is not a netmask", 400

        ip6suffix = request.args.get("ip6", "")
        if not ip6suffix:
            return "argument 'ip6' not provided", 400

        # Examples for ip6prefix:
        #   2001:9e8:8963:b000::/64
        #   2001:9e8:896f::/64
        ip_elements = ip6prefix[: ip6prefix.index("::")].split(":")
        while len(ip_elements) < 4:
            ip_elements.append("0")
        ip_elements += ip6suffix.split(":")

        ip6 = ":".join(ip_elements)
        tgt_url = f"https://www.ddnss.de/upd.php?key={key}&host={host}&ip={ip}&ip6={ip6}"

        LOGGER.debug("Forwarding request to %s.", tgt_url)
        r = requests.get(tgt_url, timeout=30)
        LOGGER.debug("Status code: %d", r.status_code)
        LOGGER.debug("Content:     %s", r.content)
        return r.content, r.status_code, r.headers.items()

    return app
