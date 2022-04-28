"""Pytest fixtures for the Ip2Geo agent"""
import pathlib

import pytest
from ostorlab.agent import definitions as agent_definitions
from ostorlab.runtimes import definitions as runtime_definitions

from agent import ip2geo_agent

@pytest.fixture(scope='function', name='ip2geo_agent')
def fixture_io2geo_agent(mocker):
    mocker.patch('ostorlab.agent.mixins.agent_healthcheck_mixin.AgentHealthcheckMixin.__init__', return_value=None)
    with (pathlib.Path(__file__).parent.parent / 'ostorlab.yaml').open() as yaml_o:
        definition = agent_definitions.AgentDefinition.from_yaml(yaml_o)
        settings = runtime_definitions.AgentSettings(
            key='agent/ostorlab/ip2geo',
            bus_url='NA',
            bus_exchange_topic='NA',
            args=[],
            healthcheck_port=5301,
            redis_url='redis://guest:guest@localhost:6379')

        agent = ip2geo_agent.Ip2GeoAgent(definition, settings)
        return agent
