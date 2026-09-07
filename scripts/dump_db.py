import lancedb
import os

db = lancedb.connect('./lancedb_data')
if "memory_nodes" in db.list_tables():
    tbl = db.open_table("memory_nodes")
    data = tbl.to_pylist()
    print(f"--- TABLE CONTENTS ({len(data)} rows) ---")
    for i, row in enumerate(data):
        print(f"Row {i}: Source={row.get('metadata', {}).get('source')}, Content={row.get('content', '')[:50]}...")
else:
    print("Table 'memory_nodes' not found.")
