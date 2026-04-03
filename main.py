"""
main.py  ←  ENTRY POINT
────────
Run with:  python main.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COMMANDS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  compare bom <PART_NUMBER>
      Reads DMA + PLM files for PART_NUMBER, compares them,
      writes MissingReport_<PART_NUMBER>.csv to Output folder.
      Example:
        compare bom AK00002600895

  missing dittios <PART_NUMBER>
      Loads MissingReport_<PART_NUMBER>.csv, filters rows where
      Parent Type == "DITTO", groups by Parent Name and prints
      each parent's children with diff values.
      Example:
        missing dittios AK00002600895

  missing <PARENT_TYPE> <PARENT_NAME>
      Searches ALL saved reports for rows matching that Parent Type
      and Parent Name.  The LAST token is always the Parent Name;
      everything between "missing" and the last token is the Parent Type
      (supports multi-word types like DITTO ASSY, SINGLE PART).
      Examples:
        missing ASSEMBLY AK00002600895
        missing DITTO ASSY AKD0002590086
        missing BOUGHT DTR0000191036
        missing SINGLE PART AK00002591916
        missing DITTO AKD0002596420
        missing STUDY AK00002600788

  exit
      Quit.

  <anything else>
      RAG similarity search over errors.txt knowledge base.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import rag_setup
from file_finder      import find_files
from bom_loader       import load_plm_bom, load_dma_and_compare
from report_generator import generate_report
from missing_dittios  import show_ditto_rows, show_by_type_and_name
from manual_run import run_manual_catproduct


# ── Initialise RAG at startup ─────────────────────────────────────────────────
rag_setup.get_db()


# ─────────────────────────────────────────────────────────────────────────────
#  Command parser for all "missing ..." variants
# ─────────────────────────────────────────────────────────────────────────────

def _parse_missing(query: str):
    """
    Parse a "missing ..." command.

    Returns one of:
        ("dittios",  part_number,  None)         → missing dittios <PART>
        ("by_type",  parent_type,  parent_name)  → missing <TYPE> <NAME>
        ("error",    message,      None)          → bad input

    Parsing rule for by_type:
        tokens = query.split()
        # tokens[0] == "missing"
        # tokens[-1] == parent_name   (always last token)
        # tokens[1:-1] joined        == parent_type  (may be multi-word)
    """
    tokens = query.split()

    # "missing" alone
    if len(tokens) < 2:
        return ("error",
                "Usage:\n"
                "  missing dittios <PART_NUMBER>\n"
                "  missing <PARENT_TYPE> <PARENT_NAME>",
                None)

    second = tokens[1].lower()

    # ── missing dittios <PART> ────────────────────────────────────────────────
    if second == "dittios":
        if len(tokens) < 3:
            return ("error", "Usage: missing dittios <PART_NUMBER>", None)
        part_number = tokens[2]   # token right after "dittios"
        return ("dittios", part_number, None)

    # ── missing <TYPE> <NAME> ─────────────────────────────────────────────────
    if len(tokens) < 3:
        return ("error",
                "Usage: missing <PARENT_TYPE> <PARENT_NAME>\n"
                "Example: missing ASSEMBLY AK00002600895",
                None)

    parent_name = tokens[-1]                     # last token = name
    parent_type = " ".join(tokens[1:-1]).upper() # everything in between = type
    return ("by_type", parent_type, parent_name)


# ─────────────────────────────────────────────────────────────────────────────
#  Main REPL
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    print("\n" + "═" * 60)
    print("  BOM RAG Agent  —  type 'exit' to quit")
    print("═" * 60 + "\n")

    while True:
        try:
            query = input("👉  Ask: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋  Exiting …")
            break

        if not query:
            continue

        q_lower = query.lower()

        # ── exit ─────────────────────────────────────────────────────────────
        if q_lower == "exit":
            print("👋  Exiting …")
            break

        # ── compare bom <PART> ────────────────────────────────────────────────
        elif q_lower.startswith("compare bom"):
            tokens = query.split()
            if len(tokens) < 3:
                print("❌  Usage: compare bom <PART_NUMBER>\n")
                continue
            part_number = tokens[2]
            print(f"\n🔍  Searching files for: {part_number}")
            try:
                dma_file, plm_file = find_files(part_number)
                if not dma_file or not plm_file:
                    print("❌  Required files not found for that part number.\n")
                    continue
                print("🔄  Reading PLM BOM …")
                plm_map = load_plm_bom(plm_file)
                print("🔄  Reading DMA BOM and comparing …")
                dma_map, missing_keys = load_dma_and_compare(dma_file, plm_map)
                out = generate_report(dma_map, plm_map, part_number)
                print(f"\n✅  Report : {out}")
                print(f"📊  Mismatches : {len(missing_keys)}\n")
            except Exception as exc:
                print(f"❌  Error during BOM compare: {exc}\n")

        # ── missing ... ───────────────────────────────────────────────────────
        elif q_lower.startswith("missing"):
            mode, arg1, arg2 = _parse_missing(query)

            if mode == "error":
                print(f"❌  {arg1}\n")

            elif mode == "dittios":
                # arg1 = part_number
                try:
                    show_ditto_rows(arg1)
                except Exception as exc:
                    print(f"❌  Error: {exc}\n")

            elif mode == "by_type":
                # arg1 = parent_type,  arg2 = parent_name
                try:
                    show_by_type_and_name(arg1, arg2)
                except Exception as exc:
                    print(f"❌  Error: {exc}\n")

        # ── manual run catproduct ─────────────────────────────────────────────
        elif q_lower == "manual run catproduct":
            try:
                run_manual_catproduct()
            except Exception as exc:
                print(f"❌  Error during manual run: {exc}\n")

        # ── RAG fallback ──────────────────────────────────────────────────────
        else:
            try:
                results = rag_setup.search(query)
                print("\n💡  Answer:\n")
                for doc in results:
                    print(doc.page_content)
                    print("\n" + "─" * 40 + "\n")
            except Exception as exc:
                print(f"❌  RAG search failed: {exc}\n")


if __name__ == "__main__":
    main()