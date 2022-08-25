"""Agent implementation for Ip2Geo : Detecting geolocation details of an IP address."""
import logging

from ostorlab.agent import agent
from ostorlab.agent import definitions as agent_definitions
from ostorlab.agent import message as m
from ostorlab.agent.mixins import agent_persist_mixin
from ostorlab.runtimes import definitions as runtime_definitions
from rich import logging as rich_logging

from agent import ip2geo

logging.basicConfig(
    format='%(message)s',
    datefmt='[%X]',
    handlers=[rich_logging.RichHandler(rich_tracebacks=True)],
    level='INFO',
    force=True
)
logger = logging.getLogger(__name__)

STORAGE_NAME = 'agent_ipgeo_storage'


class Ip2GeoAgent(agent.Agent, agent_persist_mixin.AgentPersistMixin):
    """Ip2Geo agent implementation."""

    def __init__(self,
                 agent_definition: agent_definitions.AgentDefinition,
                 agent_settings: runtime_definitions.AgentSettings) -> None:

        agent.Agent.__init__(self, agent_definition, agent_settings)
        agent_persist_mixin.AgentPersistMixin.__init__(self, agent_settings)

    def process(self, message: m.Message) -> None:
        """Process messages of type v3.asset.ip.v[4/6] and emits back the geolocation details.

        Args:
            message: The received message.
        """
        logger.info('processing message of selector : %s', message.selector)
        ip_address = message.data['host']
        if self.set_add(STORAGE_NAME, ip_address) is True:
            ip_geo_locator = ip2geo.Ip2GeoLocator()
            geolocation_details = ip_geo_locator.get_geolocation_details(ip_address)

            if 'errors' in geolocation_details:
                logger.info('skipping %s : %s', ip_address, geolocation_details['errors'])
            else:
                out_selector = f'{message.selector}.geolocation'
                self.emit(selector=out_selector, data=geolocation_details)
        else:
            logger.info('%s has already been processed. skipping for now.', ip_address)


if __name__ == '__main__':
    logger.info('starting agent ...')
    Ip2GeoAgent.main()
