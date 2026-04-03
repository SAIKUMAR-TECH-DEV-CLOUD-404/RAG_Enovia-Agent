"""
file_finder.py
──────────────
Scans the configured Input folder and returns the correct
DMA / PLM file paths for a given part number.
"""

import os
from typing import Optional, Tuple

import config


def find_files(part_number: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Scan INPUT_FOLDER for files matching *part_number*.

    Returns
    -------
    (dma_file_path, plm_file_path)
    Either may be None if not found.
    """
    input_folder: str = config.INPUT_FOLDER
    plm_pattern: str  = config.PLM_PATTERN
    dma_pattern: str  = config.DMA_PATTERN

    try:
        all_files = os.listdir(input_folder)
    except FileNotFoundError:
        print(f"❌ Input folder not found: {input_folder}")
        return None, None

    print("\n📂 Available files:")
    for f in all_files:
        print(f"   {f}")

    dma_file: Optional[str] = None
    plm_file: Optional[str] = None

    for f in all_files:
        if part_number not in f:
            continue
        full_path = os.path.join(input_folder, f)
        if plm_pattern in f:
            plm_file = full_path
        elif dma_pattern in f:
            dma_file = full_path

    print("\n📂 Files matched:")
    print(f"   DMA : {dma_file or 'NOT FOUND'}")
    print(f"   PLM : {plm_file or 'NOT FOUND'}")

    return dma_file, plm_file
