"""
config.py
─────────
Reads `config.properties` and exposes all settings as typed helpers.
Every other module imports from here — no hard-coded paths anywhere else.
"""

import os

# ── Locate config.properties relative to this file ──────────────────────────
_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.properties")


def _load_properties(path: str) -> dict:
    """Parse a .properties file into a plain dict (ignores # comments)."""
    props = {}
    with open(path, encoding="utf-8") as fh:
        for raw_line in fh:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            props[key.strip()] = value.strip()
    return props


# Load once at import time
_P = _load_properties(_CONFIG_PATH)


# ── Public helpers ───────────────────────────────────────────────────────────
def get(key: str, fallback: str = "") -> str:
    """Return a raw string value from config."""
    return _P.get(key, fallback)


def get_int(key: str, fallback: int = 0) -> int:
    return int(_P.get(key, fallback))


# ── Convenience constants (import these directly in other modules) ───────────
INPUT_FOLDER        = get("input.folder")
OUTPUT_FOLDER       = get("output.folder")

ERRORS_FILE         = get("rag.errors.file")
CHUNK_SIZE          = get_int("rag.chunk.size", 300)
CHUNK_OVERLAP       = get_int("rag.chunk.overlap", 50)
TOP_K               = get_int("rag.top.k.results", 2)
EMBEDDING_MODEL     = get("embedding.model.name")

PLM_PATTERN         = get("bom.plm.pattern")
DMA_PATTERN         = get("bom.dma.pattern")

PLM_DELIMITER       = get("bom.plm.delimiter", ",")
DMA_DELIMITER       = get("bom.dma.delimiter", "|")

PLM_COL_PARENT_TYPE    = get_int("bom.plm.col.parent.type", 1)
PLM_COL_PARENT_PART    = get_int("bom.plm.col.parent.part", 2)
PLM_COL_PARENT_VERSION = get_int("bom.plm.col.parent.version", 3)
PLM_COL_HAS_LINKS      = get_int("bom.plm.col.has.links", 7)
PLM_COL_CHILD_PART     = get_int("bom.plm.col.child.part", 9)
PLM_SKIP_LINK_VALUE    = get("bom.plm.skip.link.value", "NO_LINKS")

DMA_COL_PARENT_TYPE    = get_int("bom.dma.col.parent.type", 7)
DMA_COL_PARENT_PART    = get_int("bom.dma.col.parent.part", 3)
DMA_COL_PARENT_VERSION = get_int("bom.dma.col.parent.version", 4)
DMA_COL_HAS_LINKS      = get_int("bom.dma.col.has.links", 8)
DMA_COL_CHILD_PART     = get_int("bom.dma.col.child.part", 12)
DMA_SKIP_LINK_VALUE    = get("bom.dma.skip.link.value", "NO LINKS")

REPORT_PREFIX  = get("report.prefix", "MissingReport_")
REPORT_HEADER  = get("report.header")
