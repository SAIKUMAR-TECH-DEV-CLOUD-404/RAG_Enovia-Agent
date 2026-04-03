"""
missing_dittios.py
──────────────────

TWO public functions:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FUNCTION 1 — show_ditto_rows(part_number)
  Command  : missing dittios AK00002600895
  File used: MissingReport_AK00002600895.csv
  Filter   : Parent Type == "DITTO"  (exact — NOT "DITTO ASSY")
  Group by : Parent Name  (one block per unique parent name)
  Each row : Child Name  [Diff]  — positive shown as [7], negative as [-1]
             (every row kept separately, same child can appear twice
              if it has two different Parent Version values)

  Output example:
    Missing Dittio AKD0002596420 :
        DTR0000340190 [7],
        HHD0000043300 [1],
        DTR0000191036 [1],
        DTR0021158630 [8],
        HHD0000043302 [1],
        DTR0000174952 [1],
        AKD0002596421 [1]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FUNCTION 2 — show_by_type_and_name(parent_type, parent_name)
  Command  : missing ASSEMBLY AK00002600895
             missing DITTO ASSY AKD0002590086
             missing BOUGHT DTR0000191036
  File used: ALL MissingReport_*.csv files (combined)
  Filter   : Parent Type == <type>  AND  Parent Name == <name>
  Each row : Child Name  [Diff]  — kept in original CSV order,
             duplicate children allowed (different versions = different rows)

  Output example:
    Missing ASSEMBLY AK00002600895 :
        AK00002600899 [-1],
        AKD0002601361 [1],
        AK00002600901 [-1],
        AK00002600899 [1],
        AKD0002601361 [-1],
        AK00002600901 [1]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DIFF FORMAT RULES
  Positive diff  →  [7]    (no + sign)
  Negative diff  →  [-1]
"""

import os
from typing import Optional
import pandas as pd
import config

# ─────────────────────────────────────────────────────────────
#  File-loading helpers
# ─────────────────────────────────────────────────────────────

def _load_report_for_part(part_number: str) -> Optional[pd.DataFrame]:
    """Load MissingReport_<part_number>.csv (most recent if multiple exist)."""
    try:
        all_files = os.listdir(config.OUTPUT_FOLDER)
    except FileNotFoundError:
        print(f"❌  Output folder not found: {config.OUTPUT_FOLDER}")
        return None

    prefix   = config.REPORT_PREFIX
    matching = sorted(
        [f for f in all_files if f.startswith(f"{prefix}{part_number}")],
        reverse=True,
    )

    if not matching:
        print(f"❌  No report found for part number: {part_number}")
        print(f"     Run  'compare bom {part_number}'  first to generate it.")
        return None

    path = os.path.join(config.OUTPUT_FOLDER, matching[0])
    try:
        df = pd.read_csv(path)
        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].str.strip()
        return df if not df.empty else None
    except Exception as exc:
        print(f"❌  Could not read '{matching[0]}': {exc}")
        return None

# ─────────────────────────────────────────────────────────────
#  Diff formatting helper
# ─────────────────────────────────────────────────────────────

def _fmt_diff(diff: int) -> str:
    """Format the diff value for display."""
    return f"[{diff}]" if diff >= 0 else f"[{diff}]"

# ─────────────────────────────────────────────────────────────
#  PUBLIC FUNCTION 1 — missing dittios <PART_NUMBER>
# ─────────────────────────────────────────────────────────────

def show_ditto_rows(part_number: str) -> None:
    """Filter Parent Type == 'DITTO' and group by Parent Name."""
    df = _load_report_for_part(part_number)
    if df is None:
        return

    ditto_df = df[df["Parent Type"] == "DITTO"].copy()
    if ditto_df.empty:
        print(f"\n✅  No DITTO rows found in report for part: {part_number}")
        return

    seen, groups = [], {}
    for _, row in ditto_df.iterrows():
        pname = row["Parent Name"]
        if pname not in groups:
            seen.append(pname)
            groups[pname] = []
        groups[pname].append((row["Child Name"], int(row["Diff"])))

    print(f"\n{'─' * 60}")
    print(f"  missing dittios for part: {part_number}")
    print(f"{'─' * 60}")

    for pname in seen:
        entries = [f"{child} {_fmt_diff(diff)}" for child, diff in groups[pname]]
        children_str = ",\n    ".join(entries)
        print(f"\n  Missing Dittio {pname} :")
        print(f"    {children_str}")

    print(f"\n{'─' * 60}\n")

# ─────────────────────────────────────────────────────────────
#  PUBLIC FUNCTION 2 — missing <PARENT_TYPE> <PARENT_NAME>
# ─────────────────────────────────────────────────────────────

def show_by_type_and_name(parent_type: str, part_number: str) -> None:
    """
    Load MissingReport_<part_number>.csv.
    Filter rows where Parent Type == parent_type.
    Group by Parent Name, print each parent's children with diffs.
    """
    df = _load_report_for_part(part_number)
    if df is None:
        return

    mask = df["Parent Type"].str.upper() == parent_type.upper()
    filtered = df[mask].copy()

    if filtered.empty:
        print(
            f"\n✅  No rows found in report {part_number} for "
            f"Type='{parent_type}'\n"
            f"     Check spelling or run 'compare bom {part_number}' first.\n"
        )
        return

    seen, groups = [], {}
    for _, row in filtered.iterrows():
        pname = row["Parent Name"]
        if pname not in groups:
            seen.append(pname)
            groups[pname] = []
        groups[pname].append((row["Child Name"], int(row["Diff"])))

    print(f"\n{'─' * 60}")
    for pname in seen:
        entries = [f"{child} {_fmt_diff(diff)}" for child, diff in groups[pname]]
        children_str = ",\n    ".join(entries)
        print(f"\n  Missing {parent_type.upper()} {pname} :")
        print(f"    {children_str}")
    print(f"\n{'─' * 60}\n")
