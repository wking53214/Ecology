import lancedb
import os

def initialize_db():
    db_path = "./lancedb_data"
    table_name = "memory_nodes"
    
    if not os.path.exists(db_path):
        os.makedirs(db_path)
        
    db = lancedb.connect(db_path)
    
    if table_name not in db.table_names():
        print(f"Creating new table: {table_name}")
        db.create_table(
            table_name, 
            data=[{"vector": [0.0]*384, "content": "bootstrap", "metadata": {"source": "init"}}]
        )
        print("Table initialized successfully.")
    else:
        print(f"Table '{table_name}' already exists.")

if __name__ == "__main__":
    initialize_db()
