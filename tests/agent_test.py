"""Unittests for the Ip2Geo Agent."""

import logging
import re

import pytest
import requests_mock as rq_mock
from ostorlab.agent.message import message
from pytest_mock import plugin

from agent import ip2geo_agent as ip2geo_agt


def testAgentIp2Geo_whenLocatesIpAddress_emitsBackFindings(
    ip2geo_agent: ip2geo_agt.Ip2GeoAgent,
    agent_mock: list[message.Message],
    agent_persist_mock: dict[str | bytes, str | bytes],
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


def testAgentIp2Geo_whenIpIsHosted_emitsIspAndNetworkFlags(
    ip2geo_agent: ip2geo_agt.Ip2GeoAgent,
    agent_mock: list[message.Message],
    agent_persist_mock: dict[str | bytes, str | bytes],
    requests_mock: rq_mock.mocker.Mocker,
) -> None:
    del agent_persist_mock
    requests_mock.get(
        re.compile("http://ip-api.com/json/"),
        json={
            "query": "50.16.16.211",
            "status": "success",
            "countryCode": "US",
            "isp": "Amazon.com, Inc.",
            "org": "AWS EC2 (us-east-1)",
            "mobile": False,
            "proxy": False,
            "hosting": True,
        },
        status_code=200,
    )
    msg = message.Message.from_data(
        selector="v3.asset.ip.v4", data={"host": "50.16.16.211", "version": 4}
    )

    ip2geo_agent.process(msg)

    assert agent_mock[0].data["isp"] == "Amazon.com, Inc."
    assert agent_mock[0].data["org"] == "AWS EC2 (us-east-1)"
    assert agent_mock[0].data["mobile"] is False
    assert agent_mock[0].data["proxy"] is False
    assert agent_mock[0].data["hosting"] is True


def testAgentIp2Geo_whenIpAddressHasAlreadyBeenProcessed_shouldSkip(
    ip2geo_agent: ip2geo_agt.Ip2GeoAgent,
    agent_mock: list[message.Message],
    agent_persist_mock: dict[str | bytes, str | bytes],
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
    agent_mock: list[message.Message],
    agent_persist_mock: dict[str | bytes, str | bytes],
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


def testAgentIp2Geo_whenSingleIpAddress_sendsOneGeolocationRequest(
    ip2geo_agent: ip2geo_agt.Ip2GeoAgent,
    agent_mock: list[message.Message],
    agent_persist_mock: dict[str | bytes, str | bytes],
    requests_mock: rq_mock.mocker.Mocker,
) -> None:
    """A network with a single address must be looked up once, not once per extreme."""
    del agent_persist_mock
    requests_mock.get(
        re.compile("http://ip-api.com/json/"),
        json={
            "query": "76.76.2.0",
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
        selector="v3.asset.ip.v4",
        data={"host": "76.76.2.0", "mask": "32", "version": 4},
    )

    ip2geo_agent.process(msg)

    assert requests_mock.call_count == 1
    assert len(agent_mock) == 1
    assert agent_mock[0].data["host"] == "76.76.2.0"
    assert agent_mock[0].data["country_code"] == "CA"
    assert agent_mock[0].data["latitude"] == pytest.approx(45.4995)


def testAgentIp2Geo_whenIpAlreadyProcessed_doesNotSendGeolocationRequest(
    ip2geo_agent: ip2geo_agt.Ip2GeoAgent,
    agent_mock: list[message.Message],
    agent_persist_mock: dict[str | bytes, str | bytes],
    requests_mock: rq_mock.mocker.Mocker,
) -> None:
    """An IP received again under another selector must not be looked up again."""
    del agent_persist_mock
    requests_mock.get(
        re.compile("http://ip-api.com/json/"),
        json={
            "query": "8.8.8.8",
            "status": "success",
            "countryCode": "CA",
            "lat": 45.4995,
            "lon": -73.5848,
        },
        status_code=200,
    )

    ip2geo_agent.process(
        message.Message.from_data(
            selector="v3.asset.ip.v4", data={"host": "8.8.8.8", "version": 4}
        )
    )
    ip2geo_agent.process(
        message.Message.from_data(
            selector="v3.asset.ip.v4.whois", data={"host": "8.8.8.8", "version": 4}
        )
    )

    assert requests_mock.call_count == 1
    assert len(agent_mock) == 1


def testAgentIp2Geo_whenMessageIsOwnGeolocationOutput_skipsWithoutRequest(
    ip2geo_agent: ip2geo_agt.Ip2GeoAgent,
    agent_mock: list[message.Message],
    agent_persist_mock: dict[str | bytes, str | bytes],
    requests_mock: rq_mock.mocker.Mocker,
) -> None:
    """The agent must not reprocess the geolocation messages it emits."""
    del agent_persist_mock
    requests_mock.get(re.compile("http://ip-api.com/json/"), json={}, status_code=200)

    ip2geo_agent.process(
        message.Message.from_data(
            selector="v3.asset.ip.v4.geolocation",
            data={"host": "8.8.4.4", "version": 4},
        )
    )

    assert requests_mock.call_count == 0
    assert len(agent_mock) == 0


def testAgentIp2Geo_whenGeolocationApiRateLimits_logsWarning(
    ip2geo_agent: ip2geo_agt.Ip2GeoAgent,
    agent_mock: list[message.Message],
    agent_persist_mock: dict[str | bytes, str | bytes],
    requests_mock: rq_mock.mocker.Mocker,
    mocker: plugin.MockerFixture,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A lookup that fails with an HTTP error must log a warning instead of silently dropping the IP."""
    del agent_persist_mock
    mocker.patch("agent.request_sender.make_request.retry.sleep")
    requests_mock.get(
        re.compile("http://ip-api.com/json/"), status_code=429, reason="Too Many"
    )

    with caplog.at_level(logging.WARNING):
        ip2geo_agent.process(
            message.Message.from_data(
                selector="v3.asset.ip.v4", data={"host": "8.8.8.8", "version": 4}
            )
        )

    assert len(agent_mock) == 0
    assert any(
        record.levelno == logging.WARNING and "8.8.8.8" in record.getMessage()
        for record in caplog.records
    )
