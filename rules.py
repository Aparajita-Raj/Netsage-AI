"""
NetSage AI - Deterministic Network Rule Checker

This module checks common Cisco/network configuration problems
without using an AI model.

The goal is to detect problems that can be proven using rules.
"""

import ipaddress
import re
from typing import Any


# ============================================================
# 1. DUPLICATE IP CHECK
# ============================================================

def check_duplicate_ips(ip_addresses: list[str]) -> dict[str, Any]:
    """
    Check whether the same IP address appears more than once.
    """

    cleaned_ips = [ip.strip() for ip in ip_addresses if ip.strip()]

    duplicates = []

    for ip in set(cleaned_ips):
        if cleaned_ips.count(ip) > 1:
            duplicates.append(ip)

    if duplicates:
        return {
            "rule": "DUPLICATE_IP",
            "status": "FAIL",
            "severity": "HIGH",
            "message": f"Duplicate IP address detected: {', '.join(duplicates)}",
            "evidence": duplicates,
        }

    return {
        "rule": "DUPLICATE_IP",
        "status": "PASS",
        "severity": "LOW",
        "message": "No duplicate IP addresses detected.",
        "evidence": [],
    }


# ============================================================
# 2. SUBNET / MASK CHECK
# ============================================================

def check_subnet(
    ip_address: str,
    subnet_mask: str,
    gateway: str | None = None,
) -> dict[str, Any]:
    """
    Check whether the IP, subnet mask and gateway are logically valid.
    """

    try:
        interface = ipaddress.IPv4Interface(
            f"{ip_address}/{subnet_mask}"
        )
    except ValueError as error:
        return {
            "rule": "SUBNET_CHECK",
            "status": "FAIL",
            "severity": "HIGH",
            "message": f"Invalid IP/subnet configuration: {error}",
            "evidence": [ip_address, subnet_mask],
        }

    result = {
        "rule": "SUBNET_CHECK",
        "status": "PASS",
        "severity": "LOW",
        "message": "IP address and subnet mask are valid.",
        "evidence": [
            f"IP: {ip_address}",
            f"Mask: {subnet_mask}",
            f"Network: {interface.network}",
        ],
    }

    if gateway:
        try:
            gateway_ip = ipaddress.IPv4Address(gateway)

            if gateway_ip not in interface.network:
                result = {
                    "rule": "SUBNET_CHECK",
                    "status": "FAIL",
                    "severity": "HIGH",
                    "message": (
                        f"Gateway {gateway} is outside the "
                        f"host subnet {interface.network}."
                    ),
                    "evidence": [
                        f"Host: {ip_address}/{subnet_mask}",
                        f"Gateway: {gateway}",
                        f"Network: {interface.network}",
                    ],
                }

        except ValueError:
            return {
                "rule": "SUBNET_CHECK",
                "status": "FAIL",
                "severity": "HIGH",
                "message": f"Invalid gateway address: {gateway}",
                "evidence": [gateway],
            }

    return result


# ============================================================
# 3. GATEWAY CHECK
# ============================================================

def check_gateway(
    host_ip: str,
    subnet_mask: str,
    gateway: str,
) -> dict[str, Any]:
    """
    Check whether the default gateway belongs to the same subnet
    as the host.
    """

    try:
        network = ipaddress.IPv4Network(
            f"{host_ip}/{subnet_mask}",
            strict=False,
        )

        gateway_ip = ipaddress.IPv4Address(gateway)

    except ValueError as error:
        return {
            "rule": "GATEWAY_CHECK",
            "status": "FAIL",
            "severity": "HIGH",
            "message": f"Invalid network configuration: {error}",
            "evidence": [],
        }

    if gateway_ip not in network:
        return {
            "rule": "GATEWAY_CHECK",
            "status": "FAIL",
            "severity": "HIGH",
            "message": (
                f"Gateway {gateway} does not belong to "
                f"host network {network}."
            ),
            "evidence": [
                f"Host IP: {host_ip}",
                f"Subnet: {network}",
                f"Gateway: {gateway}",
            ],
        }

    return {
        "rule": "GATEWAY_CHECK",
        "status": "PASS",
        "severity": "LOW",
        "message": "Gateway belongs to the host subnet.",
        "evidence": [
            f"Host IP: {host_ip}",
            f"Subnet: {network}",
            f"Gateway: {gateway}",
        ],
    }


# ============================================================
# 4. INTERFACE STATUS CHECK
# ============================================================

def check_interface_status(
    interface_name: str,
    status: str,
) -> dict[str, Any]:
    """
    Check whether a network interface is operational.
    """

    normalized_status = status.lower().strip()

    down_states = [
        "down",
        "administratively down",
        "disabled",
        "shutdown",
    ]

    if normalized_status in down_states:
        return {
            "rule": "INTERFACE_STATUS",
            "status": "FAIL",
            "severity": "HIGH",
            "message": (
                f"Interface {interface_name} is not operational."
            ),
            "evidence": [
                f"Interface: {interface_name}",
                f"Status: {status}",
            ],
        }

    return {
        "rule": "INTERFACE_STATUS",
        "status": "PASS",
        "severity": "LOW",
        "message": (
            f"Interface {interface_name} appears to be operational."
        ),
        "evidence": [
            f"Interface: {interface_name}",
            f"Status: {status}",
        ],
    }


# ============================================================
# 5. VLAN CHECK
# ============================================================

