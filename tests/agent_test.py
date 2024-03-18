"""Unittests for the Ip2Geo Agent."""

import re
import pytest
from typing import List, Dict, Union

from ostorlab.agent.message import message
import requests_mock as rq_mock

from agent import ip2geo_agent as ip2geo_agt


def testAgentIp2Geo_whenLocatesIpAddress_emitsBackFindings(
    ip2geo_agent: ip2geo_agt.Ip2GeoAgent,
    agent_mock: List[message.Message],
    agent_persist_mock: Dict[Union[str, bytes], Union[str, bytes]],
    requests_mock: rq_mock.mocker.Mocker,
) -> None:
    """Unittest for emitting back the geolocation details found by the Ip2Geo agent."""
    del agent_persist_mock
    matcher = re.compile("http://ip-api.com/json/")
    requests_mock.get(
        matcher,
        json={
            "query": "8.8.8.8",
            "status": "success",
            "country": "Canada",
            "countryCode": "CA",
            "lat": 45.4995,
            "lon": -73.5848,
            "timezone": "America/Toronto",
        },
        status_code=200,
    )

    msg = message.Message.from_data(
        selector="v3.asset.ip.v4", data={"host": "8.8.8.8", "version": 4}
    )
    ip2geo_agent.process(msg)

    assert len(agent_mock) == 1
    assert agent_mock[0].selector == "v3.asset.ip.v4.geolocation"
    assert agent_mock[0].data["longitude"] == pytest.approx(-73.5848)
    assert agent_mock[0].data["country_code"] == "CA"


def testAgentIp2Geo_whenIpAddressHasAlreadyBeenProcessed_shouldSkip(
    ip2geo_agent: ip2geo_agt.Ip2GeoAgent,
    agent_mock: List[message.Message],
    agent_persist_mock: Dict[Union[str, bytes], Union[str, bytes]],
    requests_mock: rq_mock.mocker.Mocker,
) -> None:
    """Unittest for Ip2Geo Agent, when it receives an ip address that has already been processed,
    the agent should skip it.
    """

    del agent_persist_mock
    matcher = re.compile("http://ip-api.com/json/")
    requests_mock.get(
        matcher,
        json={
            "query": "8.8.8.8",
            "status": "success",
            "country": "Canada",
            "countryCode": "CA",
            "lat": 45.4995,
            "lon": -73.5848,
            "timezone": "America/Toronto",
        },
        status_code=200,
    )

    msg = message.Message.from_data(
        selector="v3.asset.ip.v4", data={"host": "8.8.8.0", "mask": "24", "version": 4}
    )
    ip2geo_agent.process(msg)

    assert len(agent_mock) == 256


def testAgentIp2Geo_whenIpAddressHasHostBits_shouldSkip(
    ip2geo_agent: ip2geo_agt.Ip2GeoAgent,
    agent_mock: List[message.Message],
    agent_persist_mock: Dict[Union[str, bytes], Union[str, bytes]],
    requests_mock: rq_mock.mocker.Mocker,
) -> None:
    """Unittest for Ip2Geo Agent, when it receives an ip address that has already been processed,
    the agent should skip it.
    """

    del agent_persist_mock
    matcher = re.compile("http://ip-api.com/json/")
    requests_mock.get(
        matcher,
        json={
            "query": "8.8.8.8",
            "status": "success",
            "country": "Canada",
            "countryCode": "CA",
            "lat": 45.4995,
            "lon": -73.5848,
            "timezone": "America/Toronto",
        },
        status_code=200,
    )

    msg = message.Message.from_data(
        selector="v3.asset.ip.v4", data={"host": "8.8.8.8", "mask": "24", "version": 4}
    )
    ip2geo_agent.process(msg)

    assert len(agent_mock) == 256
