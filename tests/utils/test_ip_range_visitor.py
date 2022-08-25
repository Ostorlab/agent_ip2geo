import ipaddress

from agent.utils import ip_range_visitor


def testVistor_withMatchingIP_returnsLocations():
    for result in ip_range_visitor.dichotomy_ip_network_visit(ipaddress.ip_network('8.8.8.0/22'), ip_range_visitor.is_first_last_ip_same_geolocation):
        print(result)