"""Unittests for the IP range visitor."""

import ipaddress
import re

from agent import ip2geo
from agent.utils.ip_range_visitor import IpRangeVisitor
import requests_mock as rq_mock

ip_range_visitor = IpRangeVisitor()


def testVistor_withMatchingIPAndMaskRecieved_returnsLocations() -> None:
    results = []
    for result in ip_range_visitor.dichotomy_ip_network_visit(
        ipaddress.ip_network("8.8.8.0/22"),
        ip_range_visitor.is_first_last_ip_same_geolocation,
    ):
        results.append(result[0:2])

    assert results == [
        (
            {
                "host": "8.8.8.0",
                "version": 4,
                "continent": "North America",
                "continent_code": "NA",
                "country": "United States",
                "country_code": "US",
                "region": "CA",
                "region_name": "California",
                "city": "Mountain View",
                "zip": "94043",
                "latitude": 37.4223,
                "longitude": -122.085,
                "timezone": "America/Los_Angeles",
            },
            {
                "host": "8.8.11.255",
                "version": 4,
                "continent": "North America",
                "continent_code": "NA",
                "country": "United States",
                "country_code": "US",
                "region": "LA",
                "region_name": "Louisiana",
                "city": "Monroe",
                "zip": "71203",
                "latitude": 32.5896,
                "longitude": -92.0669,
                "timezone": "America/Chicago",
            },
        ),
        (
            {
                "host": "8.8.8.0",
                "version": 4,
                "continent": "North America",
                "continent_code": "NA",
                "country": "United States",
                "country_code": "US",
                "region": "CA",
                "region_name": "California",
                "city": "Mountain View",
                "zip": "94043",
                "latitude": 37.4223,
                "longitude": -122.085,
                "timezone": "America/Los_Angeles",
            },
            {
                "host": "8.8.9.255",
                "version": 4,
                "continent": "North America",
                "continent_code": "NA",
                "country": "United States",
                "country_code": "US",
                "region": "FL",
                "region_name": "Florida",
                "city": "Fort Lauderdale",
                "zip": "33309",
                "latitude": 26.2018,
                "longitude": -80.1699,
                "timezone": "America/New_York",
            },
        ),
        (
            {
                "host": "8.8.8.0",
                "version": 4,
                "continent": "North America",
                "continent_code": "NA",
                "country": "United States",
                "country_code": "US",
                "region": "CA",
                "region_name": "California",
                "city": "Mountain View",
                "zip": "94043",
                "latitude": 37.4223,
                "longitude": -122.085,
                "timezone": "America/Los_Angeles",
            },
            {
                "host": "8.8.8.255",
                "version": 4,
                "continent": "North America",
                "continent_code": "NA",
                "country": "United States",
                "country_code": "US",
                "region": "CA",
                "region_name": "California",
                "city": "Mountain View",
                "zip": "94043",
                "latitude": 37.4223,
                "longitude": -122.085,
                "timezone": "America/Los_Angeles",
            },
        ),
        (
            {
                "host": "8.8.9.0",
                "version": 4,
                "continent": "North America",
                "continent_code": "NA",
                "country": "United States",
                "country_code": "US",
                "region": "FL",
                "region_name": "Florida",
                "city": "Fort Lauderdale",
                "zip": "33309",
                "latitude": 26.2018,
                "longitude": -80.1699,
                "timezone": "America/New_York",
            },
            {
                "host": "8.8.9.255",
                "version": 4,
                "continent": "North America",
                "continent_code": "NA",
                "country": "United States",
                "country_code": "US",
                "region": "FL",
                "region_name": "Florida",
                "city": "Fort Lauderdale",
                "zip": "33309",
                "latitude": 26.2018,
                "longitude": -80.1699,
                "timezone": "America/New_York",
            },
        ),
        (
            {
                "host": "8.8.10.0",
                "version": 4,
                "continent": "North America",
                "continent_code": "NA",
                "country": "United States",
                "country_code": "US",
                "region": "DC",
                "region_name": "District of Columbia",
                "city": "Washington",
                "zip": "20068",
                "latitude": 38.9072,
                "longitude": -77.0369,
                "timezone": "America/New_York",
            },
            {
                "host": "8.8.11.255",
                "version": 4,
                "continent": "North America",
                "continent_code": "NA",
                "country": "United States",
                "country_code": "US",
                "region": "LA",
                "region_name": "Louisiana",
                "city": "Monroe",
                "zip": "71203",
                "latitude": 32.5896,
                "longitude": -92.0669,
                "timezone": "America/Chicago",
            },
        ),
        (
            {
                "host": "8.8.10.0",
                "version": 4,
                "continent": "North America",
                "continent_code": "NA",
                "country": "United States",
                "country_code": "US",
                "region": "DC",
                "region_name": "District of Columbia",
                "city": "Washington",
                "zip": "20068",
                "latitude": 38.9072,
                "longitude": -77.0369,
                "timezone": "America/New_York",
            },
            {
                "host": "8.8.10.255",
                "version": 4,
                "continent": "North America",
                "continent_code": "NA",
                "country": "United States",
                "country_code": "US",
                "region": "DC",
                "region_name": "District of Columbia",
                "city": "Washington",
                "zip": "20068",
                "latitude": 38.9072,
                "longitude": -77.0369,
                "timezone": "America/New_York",
            },
        ),
        (
            {
                "host": "8.8.11.0",
                "version": 4,
                "continent": "North America",
                "continent_code": "NA",
                "country": "United States",
                "country_code": "US",
                "region": "LA",
                "region_name": "Louisiana",
                "city": "Monroe",
                "zip": "71203",
                "latitude": 32.5896,
                "longitude": -92.0669,
                "timezone": "America/Chicago",
            },
            {
                "host": "8.8.11.255",
                "version": 4,
                "continent": "North America",
                "continent_code": "NA",
                "country": "United States",
                "country_code": "US",
                "region": "LA",
                "region_name": "Louisiana",
                "city": "Monroe",
                "zip": "71203",
                "latitude": 32.5896,
                "longitude": -92.0669,
                "timezone": "America/Chicago",
            },
        ),
    ]


