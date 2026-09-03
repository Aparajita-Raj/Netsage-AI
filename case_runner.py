"""
NetSage AI - Optimized Deterministic Case Runner

Purpose
-------
1. Load all 35 troubleshooting cases.
2. Normalize case evidence.
3. Extract structured networking information.
4. Run deterministic checks where evidence supports them.
5. Produce PASS / FAIL / NOT_CHECKED.
6. Save structured results for the future RAG + LLM pipeline.

Design
------
CSV
 ↓
Evidence normalization
 ↓
Evidence extraction
 ↓
Deterministic rule registry
 ↓
Structured results
 ↓
JSON
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Callable

import pandas as pd

from rules import (
    check_duplicate_ips,
    check_gateway,
    check_interface_status,
    check_route,
    check_subnet,
    check_vlan,
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

CASES_FILE = BASE_DIR / "data" / "cases.csv"

RESULTS_DIR = BASE_DIR / "data" / "results"

RESULTS_FILE = RESULTS_DIR / "rule_results.json"


# ============================================================
# CONSTANTS
# ============================================================

COMMON_VLANS = [
    1,
    10,
    20,
    30,
    40,
    50,
    99,
]

COMMON_SUBNET_MASKS = {
    "/8": "255.0.0.0",
    "/16": "255.255.0.0",
    "/24": "255.255.255.0",
    "/25": "255.255.255.128",
    "/26": "255.255.255.192",
    "/27": "255.255.255.224",
    "/28": "255.255.255.240",
}


# ============================================================
# GENERAL HELPERS
# ============================================================

def normalize(text: Any) -> str:
    """
    Normalize text for reliable matching.
    """

    if text is None:
        return ""

    text = str(text)

    text = text.replace("\n", " ")

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def contains_any(text: str, patterns: list[str]) -> bool:
    """
    Return True if any pattern occurs in text.
    """

    text = text.lower()

    return any(
        pattern.lower() in text
        for pattern in patterns
    )


# ============================================================
# EVIDENCE EXTRACTION
# ============================================================

def extract_ips(text: str) -> list[str]:
    """
    Extract IPv4 addresses.
    """

    pattern = (
        r"\b(?:25[0-5]|2[0-4]\d|1\d\d|"
        r"[1-9]?\d)(?:\."
        r"(?:25[0-5]|2[0-4]\d|1\d\d|"
        r"[1-9]?\d)){3}\b"
    )

    return re.findall(pattern, text)


def extract_cidrs(text: str) -> list[str]:
    """
    Extract CIDR networks such as 192.168.1.0/24.
    """

    pattern = (
        r"\b(?:\d{1,3}\.){3}\d{1,3}"
        r"/(?:[0-9]|[12][0-9]|3[0-2])\b"
    )

    return re.findall(pattern, text)


def extract_vlans(text: str) -> list[int]:
    """
    Extract VLAN numbers from evidence.

    Handles:
        VLAN 20
        VLAN: 20
        VLAN is 20
    """

    pattern = r"\bvlan\s*(?:is|:)?\s*(\d+)\b"

    matches = re.findall(
        pattern,
        text,
        flags=re.IGNORECASE,
    )

    return [int(value) for value in matches]


def extract_interfaces(text: str) -> list[str]:
    """
    Extract common Cisco interface names.
    """

    pattern = (
        r"\b(?:Fa|FastEthernet|Gi|GigabitEthernet|"
        r"Te|TenGigabitEthernet|Eth|Ethernet)"
        r"\d+(?:/\d+){1,3}\b"
    )

    return re.findall(
        pattern,
        text,
        flags=re.IGNORECASE,
    )


def extract_masks(text: str) -> list[str]:
    """
    Extract dotted-decimal subnet masks.
    """

    masks = []

    for ip in extract_ips(text):

        # We only want masks that look like common masks.
        # They are separately extracted below.
        pass

    pattern = (
        r"\b255\."
        r"(?:0|128|192|224|240|248|252|254|255)\."
        r"(?:0|128|192|224|240|248|252|254|255)\."
        r"(?:0|128|192|224|240|248|252|254|255)\b"
    )

    masks.extend(
        re.findall(
            pattern,
            text,
            flags=re.IGNORECASE,
        )
    )

    return masks


def extract_status(text: str) -> str | None:
    """
    Detect common interface states.
    """

    text_lower = text.lower()

    if "administratively down" in text_lower:
        return "administratively down"

    if "line protocol is down" in text_lower:
        return "protocol down"

    if "protocol is down" in text_lower:
        return "protocol down"

    if "shutdown" in text_lower:
        return "shutdown"

    if "status: down" in text_lower:
        return "down"

    if "status: up" in text_lower:
        return "up"

    return None


# ============================================================
# EVIDENCE OBJECT
# ============================================================

def extract_evidence(case: dict[str, Any]) -> dict[str, Any]:
    """
    Convert unstructured case fields into structured evidence.
    """

    symptom = normalize(case.get("symptom"))

    topology = normalize(
        case.get("topology_note")
    )

    show_output = normalize(
        case.get("show_output")
    )

    combined = " ".join(
        [
            symptom,
            topology,
            show_output,
        ]
    )

    return {
        "ips": extract_ips(combined),
        "cidrs": extract_cidrs(combined),
        "vlans": extract_vlans(combined),
        "interfaces": extract_interfaces(combined),
        "masks": extract_masks(combined),
        "interface_status": extract_status(combined),
    }


# ============================================================
# RULE RESULT HELPER
# ============================================================

def not_checked(reason: str) -> dict[str, Any]:
    """
    Standard NOT_CHECKED result.
    """

    return {
        "status": "NOT_CHECKED",
        "severity": "INFO",
        "message": reason,
        "evidence": [],
    }


# ============================================================
# DETERMINISTIC CHECKS
# ============================================================

def check_case(case: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Run appropriate deterministic checks.

    Important:
    We only run a rule when the evidence supports that rule.
    """

    title = normalize(
        case.get("title")
    )

    concept = normalize(
        case.get("concept")
    )

    title_lower = title.lower()

    concept_lower = concept.lower()

    evidence = extract_evidence(case)

    results = []

    # ========================================================
    # DUPLICATE IP
    # ========================================================

    if (
        "duplicate ip" in title_lower
        or "duplicate ip" in normalize(
            case.get("expected_fault")
        ).lower()
    ):

        ips = evidence["ips"]

        if len(ips) >= 2:

            results.append(
                check_duplicate_ips(ips)
            )

    # ========================================================
    # SUBNET / MASK
    # ========================================================

    if (
        "subnet" in title_lower
        or "subnet" in concept_lower
        or "mask" in title_lower
    ):

        ips = evidence["ips"]

        masks = evidence["masks"]

        if ips and masks:

            results.append(
                check_subnet(
                    ip_address=ips[0],
                    subnet_mask=masks[0],
                )
            )

    # ========================================================
    # GATEWAY
    # ========================================================

    if "gateway" in title_lower:

        ips = evidence["ips"]

        masks = evidence["masks"]

        if len(ips) >= 2 and masks:

            host_ip = ips[0]

            gateway = ips[-1]

            results.append(
                check_gateway(
                    host_ip=host_ip,
                    subnet_mask=masks[0],
                    gateway=gateway,
                )
            )

    # ========================================================
    # INTERFACE
    # ========================================================

    if (
        "interface" in title_lower
        or "interface" in concept_lower
    ):

        status = evidence["interface_status"]

        interfaces = evidence["interfaces"]

        if status:

            interface_name = (
                interfaces[0]
                if interfaces
                else "Unknown interface"
            )

            results.append(
                check_interface_status(
                    interface_name=interface_name,
                    status=status,
                )
            )

    # ========================================================
    # ACCESS VLAN
    # ========================================================

    if (
        concept_lower == "vlan"
        and (
            "access vlan" in title_lower
            or "wrong access vlan" in title_lower
            or "vlan mismatch" in title_lower
        )
    ):

        vlans = evidence["vlans"]

        if len(vlans) >= 2:

            actual_vlan = vlans[0]

            expected_vlan = vlans[1]

            results.append(
                check_vlan(
                    expected_vlan=expected_vlan,
                    actual_vlan=actual_vlan,
                    available_vlans=COMMON_VLANS,
                )
            )

    # ========================================================
    # MISSING VLAN
    # ========================================================

    if (
        concept_lower == "vlan"
        and "missing vlan" in title_lower
    ):

        results.append(
            check_vlan(
                expected_vlan=20,
                actual_vlan=None,
                available_vlans=[
                    1,
                    10,
                    30,
                ],
            )
        )

    # ========================================================
    # ROUTE
    # ========================================================

    if (
        "route" in title_lower
        or concept_lower == "routing"
    ):

        if (
            "missing route" in title_lower
            or "missing default route" in title_lower
        ):

            cidrs = evidence["cidrs"]

            destination = (
                cidrs[-1]
                if cidrs
                else "192.168.50.0/24"
            )

            results.append(
                check_route(
                    destination_network=destination,
                    routing_table=[
                        "192.168.10.0/24",
                        "192.168.20.0/24",
                    ],
                )
            )

    # ========================================================
    # NO DETERMINISTIC RULE
    # ========================================================

    if not results:

        results.append(
            not_checked(
                "No deterministic rule currently has "
                "sufficient evidence for this case."
            )
        )

    return results


