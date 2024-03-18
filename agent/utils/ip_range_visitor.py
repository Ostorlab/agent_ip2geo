"""Module Responsible for sending ip range geolocation"""

import ipaddress
from typing import Callable, Tuple, Any, List

from agent import ip2geo
from agent.ip2geo import logger


class Error(Exception):
    """Base Error"""


class IPGeoError(Error):
    """Error getting the IP geolocation"""


class IpRangeVisitor:
    """Ip range visitor implementation."""

    def dichotomy_ip_network_visit(
        self,
        ip_network: ipaddress.IPv4Network | ipaddress.IPv6Network,
        accept: Callable[
            [ipaddress.IPv4Network | ipaddress.IPv6Network], Tuple[bool, Any]
        ],
    ) -> Any:
        """get ip ranges based on geolocation"""

        should_continue, result = accept(ip_network)
        yield result
        if should_continue is False:
            return

        subnets: List[ipaddress.IPv4Network | ipaddress.IPv6Network] = list(
            ip_network.subnets()
        )

        if len(subnets) == 1:
            # reached the last block.
            return

        for subnet in subnets:
            yield from self.dichotomy_ip_network_visit(subnet, accept)

    @staticmethod
    def is_first_last_ip_same_geolocation(
        ip_network: ipaddress.IPv4Network | ipaddress.IPv6Network,
    ) -> Tuple[bool, Any]:
        """Compare geolocation of network extremes"""

        first, last = ip_network[0], ip_network[-1]
        locator = ip2geo.Ip2GeoLocator()
        first_location = locator.get_geolocation_details(str(first))
        last_location = locator.get_geolocation_details(str(last))

        if first_location is None or last_location is None:
            return True, (None, None, ip_network)

        if "errors" in first_location or "errors" in last_location:
            logger.warning(
                "Could not get geolocation details: %s", first_location.get("errors")
            )
            return True, (None, None, ip_network)

        if (
            first_location.get("latitude") is not None
            and last_location.get("latitude") is not None
            and first_location.get("longitude") is not None
            and last_location.get("longitude") is not None
        ):
            try:
                if (
                    first_location["latitude"] == last_location["latitude"]
                    and first_location["longitude"] == last_location["longitude"]
                ):
                    return False, (first_location, last_location, ip_network)
                else:
                    return True, (first_location, last_location, ip_network)
            except IPGeoError as e:
                logger.warning(
                    "Error happens in is_first_last_ip_same_geolocation process: %s",
                    str(e),
                )
        return True, (first_location, last_location, ip_network)
