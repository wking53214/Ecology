import lancedb
import os

db_path = os.path.abspath("./lancedb_data")
db = lancedb.connect(db_path)

if "memory_nodes" in db.list_tables():
    tbl = db.open_table("memory_nodes")
    # Get total count of rows
    count = len(tbl.to_arrow())
    print(f"DATABASE VERIFICATION: Table 'memory_nodes' found at {db_path}")
    print(f"Total rows in table: {count}")
    if count > 0:
        print("Sample row:", tbl.to_arrow().to_pylist()[0].get('metadata'))
else:
    print("CRITICAL: Table 'memory_nodes' not found in database.")
