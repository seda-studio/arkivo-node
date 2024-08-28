import requests
import ipfshttpclient
import json

# Configuration
MAX_SNAPSHOT_ID = 25640
NODE_ID = 1  
IPFS_NODE_ADDRESS = '/dns/localhost/tcp/5001/http'

# Initialize IPFS client
client = ipfshttpclient.connect(IPFS_NODE_ADDRESS)

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

# Process SNAPSHOT_IDs based on NODE_ID
for snapshot_id in range(start_id, MAX_SNAPSHOT_ID + 1, 2):
    url = f"https://arkivo.art/snapshots/{snapshot_id}"
    try:
        # Fetch the JSON file
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Write the JSON content to a temporary file
        json_content = response.json()
        json_filename = f"snapshot_{snapshot_id}.json"
        with open(json_filename, 'w') as json_file:
            json.dump(json_content, json_file)
        
        # Add the file to IPFS
        result = client.add(json_filename)
        cid = result['Hash']
        
        # Log the successful operation
        log_success(snapshot_id, cid)
        
    except requests.exceptions.RequestException as e:
        # Log any requests-related errors
        log_error(snapshot_id, str(e))
        
    except Exception as e:
        # Log any other errors
        log_error(snapshot_id, str(e))

print(f"Process completed. Check {success_log} and {error_log} for details.")
