import faiss
import pickle
import os

def check_index():
    if os.path.exists('data/faiss_index.bin'):
        index = faiss.read_index('data/faiss_index.bin')
        print(f"Index ntotal: {index.ntotal}")
    else:
        print("Index file not found")

    if os.path.exists('data/metadata.pkl'):
        with open('data/metadata.pkl', 'rb') as f:
            metadata = pickle.load(f)
            print(f"Metadata count: {len(metadata)}")
    else:
        print("Metadata file not found")

if __name__ == "__main__":
    check_index()
