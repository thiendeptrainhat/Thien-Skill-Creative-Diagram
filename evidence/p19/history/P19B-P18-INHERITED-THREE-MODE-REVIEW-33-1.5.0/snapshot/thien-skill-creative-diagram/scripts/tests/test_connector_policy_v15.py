"""Focused D-105 checks for centered/even ports and straight-first routing."""
import unittest

from connector_policy_v15 import (
    CONNECTOR_POLICY_ID, centered_port, evenly_distributed_ports,
    straight_path, validate_even_ports,
)


class ConnectorPolicyTests(unittest.TestCase):
    def test_single_connector_uses_edge_center(self):
        self.assertEqual(centered_port(80, 1120), 600)

    def test_two_connectors_split_edge_into_equal_thirds(self):
        ports = evenly_distributed_ports(680, 1760, 2)
        self.assertEqual(ports, (1040, 1400))
        self.assertEqual((ports[0] - 680, ports[1] - ports[0], 1760 - ports[1]), (360, 360, 360))
        validate_even_ports(680, 1760, ports)

    def test_three_connectors_split_edge_into_equal_quarters(self):
        self.assertEqual(evenly_distributed_ports(0, 1200, 3), (300, 600, 900))

    def test_straight_route_is_minimal(self):
        self.assertEqual(straight_path((620, 152.5), (680, 152.5)), "M620 152.5 H680")
        self.assertEqual(straight_path((1040, 425), (1040, 255)), "M1040 425 V255")

    def test_policy_identity_is_stable(self):
        self.assertEqual(CONNECTOR_POLICY_ID, "D-105-centered-even-straight-first")


if __name__ == "__main__":
    unittest.main()
