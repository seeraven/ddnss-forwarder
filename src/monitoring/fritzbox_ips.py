"""Helpers to retrieve the current IPs from the Fritz!Box."""

# ----------------------------------------------------------------------------
# Module Import
# ----------------------------------------------------------------------------
import logging
import re
from typing import Optional

import requests

# ----------------------------------------------------------------------------
# Internal Constants
# ----------------------------------------------------------------------------
LOGGER = logging.getLogger()

UPNP_ACTION_GET_IPV4 = "GetExternalIPAddress"
UPNP_ACTION_GET_IPV6 = "X_AVM_DE_GetExternalIPv6Address"
UPNP_ACTION_GET_IPV6_PREFIX = "X_AVM_DE_GetIPv6Prefix"

RE_EXTRACT_IPV4 = re.compile(r"<NewExternalIPAddress>([0-9.]*)</NewExternalIPAddress>")
RE_EXTRACT_IPV6 = re.compile(r"<NewIPv6Prefix>([0-9a-fA-F:]*)</NewIPv6Prefix>")


# ----------------------------------------------------------------------------
# Helper Functions
# ----------------------------------------------------------------------------
def get_url(fritzbox: str) -> str:
    """Get the URL to request."""
    return f"http://{fritzbox}:49000/igdupnp/control/WANIPConn1"


def get_soap_action_header(action: str) -> str:
    """Get the SOAPAction header for the specified action."""
    return f"urn:schemas-upnp-org:service:WANIPConnection:1#{action}"


def get_soap_action_body(action: str) -> str:
    """Get the body for the specified action."""
    return (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" '
        's:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"> <s:Body> '
        f'<u:{action} xmlns:u="urn:schemas-upnp-org:service:WANIPConnection:1" />'
        "</s:Body></s:Envelope>"
    )


# ----------------------------------------------------------------------------
# Exported Functions
# ----------------------------------------------------------------------------
def get_current_ipv4(fritzbox: str) -> Optional[str]:
    """Get the current external IPv4 address of the Fritz!Box."""
    try:
        response = requests.post(
            get_url(fritzbox),
            headers={
                "Content-Type": "text/xml; charset=utf-8",
                "SOAPAction": get_soap_action_header(UPNP_ACTION_GET_IPV4),
            },
            data=get_soap_action_body(UPNP_ACTION_GET_IPV4),
            timeout=10.0,
        )
    except requests.exceptions.Timeout:
        LOGGER.error("Timeout while trying to get external IPv4 address from Fritz!Box on %s!", fritzbox)
        return None
    except requests.exceptions.RequestException as e:
        LOGGER.error("Exception while trying to get external IPv4 address from Fritz!Box on %s: %s", fritzbox, e)

    ips = RE_EXTRACT_IPV4.findall(response.text)
    if ips:
        return ips[0]
    LOGGER.error("Can't extract IPv4 address from response of Fritz!Box %s!", response.text)
    return None


def get_current_ipv6_prefix(fritzbox: str) -> Optional[str]:
    """Get the current IPv6 prefix from the Fritz!Box."""
    try:
        response = requests.post(
            get_url(fritzbox),
            headers={
                "Content-Type": "text/xml; charset=utf-8",
                "SOAPAction": get_soap_action_header(UPNP_ACTION_GET_IPV6_PREFIX),
            },
            data=get_soap_action_body(UPNP_ACTION_GET_IPV6_PREFIX),
            timeout=10.0,
        )
    except requests.exceptions.Timeout:
        LOGGER.error("Timeout while trying to get IPv6 prefix from Fritz!Box on %s", fritzbox)
        return None
    except requests.exceptions.RequestException as e:
        LOGGER.error("Exception while trying to get external IPv6 address from Fritz!Box on %s: %s", fritzbox, e)

    ips = RE_EXTRACT_IPV6.findall(response.text)
    if ips:
        return ips[0]
    LOGGER.error("Can't extract IPv6 prefix from response of Fritz!Box %s!", response.text)
    return None
