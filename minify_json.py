import json

with open('firebase-key.json', 'r') as f:
    data = json.load(f)
    # Dump to string with no whitespace
    minified = json.dumps(data, separators=(',', ':'))
    print("COPY THIS SINGLE LINE BELOW FOR RAILWAY VARIABLE:")
    print(minified)
