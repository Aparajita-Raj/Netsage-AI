"""
NetSage AI - Optimized RAG Builder

Builds a local Chroma vector database with metadata
for faster and more accurate retrieval.
"""

from pathlib import Path

from langchain_core.documents import Document

from langchain_huggingface import (
    HuggingFaceEmbeddings,
)

from langchain_chroma import Chroma


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

KNOWLEDGE_FILE = (
    BASE_DIR
    / "data"
    / "knowledge"
    / "network_troubleshooting.md"
)

VECTOR_DB_DIR = (
    BASE_DIR
    / "data"
    / "vector_db"
)


# ============================================================
# SECTION → CONCEPT MAPPING
# ============================================================

SECTION_MAP = {

    "VLAN Troubleshooting": "VLAN",

    "Trunk Troubleshooting": "Trunk",

    "IP Addressing Troubleshooting": "IP addressing",

    "Default Gateway Troubleshooting": "Gateway",

    "Interface Troubleshooting": "Interface",

    "Routing Troubleshooting": "Routing",

    "OSPF Troubleshooting": "OSPF",

    "DHCP Troubleshooting": "DHCP",

    "DNS Troubleshooting": "DNS",

    "ACL Troubleshooting": "ACL",

    "NAT Troubleshooting": "NAT",

    "Wireless Troubleshooting": "Wireless",
}


# ============================================================
# LOAD MARKDOWN SECTIONS
# ============================================================

def load_sections():

    text = KNOWLEDGE_FILE.read_text(
        encoding="utf-8"
    )

    lines = text.splitlines()

    documents = []

    current_section = None

    current_content = []

    for line in lines:

        # ----------------------------------------------------
        # Main section
        # ----------------------------------------------------

        if line.startswith("## "):

            if current_section and current_content:

                documents.append(
                    create_document(
                        current_section,
                        current_content,
                    )
                )

            current_section = (
                line[3:].strip()
            )

            current_content = []

            continue

        # ----------------------------------------------------
        # Content
        # ----------------------------------------------------

        if current_section:

            current_content.append(line)

    # --------------------------------------------------------
    # Last section
    # --------------------------------------------------------

    if current_section and current_content:

        documents.append(
            create_document(
                current_section,
                current_content,
            )
        )

    return documents


# ============================================================
# CREATE DOCUMENT
# ============================================================

def create_document(
    section: str,
    content: list[str],
):

    concept = SECTION_MAP.get(
        section,
        "General",
    )

    text = "\n".join(
        content
    ).strip()

    return Document(
        page_content=text,
        metadata={
            "concept": concept,
            "source": "network_troubleshooting.md",
            "section": section,
        },
    )


# ============================================================
# BUILD DATABASE
# ============================================================

def build_database():

    print("=" * 70)
    print("NETSAGE AI - OPTIMIZED RAG BUILDER")
    print("=" * 70)

    if not KNOWLEDGE_FILE.exists():

        raise FileNotFoundError(
            f"Knowledge file not found:\n"
            f"{KNOWLEDGE_FILE}"
        )

    print()
    print("Loading knowledge...")

    documents = load_sections()

    print(
        f"Knowledge sections: "
        f"{len(documents)}"
    )

    for document in documents:

        print(
            f"  [{document.metadata['concept']}] "
            f"{document.metadata['section']}"
        )

    # --------------------------------------------------------
    # Embeddings
    # --------------------------------------------------------

    print()
    print("Loading embedding model...")

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

    # --------------------------------------------------------
    # Rebuild vector database
    # --------------------------------------------------------

    print()
    print("Building vector database...")

    vector_db = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=str(
            VECTOR_DB_DIR
        ),
        collection_name="netsage_knowledge_v2",
    )

    print()
    print("=" * 70)
    print("OPTIMIZED RAG DATABASE READY")
    print("=" * 70)

    print()
    print(
        f"Documents stored: "
        f"{len(documents)}"
    )

    print(
        f"Database: "
        f"{VECTOR_DB_DIR}"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    build_database()