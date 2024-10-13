"""Helper to combine IPv6 prefix and address."""


# ----------------------------------------------------------------------------
# Exported Functions
# ----------------------------------------------------------------------------
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