def testVistor_withMaskNotRecieved_returnsIfFirstIPGeolocationEqualLastIPGeolocation() -> (
    None
):
    for result in ip_range_visitor.dichotomy_ip_network_visit(
        ipaddress.ip_network("8.8.8.0/32"),
        ip_range_visitor.is_first_last_ip_same_geolocation,
    ):
        assert result[0] == result[1]


def testIsFirstLastIPSameGeolocation_withNoneLatAndLon_returnsTupleTrueNone(
    requests_mock: rq_mock.mocker.Mocker,
) -> None:
    matcher = re.compile("http://ip-api.com/json/")
    requests_mock.get(
        matcher,
        json={
            "query": "8.8.8.8",
            "status": "success",
            "country": "Canada",
            "countryCode": "CA",
            "lat": None,
            "lon": None,
            "timezone": "America/Toronto",
        },
        status_code=200,
    )
    same_geo_location_mocker = ip_range_visitor.is_first_last_ip_same_geolocation(
        ipaddress.ip_network("8.8.8.0/32")
    )

    assert same_geo_location_mocker[0] is True
    assert same_geo_location_mocker[1][1]["latitude"] is None
    assert same_geo_location_mocker[1][1]["longitude"] is None


def testVistor_withLocatorReturnsNone_returnsIfFirstIPGeolocationEqualLastIPGeolocation(
    requests_mock: rq_mock.mocker.Mocker,
) -> None:
    fields_params = ",".join(ip2geo.GEO_LOCATION_FIELDS)
    requests_mock.get(
        f"http://ip-api.com/json//199.102.178.251?fields={fields_params}",
        status_code=200,
        json={"errors": "Too many calls"},
    )
    for result in ip_range_visitor.dichotomy_ip_network_visit(
        ipaddress.ip_network("199.102.178.251/32"),
        ip_range_visitor.is_first_last_ip_same_geolocation,
    ):
        assert result[0] is None
