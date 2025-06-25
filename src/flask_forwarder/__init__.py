"""Flask application put into a module."""

# ----------------------------------------------------------------------------
# Module Import
# ----------------------------------------------------------------------------
import logging
from typing import Any, Dict

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
  <li><b>ip:</b> the current IPv4 address</li>
  <li><b>ip6prefix:</b> the current IPv6 prefix as a netmask</li>
  <li><b>ip6:</b> the IPv6 suffix to construct the official address</li>
</ul>
</p>
"""


# ----------------------------------------------------------------------------
# Exported Functions
# ----------------------------------------------------------------------------
# pylint: disable=duplicate-code
def combine_ipv6_address(ipv6_prefix: str, ipv6_suffix: str) -> str:
    """Combine the IPv6 prefix and suffix into a full IPv6 address."""
    elements = []
    # Add elements from prefix (4 elements at max)
    for item in ipv6_prefix.split(":"):
        if item == "":
            item = "0"
        elements.append(item)

        if len(elements) == 4:
            break

    # Ensure we have 4 elements
    while len(elements) < 4:
        elements.append("0")

    # Add elements from the suffix
    elements += ipv6_suffix.split(":")

    # Combine everything into on IPv6 string
    return ":".join(elements)


def create_app(config: Dict[str, Dict[str, Any]]) -> Flask:
    """Create the flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile("config.py", silent=True)

    @app.route("/")
    def help_page():
        return _HELP_PAGE

    @app.route("/forward")
    def forward():  # pylint: disable=too-many-return-statements
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

        updated = []
        not_updated = []
        for domain in config:
            domain_config = config[domain]
            ip6 = combine_ipv6_address(ip6prefix, domain_config["ip6_suffix"])
            update_url = domain_config["update_url"].replace("{key}", domain_config["update_key"])
            update_url = update_url.replace("{host}", domain)
            update_url = update_url.replace("{ip4}", ip)
            update_url = update_url.replace("{ip6}", ip6)
            LOGGER.debug("Requesting update of %s by calling %s.", domain, update_url)
            try:
                response = requests.get(update_url, timeout=30.0)
                LOGGER.debug(
                    "DNS record of domain %s updated. Update url returned status code %d.",
                    domain,
                    response.status_code,
                )
                updated.append(domain)
            except requests.exceptions.Timeout:
                LOGGER.error("Timeout while trying to update DNS record of domain %s!", domain)
                not_updated.append(domain)
            except requests.exceptions.RequestException as e:
                LOGGER.error("Exception while trying to update DNS record of domain %s: %s", domain, e)
                not_updated.append(domain)

        if not_updated:
            return f"Error updating domains {not_updated}.", 200
        return f"Updated the domains {updated}.", 200

    return app
