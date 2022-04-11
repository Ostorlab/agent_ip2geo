"""Agent responsible for finding geolocation details of ip[v4-v6] addresses."""
from typing import Any, Dict
import logging
import ipaddress

from agent import request_sender


GEO_LOCATION_FIELDS = [
    'status', 'message', 'query', 'continent', 'continentCode', 'country',
    'countryCode', 'region', 'regionName', 'city', 'zip', 'lat', 'lon', 'timezone',
    'isp', 'org', 'asname', 'mobile', 'proxy', 'hosting'
]

logger = logging.getLogger(__name__)


class Ip2GeoLocator:
    """Class responsible for detecting geolocation details of IP address."""
    def __init__(self, endpoint: str) -> None:
        """Instantiate the necessary attributes of the object

        Args:
            endpoint: to which the request will be sent.
        """
        self._endpoint = endpoint


    def _locate_ip(self, ip_address) -> Dict[str, Any]:
        """Get geolocation details of an IP address"""

        fields_params = ','.join(GEO_LOCATION_FIELDS)
        path = f'{self._endpoint}/{ip_address}?fields={fields_params}'
        response = request_sender.make_request('GET', path)
        return response


    def _parse_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse output of the geolocation request to the expected format of Ostorlab's geo-location proto message."""
        if response.get('status') == 'success':
            message = {
                'host': response.get('query'),
                'version': int(ipaddress.ip_network(response.get('query'), strict=False).version),
                'continent': response.get('continent'),
                'continent_code': response.get('continentCode'),
                'country': response.get('country'),
                'country_code': response.get('countryCode'),
                'region': response.get('region'),
                'region_name': response.get('regionName'),
                'city': response.get('city'),
                'zip': response.get('zip'),
                'latitude': response.get('lat'),
                'longitude': response.get('lon'),
                'timezone': response.get('timezone')
            }
        else:
            message = {
                'errors': response.get('message')
            }
        return message

    def get_geolocation_details(self, ip_address: str) -> Dict[str, Any]:
        """Find geolocation details of an IP address.

        Args:
            ip_address to geolocate
        Returns:
            dictionary of the geolocation details in Ostorlab's geolocation protobuff format.
        """
        response = self._locate_ip(ip_address)
        geolocation_details = self._parse_response(response)
        return geolocation_details
