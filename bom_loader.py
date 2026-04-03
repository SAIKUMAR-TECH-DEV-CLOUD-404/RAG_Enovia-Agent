"""
bom_loader.py
─────────────
Reads PLM and DMA BOM files and returns quantity-maps keyed by BomKey.
All column indices and skip-values come from config.py — nothing is hard-coded.
"""

from collections import defaultdict
from typing import Dict, List, Tuple

import config
from bom_model import BomKey


# ── Type alias ───────────────────────────────────────────────────────────────
BomMap = Dict[BomKey, int]   # BomKey → quantity


# ── PLM loader ───────────────────────────────────────────────────────────────
def load_plm_bom(plm_file: str) -> BomMap:
    """
    Parse the PLM BOM CSV file.

    Returns a dict mapping each BomKey to its occurrence count.
    Rows flagged with the configured NO_LINKS marker are skipped.
    """
    plm_map: BomMap = defaultdict(int)

    col_parent_type    = config.PLM_COL_PARENT_TYPE
    col_parent_part    = config.PLM_COL_PARENT_PART
    col_parent_version = config.PLM_COL_PARENT_VERSION
    col_has_links      = config.PLM_COL_HAS_LINKS
    col_child_part     = config.PLM_COL_CHILD_PART
    skip_value         = config.PLM_SKIP_LINK_VALUE
    delimiter          = config.PLM_DELIMITER

    with open(plm_file, encoding="utf-8") as fh:
        lines = fh.readlines()

    for raw in lines[1:]:                          # skip header row
        line = raw.replace('"', '')
        cols = line.strip().split(delimiter)

        if len(cols) <= max(col_parent_type, col_parent_part,
                            col_parent_version, col_has_links, col_child_part):
            continue                               # malformed row — skip

        if cols[col_has_links].strip() == skip_value:
            continue                               # no structural links — skip

        key = BomKey(
            parent_type    = cols[col_parent_type].strip(),
            parent_part    = cols[col_parent_part].strip(),
            parent_version = cols[col_parent_version].strip().replace("'", ""),
            child_part     = cols[col_child_part].strip(),
        )
        plm_map[key] += 1

    return plm_map


# ── DMA loader + comparison ───────────────────────────────────────────────────
def load_dma_and_compare(
    dma_file: str,
    plm_map: BomMap,
) -> Tuple[BomMap, List[BomKey]]:
    """
    Parse the DMA BOM pipe-delimited file and compare against *plm_map*.

    Returns
    -------
    dma_map      : quantity-map for the DMA BOM
    missing_keys : BomKeys present in DMA but absent (qty 0) in PLM
    """
    dma_map: BomMap        = defaultdict(int)
    missing_keys: List[BomKey] = []

    col_parent_type    = config.DMA_COL_PARENT_TYPE
    col_parent_part    = config.DMA_COL_PARENT_PART
    col_parent_version = config.DMA_COL_PARENT_VERSION
    col_has_links      = config.DMA_COL_HAS_LINKS
    col_child_part     = config.DMA_COL_CHILD_PART
    skip_value         = config.DMA_SKIP_LINK_VALUE
    delimiter          = config.DMA_DELIMITER

    with open(dma_file, encoding="utf-8") as fh:
        lines = fh.readlines()

    for raw in lines[1:]:                          # skip header row
        line = raw.replace('"', '')
        cols = line.strip().split(delimiter)

        if len(cols) <= max(col_parent_type, col_parent_part,
                            col_parent_version, col_has_links, col_child_part):
            continue                               # malformed row — skip

        if cols[col_has_links].strip() == skip_value:
            continue                               # no structural links — skip

        key = BomKey(
            parent_type    = cols[col_parent_type].strip(),
            parent_part    = cols[col_parent_part].strip(),
            parent_version = cols[col_parent_version].strip().replace("'", ""),
            child_part     = cols[col_child_part].strip(),
        )
        dma_map[key] += 1

        if plm_map.get(key, 0) == 0:
            missing_keys.append(key)

    return dma_map, missing_keys