def check_vlan(
    expected_vlan: int,
    actual_vlan: int | None,
    available_vlans: list[int] | None = None,
) -> dict[str, Any]:
    """
    Check VLAN existence and interface VLAN assignment.
    """

    if available_vlans is not None:
        if expected_vlan not in available_vlans:
            return {
                "rule": "VLAN_CHECK",
                "status": "FAIL",
                "severity": "HIGH",
                "message": (
                    f"Expected VLAN {expected_vlan} "
                    f"does not exist."
                ),
                "evidence": [
                    f"Expected VLAN: {expected_vlan}",
                    f"Available VLANs: {available_vlans}",
                ],
            }

    if actual_vlan is None:
        return {
            "rule": "VLAN_CHECK",
            "status": "FAIL",
            "severity": "HIGH",
            "message": (
                f"Interface is not assigned to VLAN "
                f"{expected_vlan}."
            ),
            "evidence": [
                f"Expected VLAN: {expected_vlan}",
                "Actual VLAN: None",
            ],
        }

    if actual_vlan != expected_vlan:
        return {
            "rule": "VLAN_CHECK",
            "status": "FAIL",
            "severity": "HIGH",
            "message": (
                f"VLAN mismatch. Expected VLAN "
                f"{expected_vlan}, but found VLAN {actual_vlan}."
            ),
            "evidence": [
                f"Expected VLAN: {expected_vlan}",
                f"Actual VLAN: {actual_vlan}",
            ],
        }

    return {
        "rule": "VLAN_CHECK",
        "status": "PASS",
        "severity": "LOW",
        "message": (
            f"Interface is correctly assigned to VLAN "
            f"{expected_vlan}."
        ),
        "evidence": [
            f"Expected VLAN: {expected_vlan}",
            f"Actual VLAN: {actual_vlan}",
        ],
    }


# ============================================================
# 6. ROUTE CHECK
# ============================================================

def check_route(
    destination_network: str,
    routing_table: list[str],
) -> dict[str, Any]:
    """
    Check whether a destination network exists in the routing table.
    """

    destination = destination_network.strip()

    normalized_routes = [
        route.strip()
        for route in routing_table
        if route.strip()
    ]

    if destination not in normalized_routes:
        return {
            "rule": "ROUTE_CHECK",
            "status": "FAIL",
            "severity": "HIGH",
            "message": (
                f"No route found for destination "
                f"{destination}."
            ),
            "evidence": [
                f"Destination: {destination}",
                f"Routing table: {normalized_routes}",
            ],
        }

    return {
        "rule": "ROUTE_CHECK",
        "status": "PASS",
        "severity": "LOW",
        "message": (
            f"Route to {destination} exists."
        ),
        "evidence": [
            f"Destination: {destination}",
        ],
    }


# ============================================================
# RUN ALL RULES
# ============================================================

def run_all_checks(case_data: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Run whichever checks have data available.

    This function allows us to send a case to the rule engine
    without requiring every possible field.
    """

    results = []

    # Duplicate IP check
    if "ip_addresses" in case_data:
        results.append(
            check_duplicate_ips(case_data["ip_addresses"])
        )

    # Subnet check
    if (
        "ip_address" in case_data
        and "subnet_mask" in case_data
    ):
        results.append(
            check_subnet(
                case_data["ip_address"],
                case_data["subnet_mask"],
                case_data.get("gateway"),
            )
        )

    # Gateway check
    if (
        "host_ip" in case_data
        and "subnet_mask" in case_data
        and "gateway" in case_data
    ):
        results.append(
            check_gateway(
                case_data["host_ip"],
                case_data["subnet_mask"],
                case_data["gateway"],
            )
        )

    # Interface check
    if (
        "interface_name" in case_data
        and "interface_status" in case_data
    ):
        results.append(
            check_interface_status(
                case_data["interface_name"],
                case_data["interface_status"],
            )
        )

    # VLAN check
    if "expected_vlan" in case_data:
        results.append(
            check_vlan(
                case_data["expected_vlan"],
                case_data.get("actual_vlan"),
                case_data.get("available_vlans"),
            )
        )

    # Route check
    if (
        "destination_network" in case_data
        and "routing_table" in case_data
    ):
        results.append(
            check_route(
                case_data["destination_network"],
                case_data["routing_table"],
            )
        )

    return results


# ============================================================
# SIMPLE TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("NETSAGE AI - RULE ENGINE TEST")
    print("=" * 60)

    test_case = {
        "ip_addresses": [
            "192.168.1.10",
            "192.168.1.20",
            "192.168.1.10",
        ],

        "host_ip": "192.168.1.10",
        "ip_address": "192.168.1.10",
        "subnet_mask": "255.255.255.0",
        "gateway": "192.168.2.1",

        "interface_name": "Fa0/3",
        "interface_status": "up",

        "expected_vlan": 30,
        "actual_vlan": 20,
        "available_vlans": [1, 10, 20, 30],

        "destination_network": "192.168.50.0/24",
        "routing_table": [
            "192.168.10.0/24",
            "192.168.20.0/24",
        ],
    }

    results = run_all_checks(test_case)

    for result in results:

        print()
        print(f"Rule     : {result['rule']}")
        print(f"Status   : {result['status']}")
        print(f"Severity : {result['severity']}")
        print(f"Message  : {result['message']}")

        if result["evidence"]:
            print("Evidence :")

            for evidence in result["evidence"]:
                print(f"  - {evidence}")

    print()
    print("=" * 60)
    print("RULE ENGINE TEST COMPLETE")
    print("=" * 60)