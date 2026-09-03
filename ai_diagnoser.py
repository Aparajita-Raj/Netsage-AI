"""
NETSAGE AI
AI Diagnosis Engine

Pipeline:
Problem
   ↓
Concept Detection
   ↓
RAG Retrieval
   ↓
Diagnosis
   ↓
Recommended Fixes
   ↓
Verification Steps

OpenAI API is NOT required.
"""

from pathlib import Path
import sys


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# IMPORT RAG RETRIEVER
# ============================================================

from backend.rag_retriever import retrieve


# ============================================================
# CONCEPT DETECTION
# ============================================================

CONCEPT_KEYWORDS = {
    "VLAN": [
        "vlan",
        "access vlan",
        "wrong vlan",
        "missing vlan",
        "vlan mismatch",
        "trunk vlan",
    ],

    "Trunk": [
        "trunk",
        "native vlan",
        "allowed vlan",
        "trunk port",
    ],

    "IP addressing": [
        "ip address",
        "ip mismatch",
        "subnet",
        "subnet mask",
        "duplicate ip",
        "addressing",
    ],

    "Gateway": [
        "gateway",
        "default gateway",
    ],

    "Interface": [
        "interface",
        "port down",
        "interface down",
        "administratively down",
        "protocol down",
    ],

    "Routing": [
        "route",
        "routing",
        "next hop",
        "routing table",
        "default route",
    ],

    "OSPF": [
        "ospf",
        "neighbor",
        "adjacency",
        "full state",
        "area mismatch",
    ],

    "DHCP": [
        "dhcp",
        "address pool",
        "dhcp server",
        "dhcp relay",
        "ip address automatically",
    ],

    "DNS": [
        "dns",
        "domain name",
        "dns server",
        "dns record",
        "name resolution",
    ],

    "ACL": [
        "acl",
        "access control list",
        "blocked traffic",
        "deny traffic",
    ],

    "NAT": [
        "nat",
        "translation",
        "inside interface",
        "outside interface",
    ],

    "Wireless": [
        "wireless",
        "wifi",
        "ssid",
        "authentication",
        "wireless vlan",
    ],
}


def detect_concept(problem: str) -> str:
    """
    Detect the most likely networking concept.
    """

    text = problem.lower()

    scores = {}

    for concept, keywords in CONCEPT_KEYWORDS.items():

        score = 0

        for keyword in keywords:

            if keyword.lower() in text:
                score += 1

        scores[concept] = score

    best_concept = max(scores, key=scores.get)

    if scores[best_concept] == 0:
        return "General"

    return best_concept


# ============================================================
# RAG RETRIEVAL
# ============================================================

# ============================================================
# RAG RETRIEVAL
# ============================================================

def get_rag_knowledge(problem: str, concept: str):
    """
    Connect the diagnosis engine to the existing RAG retriever.
    """

    try:
        results = retrieve(problem, concept)

        if results:
            return results

    except TypeError:
        # Some retriever versions accept only the query.
        try:
            results = retrieve(problem)

            if results:
                return results

        except Exception as error:
            print(f"[RAG WARNING] {error}")

    except Exception as error:
        print(f"[RAG WARNING] {error}")

    return []


# ============================================================
# DIAGNOSIS DATABASE
# ============================================================