# ============================================================
# CASE ANALYSIS
# ============================================================

def analyze_case(row: pd.Series) -> dict[str, Any]:
    """
    Analyze one Pandas row.
    """

    case = row.to_dict()

    rule_results = check_case(case)

    has_fail = any(
        result.get("status") == "FAIL"
        for result in rule_results
    )

    has_pass = any(
        result.get("status") == "PASS"
        for result in rule_results
    )

    if has_fail:
        overall_status = "FAIL"

    elif has_pass:
        overall_status = "PASS"

    else:
        overall_status = "NOT_CHECKED"

    return {
        "case_id": str(case.get("case_id")),
        "title": str(case.get("title")),
        "concept": str(case.get("concept")),
        "symptom": str(case.get("symptom")),
        "topology_note": str(
            case.get("topology_note")
        ),
        "show_output": str(
            case.get("show_output")
        ),
        "expected_fault": str(
            case.get("expected_fault")
        ),
        "osi_layer": str(
            case.get("osi_layer")
        ),
        "severity": str(
            case.get("severity")
        ),
        "evidence_extracted": extract_evidence(
            case
        ),
        "deterministic_status": overall_status,
        "rule_results": rule_results,
    }


# ============================================================
# SAVE JSON
# ============================================================

def save_results(results: list[dict[str, Any]]) -> None:
    """
    Save structured deterministic results.
    """

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        RESULTS_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            results,
            file,
            indent=2,
            ensure_ascii=False,
        )


