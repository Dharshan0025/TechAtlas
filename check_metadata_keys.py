import pickle

def check_keys():
    with open('data/metadata.pkl', 'rb') as f:
        metadata = pickle.load(f)
        print(f"Keys: {list(metadata.keys())}")
        print(f"Type of keys: {type(list(metadata.keys())[0])}")

if __name__ == "__main__":
    check_keys()
