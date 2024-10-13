"""Monitoring worker."""

# ----------------------------------------------------------------------------
# Module Import
# ----------------------------------------------------------------------------
import logging
import time
from threading import Thread
from typing import Any, Dict, Optional

import requests

from .dns_lookup import get_ipv4, get_ipv6
from .fritzbox_ips import get_current_ipv4, get_current_ipv6_prefix
from .ipv6_combination import combine_ipv6_address

# ----------------------------------------------------------------------------
# Internal Constants
# ----------------------------------------------------------------------------
LOGGER = logging.getLogger()


# ----------------------------------------------------------------------------
# Worker Class
# ----------------------------------------------------------------------------
class MonitorWorker(Thread):
    """The worker thread monitoring one domain."""

    def __init__(self, domain: str, config: Dict[str, Any]) -> None:
        """Construct a new worker."""
        super().__init__()
        self.host = domain
        self.check_interval = int(config["check_interval"])
        self.fritzbox = config["fritzbox"]
        self.ip6_suffix = config["ip6_suffix"]
        self.update_key = config["update_key"]
        self.update_url = config["update_url"]

    def run(self) -> None:
        """The threads main function."""
        while True:
            current_ipv4: Optional[str] = None
            current_ipv6_prefix: Optional[str] = None
            dns_ipv4: Optional[str] = None
            dns_ipv6: Optional[str] = None
            while (current_ipv4 is None) or (current_ipv6_prefix is None) or (dns_ipv4 is None) or (dns_ipv6 is None):
                current_ipv4 = get_current_ipv4(self.fritzbox)
                current_ipv6_prefix = get_current_ipv6_prefix(self.fritzbox)
                dns_ipv4 = get_ipv4(self.host)
                dns_ipv6 = get_ipv6(self.host)
                if (current_ipv4 is None) or (current_ipv6_prefix is None) or (dns_ipv4 is None) or (dns_ipv6 is None):
                    LOGGER.error(
                        "Can't retrieve all current IP addresses from Fritz!Box for verification. "
                        "Retrying in 30 seconds."
                    )
                    time.sleep(30)

            current_ipv6 = combine_ipv6_address(current_ipv6_prefix, self.ip6_suffix)
            LOGGER.debug("Current IPv4 address is %s and current IPv6 prefix is %s.", current_ipv4, current_ipv6_prefix)
            LOGGER.debug("=> The current IPv6 address of the server is %s.", current_ipv6)
            LOGGER.debug(
                "Current DNS address of %s is IPv4 address %s and IPv6 address %s.", self.host, dns_ipv4, dns_ipv6
            )

            if current_ipv4 != dns_ipv4 or current_ipv6 != dns_ipv6:
                LOGGER.error("DNS record of domain %s is invalid! Updating DNS now...", self.host)
                update_url = self.update_url.replace("{key}", self.update_key)
                update_url = update_url.replace("{host}", self.host)
                update_url = update_url.replace("{ip4}", current_ipv4)
                update_url = update_url.replace("{ip6}", current_ipv6)

                try:
                    response = requests.get(update_url, timeout=30.0)
                    LOGGER.debug(
                        "DNS record of domain %s updated. Update url returned status code %d.",
                        self.host,
                        response.status_code,
                    )
                except requests.exceptions.Timeout:
                    LOGGER.error("Timeout while trying to update DNS record of domain %s!", self.host)
                except requests.exceptions.RequestException as e:
                    LOGGER.error("Exception while trying to update DNS record of domain %s: %s", self.host, e)

            else:
                LOGGER.debug("DNS record of domain %s is valid.", self.host)
            LOGGER.debug("Waiting %d seconds before next check of domain %s.", self.check_interval, self.host)
            time.sleep(self.check_interval)


# ----------------------------------------------------------------------------
# Worker Constructions
# ----------------------------------------------------------------------------
def construct_workers(config: Dict[str, Dict[str, Any]]) -> None:
    """Construct and start all worker threads."""
    for domain in config:
        worker_thread = MonitorWorker(domain, config[domain])
        LOGGER.info("Starting monitoring thread for domain %s.", domain)
        worker_thread.start()