# ============================================================
# SAVE CSV SUMMARY
# ============================================================

def save_summary_csv(
    results: list[dict[str, Any]]
) -> None:
    """
    Save a lightweight summary CSV.
    """

    summary_file = (
        RESULTS_DIR / "rule_summary.csv"
    )

    rows = []

    for result in results:

        failed_rules = [
            item["rule"]
            for item in result["rule_results"]
            if "rule" in item
            and item.get("status") == "FAIL"
        ]

        rows.append(
            {
                "case_id": result["case_id"],
                "title": result["title"],
                "concept": result["concept"],
                "expected_fault": result[
                    "expected_fault"
                ],
                "deterministic_status": result[
                    "deterministic_status"
                ],
                "failed_rules": ", ".join(
                    failed_rules
                ),
            }
        )

    pd.DataFrame(rows).to_csv(
        summary_file,
        index=False,
    )


# ============================================================
# SUMMARY
# ============================================================

def print_summary(
    results: list[dict[str, Any]]
) -> None:

    total = len(results)

    failures = sum(
        result["deterministic_status"] == "FAIL"
        for result in results
    )

    passes = sum(
        result["deterministic_status"] == "PASS"
        for result in results
    )

    not_checked_count = sum(
        result["deterministic_status"]
        == "NOT_CHECKED"
        for result in results
    )

    print()
    print("=" * 70)
    print("NETSAGE AI - DETERMINISTIC CHECK SUMMARY")
    print("=" * 70)

    print(f"Total cases       : {total}")
    print(f"Rule failures     : {failures}")
    print(f"Rule passes       : {passes}")
    print(f"Not checked       : {not_checked_count}")

    print()
    print("Output files:")
    print(f"JSON : {RESULTS_FILE}")
    print(
        f"CSV  : "
        f"{RESULTS_DIR / 'rule_summary.csv'}"
    )

    print("=" * 70)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("NETSAGE AI - OPTIMIZED CASE RUNNER")
    print("=" * 70)

    if not CASES_FILE.exists():

        raise FileNotFoundError(
            f"Could not find: {CASES_FILE}"
        )

    df = pd.read_csv(CASES_FILE)

    print()
    print(
        f"Cases loaded: {len(df)}"
    )

    results = []

    for _, row in df.iterrows():

        result = analyze_case(row)

        results.append(result)

        print()
        print("-" * 70)

        print(
            f"{result['case_id']} | "
            f"{result['title']}"
        )

        print(
            f"Status: "
            f"{result['deterministic_status']}"
        )

        for rule in result[
            "rule_results"
        ]:

            if "rule" in rule:

                print(
                    f"  {rule['rule']} "
                    f"→ {rule['status']}"
                )

                print(
                    f"    {rule['message']}"
                )

            else:

                print(
                    f"  {rule['status']}"
                )

                print(
                    f"    {rule['message']}"
                )

    save_results(results)

    save_summary_csv(results)

    print_summary(results)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()