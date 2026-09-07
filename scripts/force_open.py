import lancedb
import os

db_path = os.path.abspath("./lancedb_data")
db = lancedb.connect(db_path)

try:
    # Attempt direct access
    tbl = db.open_table("memory_nodes")
    print(f"SUCCESS: Table 'memory_nodes' opened directly.")
    print(f"Total rows: {len(tbl.to_arrow())}")
    
    # Verify we can actually read data
    data = tbl.to_arrow().to_pylist()
    if data:
        print(f"Sample metadata: {data[0].get('metadata')}")
except Exception as e:
    print(f"FAILED to open table directly: {e}")
    print("This confirms the folder exists but LanceDB cannot initialize the dataset.")
