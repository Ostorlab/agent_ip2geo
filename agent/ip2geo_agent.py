"""Agent implementation for Ip2Geo : Detecting geolocation details of an IP address."""
import logging
import ipaddress

from ostorlab.agent import agent
from ostorlab.agent import definitions as agent_definitions
from ostorlab.agent import message as m
from ostorlab.agent.mixins import agent_persist_mixin
from ostorlab.runtimes import definitions as runtime_definitions
from rich import logging as rich_logging
from agent.utils.ip_range_visitor import IpRangeVisitor

logging.basicConfig(
    format='%(message)s',
    datefmt='[%X]',
    handlers=[rich_logging.RichHandler(rich_tracebacks=True)],
    level='INFO',
    force=True
)
logger = logging.getLogger(__name__)

STORAGE_NAME = b'agent_ipgeo_storage'


class Ip2GeoAgent(agent.Agent, agent_persist_mixin.AgentPersistMixin):
    """Ip2Geo agent implementation."""

    def __init__(self,
                 agent_definition: agent_definitions.AgentDefinition,
                 agent_settings: runtime_definitions.AgentSettings,
                 ) -> None:

        agent.Agent.__init__(self, agent_definition, agent_settings)
        agent_persist_mixin.AgentPersistMixin.__init__(self, agent_settings)
        self.ip_range_visitor = IpRangeVisitor()

    def process(self, message: m.Message) -> None:
        """Process messages of type v3.asset.ip.v[4/6] and emits back the geolocation details.

        Args:
            message: The received message.
        """
        logger.info('processing message of selector : %s', message.selector)

        ip = message.data['host']
        mask = message.data.get('mask')
        version = message.data.get('version')

        out_selector = 'v3.asset.ip.v6.geolocation' if version == 6 else 'v3.asset.ip.v4.geolocation'
        network = ipaddress.ip_network(f'{ip}/{mask}') if mask is not None else ipaddress.ip_network(f'{ip}')

        # classify ip range based on geolocation
        for result in self.ip_range_visitor.dichotomy_ip_network_visit(
                network, self.ip_range_visitor.is_first_last_ip_same_geolocation):

            geolocation_details = result[0]
            geolocation_network = result[2]
            for ip in geolocation_network:
                # check if ip not tested before
                if self.add_ip_network(STORAGE_NAME, ipaddress.ip_network(ip)) is True:
                    # create geolocation details dict for each ip and emit it
                    geolocation_details['host'] = str(ip)
                    self.emit(selector=out_selector, data=geolocation_details)
                else:
                    logger.info('%s has already been processed. skipping for now.', ip)


if __name__ == '__main__':
    logger.info('starting agent ...')
    Ip2GeoAgent.main()
