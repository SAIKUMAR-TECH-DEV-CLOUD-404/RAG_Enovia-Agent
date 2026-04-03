"""
report_generator.py
───────────────────
Generates the CSV mismatch report by comparing DMA and PLM BOM maps.
Only rows where DMA qty ≠ PLM qty are written (diff ≠ 0).
"""

import os
from typing import Dict

import config
from bom_model import BomKey

BomMap = Dict[BomKey, int]


def generate_report(
    dma_map: BomMap,
    plm_map: BomMap,
    part_number: str,
) -> str:
    """
    Write a CSV diff report to the Output folder.

    Parameters
    ----------
    dma_map     : quantity-map from DMA BOM
    plm_map     : quantity-map from PLM BOM
    part_number : used to build the output filename

    Returns
    -------
    Full path of the generated report file.
    """
    os.makedirs(config.OUTPUT_FOLDER, exist_ok=True)

    filename    = f"{config.REPORT_PREFIX}{part_number}.csv"
    output_path = os.path.join(config.OUTPUT_FOLDER, filename)
    header      = config.REPORT_HEADER

    all_keys = set(dma_map.keys()) | set(plm_map.keys())

    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write(header + "\n")
        for key in all_keys:
            dma_qty = dma_map.get(key, 0)
            plm_qty = plm_map.get(key, 0)
            diff    = dma_qty - plm_qty
            if diff != 0:
                fh.write(
                    f"{key.parent_type},{key.parent_part},"
                    f"{key.parent_version},{key.child_part},"
                    f"{dma_qty},{plm_qty},{diff}\n"
                )

    return output_path
