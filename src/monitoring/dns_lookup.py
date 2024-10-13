"""Helper to retrieve the IPs from the DNS."""

# ----------------------------------------------------------------------------
# Module Import
# ----------------------------------------------------------------------------
import logging
import socket
from typing import Optional

# ----------------------------------------------------------------------------
# Internal Constants
# ----------------------------------------------------------------------------
LOGGER = logging.getLogger()


# ----------------------------------------------------------------------------
# Exported Functions
# ----------------------------------------------------------------------------
def get_ipv4(domain: str) -> Optional[str]:
    """Get the IPv4 address of the domain from DNS."""
    try:
        results = socket.getaddrinfo(domain, 80, family=socket.AF_INET)
    except socket.gaierror as e:
        LOGGER.error("Error while retrieving address for %s: %s", domain, e)
        return None
    if results:
        return results[0][4][0]
    LOGGER.error("Can't get IPv4 address for %s!", domain)
    return None


def get_ipv6(domain: str) -> Optional[str]:
    """Get the IPv6 address of the domain from DNS."""
    try:
        results = socket.getaddrinfo(domain, 80, family=socket.AF_INET6)
    except socket.gaierror as e:
        LOGGER.error("Error while retrieving address for %s: %s", domain, e)
        return None
    if results:
        return results[0][4][0]
    LOGGER.error("Can't get IPv6 address for %s!", domain)
    return None
