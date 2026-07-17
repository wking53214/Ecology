import os
import ollama
from datetime import datetime
import concurrent.futures
import time

class ActiveKnowledgeObject:
    def __init__(self, identity, content, timestamp):
        self.identity = identity
        self.content = content
        self.timestamp = timestamp
        self.date_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')

    def receive_message(self, message):
        relevance_response = ollama.chat(
            model='llama3.2:1b',
            messages=[
                {'role': 'system', 'content': 'You are a binary classifier. Output exactly YES if the data contains the answer to the query, or NO if it does not. No other text.'},
                {'role': 'user', 'content': 'Data: "The car is red."\nQuery: "What color is the vehicle?"'},
                {'role': 'assistant', 'content': 'YES'},
                {'role': 'user', 'content': 'Data: "The car is red."\nQuery: "How do I cook pasta?"'},
                {'role': 'assistant', 'content': 'NO'},
                {'role': 'user', 'content': f'Data: "{self.content}"\nQuery: "{message}"'}
            ],
            options={'temperature': 0.0, 'top_k': 1}
        )
        
        relevance = relevance_response['message']['content'].strip().upper()
        
        if "YES" in relevance:
            answer_response = ollama.chat(
                model='llama3.2:1b',
                messages=[
                    {'role': 'system', 'content': 'You are a strict text-extraction robot. Extract the exact sentence containing the answer. If the answer is not present, output exactly: UNKNOWN.'},
                    {'role': 'user', 'content': 'Data: "The car is red. It has four wheels."\nQuery: "What color is the vehicle?"'},
                    {'role': 'assistant', 'content': 'The car is red.'},
                    {'role': 'user', 'content': 'Data: "The car is red. It has four wheels."\nQuery: "Who makes the car?"'},
                    {'role': 'assistant', 'content': 'UNKNOWN'},
                    {'role': 'user', 'content': f'Data: "{self.content}"\nQuery: "{message}"'}
                ],
                options={'temperature': 0.0, 'top_k': 1}
            )
            
            reply = answer_response['message']['content'].strip()
            
            blacklist = ["UNKNOWN", "I couldn't find", "I didn't provide", "I can't provide", "I don't have", "If I had to guess"]
            is_blacklisted = any(phrase.lower() in reply.lower() for phrase in blacklist)
            
            if is_blacklisted:
                return

            if reply.lower() not in self.content.lower():
                print(f"[{self.identity} | MEMBRANE BLOCK: DEFENSE 2] Rejected String: '{reply}'")
                return
                
            if len(reply.split()) < 1:
                print(f"[{self.identity} | MEMBRANE BLOCK: DEFENSE 3] Rejected String: '{reply}'")
                return

            print(f"[{self.identity} | {self.date_str}] responding:\n{reply}\n")


def broadcast_to_ether(ecology_cluster, message):
    print(f"--- Broadcasting: '{message}' ---")
    start_time = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        executor.map(lambda obj: obj.receive_message(message), ecology_cluster)
    elapsed = time.perf_counter() - start_time
    print(f"[Telemetry] Broadcast completed in {elapsed:.4f} seconds.\n")


def ingest_directory(directory_path):
    ecology_cluster = []
    
    if not os.path.exists(directory_path):
        print(f"[System] Directory '{directory_path}' not found.")
        return ecology_cluster

    files = [f for f in os.listdir(directory_path) if f.endswith((".md", ".txt"))]
    
    for filename in files:
        filepath = os.path.join(directory_path, filename)
        file_timestamp = os.path.getmtime(filepath)
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
                raw_dna = file.read().strip()
        except Exception as e:
            print(f"[System] Skipping '{filename}' due to read error: {e}")
            continue

        segments = [segment.strip() for segment in raw_dna.split('\n\n') if segment.strip()]
        
        for index, segment in enumerate(segments):
            identity = f"{filename}[Cell-{index+1}]"
            cell = ActiveKnowledgeObject(identity=identity, content=segment, timestamp=file_timestamp)
            ecology_cluster.append(cell)
                
    ecology_cluster.sort(key=lambda x: x.timestamp, reverse=True)
            
    print(f"[System] Ecology initialized with {len(ecology_cluster)} active cells descended from {len(files)} parent structures.\n")
    return ecology_cluster


if __name__ == "__main__":
    ecology = ingest_directory("corpus")
    
    if not ecology:
        print("Add valid text or markdown files to the 'corpus' directory and try again.")
        exit()
        
    print("\n[System] The ecology is listening. Type 'exit' or 'quit' to shut down.")
    
    while True:
        try:
            user_query = input("\nBroadcast > ")
            
            if user_query.strip().lower() in ['exit', 'quit']:
                print("[System] Shutting down the ecology. Goodbye.")
                break
                
            if not user_query.strip():
                continue
                
            broadcast_to_ether(ecology, user_query)
            
        except KeyboardInterrupt:
            print("\n[System] Shutting down the ecology. Goodbye.")
            break
