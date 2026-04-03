# manual_run.py

import os
import textwrap

# ── SQL Builder ─────────────────────────────────────────────
def build_sql_query(parts):
    quoted = ",".join([f"'{p}'" for p in parts])
    sql = f"""
    SELECT p.s_part_number,
           p."$COID",
           p.c_part_version
    FROM DESIGN.part_list p
    JOIN (
        SELECT s_part_number, MAX(c_part_version) AS max_version
        FROM DESIGN.part_list
        WHERE s_part_number IN ({quoted})
        GROUP BY s_part_number
    ) latest
    ON p.s_part_number = latest.s_part_number
    AND p.c_part_version = latest.max_version;
    """
    return textwrap.dedent(sql).strip()

# ── XML Generator ───────────────────────────────────────────
def generate_xml(objects):
    xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<enoviavpm_transfer>']
    for name, uuid in objects:
        xml_lines.append(
            f'\t<enoviavpm_object name="{name}" uuid="CATCON DESIGN PART_LIST {uuid}3030303030303030"/>'
        )
    xml_lines.append('</enoviavpm_transfer>')
    return "\n".join(xml_lines)

# ── File Writer (splits into chunks of 5) ───────────────────
def write_output_files(objects, base_context="0.0001"):
    os.makedirs("CatProduct_output", exist_ok=True)
    chunks = [objects[i:i+5] for i in range(0, len(objects), 5)]
    for idx, chunk in enumerate(chunks, start=1):
        filename = f"02977.04.catproduct_auth.{base_context}-{idx}.vpmuuid_lst"
        filepath = os.path.join("CatProduct_output", filename)
        xml_content = generate_xml(chunk)
        with open(filepath, "w") as f:
            f.write(xml_content)
        print(f"✅ Created: {filepath}")

# ── Main callable for integration with main.py ──────────────
def run_manual_catproduct():
    dittios = input("Provide the dittios here (comma separated): ").strip().split(",")
    sql = build_sql_query(dittios)
    print("\n📜 Run this SQL in PROD DMA DB:\n")
    print(sql)

    print("\nNow enter mappings in format: <part_number> <uuid> --A")
    print("Enter 'done' when finished.")
    objects = []
    while True:
        line = input("> ").strip()
        if line.lower() == "done":
            break
        parts = line.split()
        if len(parts) >= 2:
            name = f"{parts[0]} --A"
            uuid = parts[1]
            objects.append((name, uuid))

    write_output_files(objects)
