"""Unittests for the IP range visitor."""

import ipaddress

from agent.utils import ip_range_visitor


def testVistor_withMatchingIPAndMaskRecieved_returnsLocations():
    results = []
    for result in ip_range_visitor.dichotomy_ip_network_visit(ipaddress.ip_network('8.8.8.0/22'),
                    ip_range_visitor.is_first_last_ip_same_geolocation):
        results.append(result)

    assert all(len(result) == 3 and result[0] != result[1] for result in results)


def testVistor_withMatchingIPAndMaskNotRecieved_returnsLocation():
    for result in ip_range_visitor.dichotomy_ip_network_visit(ipaddress.ip_network('8.8.8.0/32'),
                    ip_range_visitor.is_first_last_ip_same_geolocation):
        assert result[0] == result[1]

