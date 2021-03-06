"""Unittests for the Ip2Geo Agent."""
import re
import pytest

from ostorlab.agent import message


def testAgentIp2Geo_whenLocatesIpAddress_emitsBackFindings(ip2geo_agent, agent_mock, agent_persist_mock, requests_mock):
    """Unittest for emitting back the geolocation details found by the Ip2Geo agent."""
    del agent_persist_mock
    matcher = re.compile('http://ip-api.com/json/')
    requests_mock.get(
        matcher,
        json={
            'query': '8.8.8.8',
            'status': 'success',
            'country': 'Canada',
            'countryCode': 'CA',
            'lat': 45.4995,
            'lon': -73.5848,
            'timezone': 'America/Toronto'
        },
        status_code=200
    )

    msg = message.Message.from_data(selector='v3.asset.ip.v4', data={'host': '8.8.8.8', 'version':4})
    ip2geo_agent.process(msg)

    assert len(agent_mock) == 1
    assert agent_mock[0].selector =='v3.asset.ip.v4.geolocation'
    assert agent_mock[0].data['longitude'] ==  pytest.approx(-73.5848)
    assert agent_mock[0].data['country_code'] == 'CA'


def testAgentIp2Geo_whenIpAddressIsInvalid_shouldSkip(ip2geo_agent,
                                                      agent_mock,
                                                      agent_persist_mock,
                                                      requests_mock):
    """Unittest for Ip2Geo Agent, when it receives an invalid ip address, the agent should skip it."""
    del agent_persist_mock
    matcher = re.compile('http://ip-api.com/json/')
    requests_mock.get(
        matcher,
        json={
            'query': '8.8.',
            'status': 'fail',
            'message': 'query is in wrong format.'
        },
        status_code=200
    )

    msg = message.Message.from_data(selector='v3.asset.ip.v4', data={'host': '8.8.', 'version':4})
    ip2geo_agent.process(msg)

    assert len(agent_mock) == 0


def testAgentIp2Geo_whenIpAddressHasAlreadyBeenProcessed_shouldSkip(ip2geo_agent,
                                                                    agent_mock,
                                                                    agent_persist_mock,
                                                                    requests_mock):
    """Unittest for Ip2Geo Agent, when it receives an ip address that has already been processed,
       the agent should skip it.
    """

    del agent_persist_mock
    matcher = re.compile('http://ip-api.com/json/')
    requests_mock.get(
        matcher,
        json={
            'query': '8.8.8.8',
            'status': 'success',
            'country': 'Canada',
            'countryCode': 'CA',
            'lat': 45.4995,
            'lon': -73.5848,
            'timezone': 'America/Toronto'
        },
        status_code=200
    )

    msg = message.Message.from_data(selector='v3.asset.ip.v4', data={'host': '8.8.', 'version':4})
    ip2geo_agent.process(msg)
    ip2geo_agent.process(msg)

    assert len(agent_mock) == 1