DIAGNOSIS_DATABASE = {

    "VLAN": {
        "diagnosis":
            "The device may be assigned to an incorrect or missing VLAN.",

        "fixes": [
            "Check the access VLAN configuration.",
            "Verify that the required VLAN exists.",
            "Assign the interface to the correct VLAN.",
        ],

        "verification": [
            "show vlan brief",
            "show interfaces switchport",
        ],
    },

    "Trunk": {
        "diagnosis":
            "The trunk configuration may not be carrying the required VLAN or may have a native VLAN mismatch.",

        "fixes": [
            "Check trunk mode and allowed VLANs.",
            "Verify the required VLAN is allowed on the trunk.",
            "Check the native VLAN configuration.",
        ],

        "verification": [
            "show interfaces trunk",
            "show interfaces switchport",
        ],
    },

    "IP addressing": {
        "diagnosis":
            "The device may have an incorrect IP address or subnet configuration.",

        "fixes": [
            "Check the IP address.",
            "Verify the subnet mask.",
            "Check for duplicate IP addresses.",
        ],

        "verification": [
            "ipconfig /all",
            "show ip interface brief",
        ],
    },

    "Gateway": {
        "diagnosis":
            "The configured default gateway may be incorrect or outside the host subnet.",

        "fixes": [
            "Verify the host subnet.",
            "Configure the correct default gateway.",
            "Test connectivity to the gateway.",
        ],

        "verification": [
            "ipconfig /all",
            "ping <gateway>",
        ],
    },

    "Interface": {
        "diagnosis":
            "The network interface may be administratively disabled or operationally down.",

        "fixes": [
            "Check the interface status.",
            "Verify the interface configuration.",
            "Enable the interface if it is administratively down.",
        ],

        "verification": [
            "show ip interface brief",
            "show interfaces",
        ],
    },

    "Routing": {
        "diagnosis":
            "The routing table may not contain the required destination route.",

        "fixes": [
            "Check the routing table.",
            "Verify the next hop.",
            "Add or correct the required route.",
        ],

        "verification": [
            "show ip route",
            "ping <destination>",
        ],
    },

    "OSPF": {
        "diagnosis":
            "The OSPF adjacency may not be forming correctly.",

        "fixes": [
            "Check OSPF neighbor state.",
            "Verify OSPF areas.",
            "Check network configuration.",
            "Verify authentication and timers.",
        ],

        "verification": [
            "show ip ospf neighbor",
            "show ip ospf interface",
        ],
    },

    "DHCP": {
        "diagnosis":
            "The DHCP service or relay configuration may be preventing clients from receiving addresses.",

        "fixes": [
            "Check the DHCP pool.",
            "Verify the DHCP network.",
            "Check the default gateway.",
            "Verify DHCP relay configuration.",
        ],

        "verification": [
            "show ip dhcp pool",
            "show ip dhcp binding",
            "show running-config",
        ],
    },

    "DNS": {
        "diagnosis":
            "The DNS configuration or DNS server connectivity may be preventing name resolution.",

        "fixes": [
            "Verify the configured DNS server.",
            "Check DNS records.",
            "Test connectivity to the DNS server.",
        ],

        "verification": [
            "ipconfig /all",
            "nslookup <domain>",
            "ping <dns-server>",
        ],
    },

    "ACL": {
        "diagnosis":
            "An access control list may be blocking the required traffic.",

        "fixes": [
            "Inspect the ACL rules.",
            "Check whether the ACL denies the required traffic.",
            "Verify the ACL is applied to the correct interface and direction.",
        ],

        "verification": [
            "show access-lists",
            "show running-config",
        ],
    },

    "NAT": {
        "diagnosis":
            "The NAT configuration may be preventing address translation.",

        "fixes": [
            "Check inside and outside interfaces.",
            "Verify the NAT ACL.",
            "Check whether translations are being created.",
        ],

        "verification": [
            "show ip nat translations",
            "show ip nat statistics",
            "show running-config",
        ],
    },

    "Wireless": {
        "diagnosis":
            "The wireless configuration may contain an SSID, authentication, VLAN, or gateway problem.",

        "fixes": [
            "Verify the SSID configuration.",
            "Check wireless authentication.",
            "Verify wireless VLAN mapping.",
            "Check the wireless gateway configuration.",
        ],

        "verification": [
            "show running-config",
            "show vlan brief",
            "ping <gateway>",
        ],
    },

    "General": {
        "diagnosis":
            "The network problem could not be mapped to a specific troubleshooting category.",

        "fixes": [
            "Collect the relevant device configuration.",
            "Check interface and connectivity status.",
            "Review routing and addressing information.",
        ],

        "verification": [
            "show ip interface brief",
            "show ip route",
        ],
    },
}


# ============================================================
# FORMAT RAG RESULTS
# ============================================================

def format_rag_results(results):
    """
    Convert RAG results into readable text.
    """

    if not results:
        return ""

    formatted = []

    for result in results:

        if isinstance(result, dict):

            text = result.get("text")

            if not text:
                text = result.get("content")

            if not text:
                text = str(result)

            formatted.append(text)

        else:

            # LangChain Document
            if hasattr(result, "page_content"):

                formatted.append(result.page_content)

            else:

                formatted.append(str(result))

    return "\n\n---\n\n".join(formatted)


# ============================================================
# MAIN DIAGNOSIS FUNCTION
# ============================================================

def diagnose(problem: str):

    concept = detect_concept(problem)

    rag_results = get_rag_knowledge(problem, concept)

    knowledge = format_rag_results(rag_results)

    diagnosis_data = DIAGNOSIS_DATABASE.get(
        concept,
        DIAGNOSIS_DATABASE["General"]
    )

    return {
        "problem": problem,
        "concept": concept,
        "diagnosis": diagnosis_data["diagnosis"],
        "fixes": diagnosis_data["fixes"],
        "verification": diagnosis_data["verification"],
        "rag_found": bool(rag_results),
        "rag_knowledge": knowledge,
    }


# ============================================================
# DISPLAY
# ============================================================

def print_diagnosis(result):

    print()
    print("=" * 70)
    print("NETSAGE AI - NETWORK DIAGNOSIS")
    print("=" * 70)

    print()

    print("Problem:")
    print(result["problem"])

    print()

    print("Detected Concept:")
    print(result["concept"])

    print()

    print("Diagnosis:")
    print(result["diagnosis"])

    print()

    print("Recommended Fixes:")

    for index, fix in enumerate(result["fixes"], 1):

        print(f"  {index}. {fix}")

    print()

    print("Verification Steps:")

    for index, step in enumerate(result["verification"], 1):

        print(f"  {index}. {step}")

    print()

    print(
        "RAG Knowledge Retrieved:",
        "YES" if result["rag_found"] else "NO"
    )

    if result["rag_found"]:

        print()

        print("Retrieved Knowledge:")
        print("-" * 70)

        print(result["rag_knowledge"][:3000])

    print()

    print("=" * 70)
    print("DIAGNOSIS COMPLETE")
    print("=" * 70)


# ============================================================
# TEST CASES
# ============================================================

if __name__ == "__main__":

    test_problems = [

        "PC is connected to the wrong VLAN",

        "OSPF neighbor is down and adjacency is not reaching FULL state",

        "host has wrong default gateway",

        "router has no route to destination",

        "DHCP client cannot get an IP address from a remote DHCP server",

    ]

    for problem in test_problems:

        result = diagnose(problem)

        print_diagnosis(result)