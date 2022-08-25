"""Agent implementation for Ip2Geo : Detecting geolocation details of an IP address."""
import logging
import ipaddress

from rich import logging as rich_logging
from ostorlab.agent import agent
from ostorlab.agent import message as m
from ostorlab.agent.mixins import agent_persist_mixin
from ostorlab.agent import definitions as agent_definitions
from ostorlab.runtimes import definitions as runtime_definitions
from agent import ip2geo

logging.basicConfig(
    format='%(message)s',
    datefmt='[%X]',
    handlers=[rich_logging.RichHandler(rich_tracebacks=True)],
    level='INFO',
    force=True
)
logger = logging.getLogger(__name__)

GEO_LOCATION_API_ENDPOINT = 'http://ip-api.com/json/'
STORAGE_NAME = 'agent_ipgeo_storage'


def _is_same_geolocation(hosts):
    ip_geo_locator = ip2geo.Ip2GeoLocator(GEO_LOCATION_API_ENDPOINT)

    geolocation_details_first = ip_geo_locator.get_geolocation_details(str(hosts[0]))
    if 'errors' in geolocation_details_first:
        logger.info('skipping %s : %s', str(hosts[0]), geolocation_details_first['errors'])

    geolocation_details_last = ip_geo_locator.get_geolocation_details(str(hosts[-1]))
    if 'errors' in geolocation_details_last:
        logger.info('skipping %s : %s', str(hosts[-1]), geolocation_details_last['errors'])

    return geolocation_details_last == geolocation_details_first


class Ip2GeoAgent(agent.Agent, agent_persist_mixin.AgentPersistMixin):
    """Ip2Geo agent implementation."""

    def __init__(self,
                 agent_definition: agent_definitions.AgentDefinition,
                 agent_settings: runtime_definitions.AgentSettings) -> None:

        agent.Agent.__init__(self, agent_definition, agent_settings)
        agent_persist_mixin.AgentPersistMixin.__init__(self, agent_settings)

    def _send_range(self, hosts, message: m.Message):
        ip_geo_locator = ip2geo.Ip2GeoLocator(GEO_LOCATION_API_ENDPOINT)
        response = ip_geo_locator.locate_ip(str(hosts[0]))
        for host in hosts:
            response['host'] = str(host)
            geolocation_details = ip_geo_locator.parse_response(response)
            out_selector = f'{message.selector}.geolocation'
            self.emit(selector=out_selector, data=geolocation_details)

    def _classify_ips_geolocation(self, network: ipaddress, message: m.Message):
        if self.set_add(STORAGE_NAME, network) is True:
            if self.is_same_geo(list(network.hosts())):
                self.send_range(list(network.hosts()))
            #     I still confused
            if network.num_addresses == 1:
                return
            else:
                self._classify_ips_geolocation(network.subnets()[0], message)
                self._classify_ips_geolocation(network.subnets()[-1], message)

    def process(self, message: m.Message) -> None:
        """Process messages of type v3.asset.ip.v[4/6] and emits back the geolocation details.

        Args:
            message: The received message.
        """
        logger.info('processing message of selector : %s', message.selector)
        ip_address = message.data['host']
        if message.data['mask'] is None:
            if self.set_add(STORAGE_NAME, ip_address) is True:
                ip_geo_locator = ip2geo.Ip2GeoLocator(GEO_LOCATION_API_ENDPOINT)
                geolocation_details = ip_geo_locator.get_geolocation_details(ip_address)

                if 'errors' in geolocation_details:
                    logger.info('skipping %s : %s', ip_address, geolocation_details['errors'])
                else:
                    out_selector = f'{message.selector}.geolocation'
                    self.emit(selector=out_selector, data=geolocation_details)
            else:
                logger.info('%s has already been processed. skipping for now.', ip_address)
        else:
            network = ipaddress.ip_network(f"{message.data.get('host')}/{message.data.get('mask')}")
            if self.set_add(STORAGE_NAME, network) is True:
                self._classify_ips_geolocation(network, message, )
            else:
                logger.info('%s has already been processed. skipping for now.', network)


if __name__ == '__main__':
    logger.info('starting agent ...')
    Ip2GeoAgent.main()
