import requests
import json
import os
from tqdm import tqdm

# Configuration
MAX_SNAPSHOT_ID = 25640
NODE_ID = 1  # 1 for odd numbers, 2 for even numbers
IPFS_API_URL = 'http://127.0.0.1:5001/api/v0'
DATA_DIR = 'data'  # Directory to save JSON files

# Ensure the data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Output files
success_log = "successful_operations.log"
error_log = "error_operations.log"

# Helper function to log success
def log_success(snapshot_id, cid):
    with open(success_log, 'a') as file:
        file.write(f"SNAPSHOT_ID: {snapshot_id}, CID: {cid}\n")

# Helper function to log errors
def log_error(snapshot_id, error_message):
    with open(error_log, 'a') as file:
        file.write(f"SNAPSHOT_ID: {snapshot_id}, ERROR: {error_message}\n")

# Determine starting point based on NODE_ID
if NODE_ID == 1:
    start_id = 1  # Odd numbers start from 1
elif NODE_ID == 2:
    start_id = 2  # Even numbers start from 2
else:
    raise ValueError("NODE_ID must be either 1 (odd) or 2 (even)")

# Calculate total iterations for progress bar
total_iterations = (MAX_SNAPSHOT_ID - start_id) // 2 + 1

# Process SNAPSHOT_IDs based on NODE_ID with a progress bar
for snapshot_id in tqdm(range(start_id, MAX_SNAPSHOT_ID + 1, 2), total=total_iterations, desc="Processing Snapshots"):
    url = f"https://arkivo.art/snapshots/{snapshot_id}"
    try:
        # Fetch the JSON file
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Write the JSON content to a file in the data directory
        json_content = response.json()
        json_filename = os.path.join(DATA_DIR, f"snapshot_{snapshot_id}.json")
        with open(json_filename, 'w') as json_file:
            json.dump(json_content, json_file)
        
        # Add the file to IPFS
        with open(json_filename, 'rb') as file_to_add:
            files = {'file': file_to_add}
            ipfs_response = requests.post(f"{IPFS_API_URL}/add", files=files)
            ipfs_response.raise_for_status()
            cid = ipfs_response.json()['Hash']
        
        # Log the successful operation
        log_success(snapshot_id, cid)
        
        # Delete the file after successful addition to IPFS
        os.remove(json_filename)
        
    except requests.exceptions.RequestException as e:
        # Log any requests-related errors
        log_error(snapshot_id, str(e))
        
    except Exception as e:
        # Log any other errors
        log_error(snapshot_id, str(e))

print(f"Process completed. Check {success_log} and {error_log} for details.")
