"""
NetSage AI - Optimized RAG Retriever
"""

from pathlib import Path

from langchain_huggingface import (
    HuggingFaceEmbeddings,
)

from langchain_chroma import Chroma


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

VECTOR_DB_DIR = (
    BASE_DIR
    / "data"
    / "vector_db"
)


# ============================================================
# EMBEDDINGS
# ============================================================

embeddings = HuggingFaceEmbeddings(
    model_name=(
        "sentence-transformers/"
        "all-MiniLM-L6-v2"
    ),
    model_kwargs={
        "device": "cpu",
    },
    encode_kwargs={
        "normalize_embeddings": True,
    },
)


# ============================================================
# DATABASE
# ============================================================

vector_db = Chroma(
    persist_directory=str(
        VECTOR_DB_DIR
    ),
    embedding_function=embeddings,
    collection_name="netsage_knowledge_v2",
)


# ============================================================
# CONCEPT DETECTION
# ============================================================

CONCEPT_KEYWORDS = {

    "DHCP": [
        "dhcp",
        "address pool",
        "helper address",
        "ip helper",
        "dhcp server",
        "dhcp client",
        "dhcp relay",
    ],

    "VLAN": [
        "vlan",
        "access vlan",
        "wrong vlan",
    ],

    "Trunk": [
        "trunk",
        "native vlan",
        "allowed vlan",
    ],

    "OSPF": [
        "ospf",
        "neighbor",
        "adjacency",
        "area",
    ],

    "Gateway": [
        "gateway",
        "default gateway",
    ],

    "Routing": [
        "route",
        "routing",
        "next hop",
        "default route",
    ],

    "Interface": [
        "interface",
        "shutdown",
        "protocol down",
        "administratively down",
    ],

    "DNS": [
        "dns",
        "domain",
        "hostname resolution",
        "name resolution",
    ],

    "ACL": [
        "acl",
        "access control",
        "deny traffic",
        "ssh blocked",
        "dns blocked",
    ],

    "NAT": [
        "nat",
        "translation",
        "inside interface",
        "outside interface",
    ],

    "Wireless": [
        "wireless",
        "ssid",
        "wifi",
        "authentication",
    ],

    "IP addressing": [
        "ip address",
        "subnet",
        "subnet mask",
        "duplicate ip",
        "address mismatch",
    ],
}

# ============================================================
# DETECT CONCEPT
# ============================================================

def detect_concept(
    query: str,
) -> str | None:

    query_lower = query.lower()

    scores = {}

    for concept, keywords in (
        CONCEPT_KEYWORDS.items()
    ):

        score = 0

        for keyword in keywords:

            if keyword in query_lower:

                score += 1

        if score > 0:

            scores[concept] = score

    if not scores:

        return None

    return max(
        scores,
        key=scores.get,
    )


# ============================================================
# RETRIEVE
# ============================================================

def retrieve(
    query: str,
    k: int = 3,
):

    concept = detect_concept(
        query
    )

    print()
    print(
        f"Detected concept: "
        f"{concept or 'General'}"
    )

    # --------------------------------------------------------
    # Metadata filtered search
    # --------------------------------------------------------

    if concept:

        documents = (
            vector_db.similarity_search(
                query,
                k=k,
                filter={
                    "concept": concept
                },
            )
        )

    else:

        documents = (
            vector_db.similarity_search(
                query,
                k=k,
            )
        )

    return documents


# ============================================================
# DISPLAY
# ============================================================

def display_results(
    query: str,
    documents,
):

    print()
    print("=" * 70)
    print("NETSAGE AI - OPTIMIZED RAG TEST")
    print("=" * 70)

    print()
    print(
        f"Query:\n{query}"
    )

    print()
    print(
        f"Results: {len(documents)}"
    )

    for index, document in enumerate(
        documents,
        start=1,
    ):

        print()
        print("-" * 70)

        print(
            f"RESULT {index}"
        )

        print(
            f"Concept: "
            f"{document.metadata.get('concept')}"
        )

        print(
            f"Section: "
            f"{document.metadata.get('section')}"
        )

        print()

        print(
            document.page_content[
                :1000
            ]
        )


# ============================================================
# TEST
# ============================================================

def main():

    test_queries = [

        "OSPF neighbor is down and adjacency "
        "is not reaching FULL state",

        "PC is connected to the wrong VLAN",

        "DHCP client cannot get an IP address "
        "from a remote DHCP server",

        "host has wrong default gateway",

        "router has no route to destination",

    ]

    for query in test_queries:

        documents = retrieve(
            query,
            k=3,
        )

        display_results(
            query,
            documents,
        )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()