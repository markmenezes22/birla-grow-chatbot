import json
import os
import sys

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.data_pipeline.chunker import chunk_all_funds

def dump_chunks():
    data_dir = os.path.join(project_root, 'data')
    raw_file = os.path.join(data_dir, 'raw_scraped_data.json')
    chunks_file = os.path.join(data_dir, 'chunks.json')
    
    if not os.path.exists(raw_file):
        print(f"Error: {raw_file} not found.")
        return
        
    with open(raw_file, 'r', encoding='utf-8') as f:
        scraped_data = json.load(f)
        
    documents = chunk_all_funds(scraped_data)
    
    # Convert LangChain Documents to dicts for JSON serialization
    chunks_data = []
    for doc in documents:
        chunks_data.append({
            "content": doc.page_content,
            "metadata": doc.metadata
        })
        
    with open(chunks_file, 'w', encoding='utf-8') as f:
        json.dump(chunks_data, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully wrote {len(chunks_data)} chunks to {chunks_file}")

if __name__ == "__main__":
    dump_chunks()
