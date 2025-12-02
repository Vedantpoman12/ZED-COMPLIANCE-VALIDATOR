import pickle
import json

METADATA_FILE = "gst_metadata.pkl"

try:
    with open(METADATA_FILE, "rb") as f:
        data = pickle.load(f)

    print(f"Successfully loaded metadata from '{METADATA_FILE}'.")
    print(f"Total documents processed: {len(data)}\n")
    
    print(json.dumps(data, indent=2))

except FileNotFoundError:
    print(f"Error: Could not find file '{METADATA_FILE}'.")
    print("Have you run the main script yet?")
except Exception as e:
    print(f"An error occurred: {e}")