""" Module Responsible for sending ip range geolocation"""
import ipaddress
from typing import Callable, Tuple, Any

from agent import ip2geo
from agent.ip2geo import logger


class Error(Exception):
    """Base Error"""


class IPGeoError(Error):
    """Error getting the IP geolocation"""


class IpRangeVisitor:
    def __init__(self) -> None:
        super().__init__()

    def dichotomy_ip_network_visit(self, ip_network: ipaddress.IPv4Network | ipaddress.IPv6Network,
                                   accept: Callable[
                                       [ipaddress.IPv4Network | ipaddress.IPv6Network], Tuple[bool, Any]]) -> Any:
        should_continue, result = accept(ip_network)
        yield result
        if should_continue is False:
            return

        subnets = list(ip_network.subnets())

        if len(subnets) == 1:
            # reached the last block.
            return

        for subnet in subnets:
            yield from self.dichotomy_ip_network_visit(subnet, accept)

    @staticmethod
    def is_first_last_ip_same_geolocation(ip_network: ipaddress.IPv4Network | ipaddress.IPv6Network
                                          ) -> Tuple[bool, Any]:
        first, last = ip_network[0], ip_network[-1]
        locator = ip2geo.Ip2GeoLocator()
        first_location = locator.get_geolocation_details(str(first))
        last_location = locator.get_geolocation_details(str(last))
        try:
            if first_location['latitude'] == last_location['latitude'] and \
                    first_location['longitude'] == last_location['longitude']:
                return False, (first_location, last_location, ip_network)
            else:
                return True, (first_location, last_location, ip_network)
        except IPGeoError as e:
            logger.warning("Error happens in is_first_last_ip_same_geolocation process", str(e))
