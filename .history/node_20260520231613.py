# Import the os module to fetch runtime environment variables from Docker
import os
# Import sys to access system-specific parameters and functions if needed
import sys
# Import time to manage polling intervals, backoffs, and loop delays
import time
# Import uuid to generate distinct identifiers for fallback node initializations
import uuid
# Import socket to handle low-level network communications and IP resolutions
import socket
# Import struct to pack Python values into bytes for binary C-style network operations
import struct
# Import requests to handle synchronous HTTP communication with the bootstrap server
import requests
# Import threading to spawn parallel background worker daemons for concurrent tasks
import threading
# Import hashlib to access the cryptographic SHA-1 algorithm for DHT math
import hashlib
# Import Flask components to parse payloads, route endpoints, and serve static assets
from flask import Flask, request, jsonify, send_from_directory

# Instantiate the main Flask application context for this peer node
app = Flask(__name__)

# --- IDENTITY & NETWORK SETUP ---
# Assign a unique node ID from environment variables, defaulting to a randomly sliced UUID
NODE_ID = os.getenv("NODE_ID", f"node_{str(uuid.uuid4())[:8]}")
# Resolve and capture the current container's virtual network hostname
MY_HOSTNAME = socket.gethostname()
# Convert the resolved hostname into its standard dot-decimal local IP address string
MY_IP = socket.gethostbyname(MY_HOSTNAME)
# Define the constant internal execution port mapping for the web server instance
MY_PORT = 5000
# Construct the local endpoint URI template to register within the cluster topology
MY_URL = f"http://{MY_HOSTNAME}:{MY_PORT}"
# Fetch the absolute bootstrap orchestration endpoint from the underlying network environment
BOOTSTRAP_URL = os.getenv('BOOTSTRAP_URL', 'http://bootstrap:5000')

# --- LOW-LEVEL MULTICAST (UDP) CONFIGURATION ---
# Define a standard IPv4 Local Scope Multicast group address for out-of-band packet delivery
MULTICAST_GROUP = '224.0.0.1'
# Assign a dedicated port number exclusively for receiving raw UDP group broadcasts
MULTICAST_PORT = 10000

# Initialize an empty set to keep a unique collection of all identified network endpoints
peers = set()
# Initialize an empty tracking list to hold available nodes verified by active health audits
active_peers = list()

# --- PERSISTENCE & KV ENGINE ---
# Dynamic path configuration ensuring each unique node isolates its filesystem workspace
STORAGE_DIR = f"./storage/{NODE_ID}"
# Create the local workspace directory recursively if it is absent from the host layout
os.makedirs(STORAGE_DIR, exist_ok=True)
# Initialize a thread-safe Python dictionary to act as the in-memory decentralized partition
kv_store = {}

# ==========================================
# DHT MECHANICS (SHA-1)
# ==========================================
# Compute a cryptographic SHA-1 signature of a key and format it as a large base-10 integer
def get_hash(key):
    # Encode key string to UTF-8, hash it, generate hex digest, and parse as base-16 integer
    return int(hashlib.sha1(key.encode()).hexdigest(), 16)

# Select the responsible destination storage host based on modulo math consistent coordinates
def get_responsible_node(key, nodes_list):
    # Fallback safe-guard returning Null if the target cluster reference map is currently blank
    if not nodes_list:
        # Halt execution of coordinate mapping since zero active nodes are reachable
        return None
    # Sort host configurations to enforce identical cluster-wide consensus on ring layout
    sorted_nodes = sorted(list(nodes_list))
    # Map the huge SHA-1 key integer down to a valid ring index using the modulo operator
    index = get_hash(key) % len(sorted_nodes)
    # Extract and return the target location string assigned to the computed coordinate index
    return sorted_nodes[index]

# ==========================================
# MULTICAST LAYER (UDP SOCKET LISTENER)
# ==========================================
# Execution loop monitoring a low-level UDP interface for native hardware broadcasts
def run_udp_multicast_listener():
    """Binds to a raw UDP socket to handle network-layer multicast payloads natively."""
    # Instantiate a low-level IPv4, connectionless datagram socket using the UDP protocol
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    # Adjust socket settings to allow instant port reuse, preventing "Address already in use" errors
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Bind the socket interface to monitor any available network adapter on the multicast port
    sock.bind(('', MULTICAST_PORT))
    
    # Pack the multicast IP address and interface flag into a standard 8-byte C-struct format
    mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
    # Issue an explicit IP level kernel command to join the specified multicast network group
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    
    # Log an absolute startup receipt straight to the unbuffered Docker console container stream
    print(f"[{NODE_ID}] UDP Multicast Interface listening on {MULTICAST_GROUP}:{MULTICAST_PORT}", flush=True)
    
    # Enter an infinite runtime execution loop to continuously block and process incoming packets
    while True:
        # Protect individual packet parsing executions inside a retry block against transport exceptions
        try:
            # Block thread and receive an unbuffered packet stream payload up to a 1024 byte window
            data, addr = sock.recvfrom(1024)
            # Reconstruct the raw binary byte arrays back into a clear, editable text format
            message = data.decode('utf-8')
            # Output the received string along with the originating sender's IP and transient port
            print(f"[{NODE_ID}] Native UDP Multicast Received from {addr}: {message}", flush=True)
        # Catch network driver or decoding interruptions gracefully without killing the main thread
        except Exception as e:
            # Write out the structural failure to stdout to streamline ongoing debugging steps
            print(f"Multicast error: {e}", flush=True)

# Expose a gateway endpoint enabling external HTTP entities to trigger an internal network broadcast
@app.route('/broadcast', methods=['POST'])
def send_multicast_broadcast():
    """Triggers a single UDP out-of-band group packet broadcast."""
    # Parse the inbound HTTP payload safely, falling back to an empty collection on null values
    data = request.get_json(force=True, silent=True) or {}
    # Extract the payload string message value, supplying an obvious default message if missing
    msg = data.get("msg", "Default Multicast Echo")
    
    # Construct a raw IPv4 connectionless UDP datagram socket for immediate outbound transmission
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    # Set Time-To-Live (TTL) to 2, ensuring packets clear the local container bridge network boundaries
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    # Push the encoded text payload down the UDP interface to the destination multicast group
    sock.sendto(f"Broadcast from {NODE_ID}: {msg}".encode('utf-8'), (MULTICAST_GROUP, MULTICAST_PORT))
    # Return a structured JSON response to the caller verifying execution success
    return jsonify({"status": "multicast_sent", "payload": msg}), 200

# ==========================================
# STORAGE & ANYCAST ROUTING GATEWAYS
# ==========================================
# Endpoint exposing a liveness check to keep tracking maps clean
@app.route('/health', methods=['GET'])
def health():
    # Return a status payload to confirm the node's server loop is operational
    return jsonify({"status": "alive", "node": NODE_ID}), 200

# Endpoint to store a key-value pair directly within this node's local dictionary partition
@app.route('/kv', methods=['POST'])
def handle_kv_post():
    # Parse incoming payload data cleanly while suppressing structural content errors
    data = request.get_json(force=True, silent=True) or {}
    # Isolate the lookup identity token string from the execution payload map
    key = data.get('key')
    # Extract the payload data object associated directly with the tracking key token
    value = data.get('value')
    # Validate payload parameters to block incomplete schema registrations
    if not key or value is None:
        # Respond with an explicit 400 Bad Request status code to notify the calling client
        return jsonify({"error": "Bad schema"}), 400

    # Write data straight into the active memory allocation tracking dictionary
    kv_store[key] = value
    # Provide confirmation payload identifying exactly which node committed the storage operation
    return jsonify({"status": "success", "node": NODE_ID})

# Endpoint to fetch data values back out of this node's local store
@app.route('/kv/<key>', methods=['GET'])
def handle_kv_get(key):
    # Attempt to locate and extract the requested entry from the dictionary
    value = kv_store.get(key)
    # Handle lookups for missing records to prevent runtime script crashes
    if value is None:
        # Return a structured 404 status object back downstream to the calling connection
        return jsonify({"error": "Not found"}), 404
    # Package and return the entry metrics alongside the identity of this retrieval host
    return jsonify({"key": key, "value": value, "node": NODE_ID})

# Expose a endpoint managing multi-part form payloads for block data persistence
@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if a file payload exists in the incoming multipart file dictionary
    if 'file' not in request.files: return jsonify({"error": "No file"}), 400
    # Isolate the active file target pointer from the uploaded context dictionary
    file = request.files['file']
    # Persist the file safely to disk by stitching together the storage root with the filename
    file.save(os.path.join(STORAGE_DIR, file.filename))
    # Output an operational confirmation detailing the target storage node name
    return jsonify({"status": "saved", "node": NODE_ID})

# ==========================================
# RECOVERY & MESH TOPOLOGY SYNCHRONIZATION
# ==========================================
# Routine to handle registration handshake actions with the bootstrap server on cold starts
def register_with_bootstrap():
    # Continue execution indefinitely until a handshake registration sequence completes
    while True:
        # Wrap connection attempts inside a try block to handle bootstrap server unavailability
        try:
            # Issue a POST handshake payload containing this node's registration string
            response = requests.post(f"{BOOTSTRAP_URL}/register", json={"url": MY_URL}, timeout=5)
            # Break out of the execution loop once the registry answers with a 200 OK status
            if response.status_code == 200:
                # Terminate the retry loop now that registration is successful
                break
        # Trap transport faults safely to prevent premature worker thread crashes
        except Exception:
            # Pause execution for 3 seconds before issuing an additional registration request
            time.sleep(3)

# Background execution loop to synchronize the local tracking table with the bootstrap node
def check_health_loop():
    # Declare list alterations as global to mutate values outside the scope of this function
    global active_peers
    # Continuously poll the registry to dynamically capture updates to the cluster layout
    while True:
        # Wait 5 seconds between synchronization sweeps to conserve network resources
        time.sleep(5)
        # Protect registry download routines against unexpected dropped connections
        try:
            # Query the bootstrap peer registry to fetch an updated snapshot of all active nodes
            resp = requests.get(f"{BOOTSTRAP_URL}/peers", timeout=2)
            # Process payload metrics if the response arrives intact
            if resp.status_code == 200:
                # Map the updated node registration list straight to our active tracker variable
                active_peers = resp.json().get('peers', [])
        # Silently absorb communication dropouts to maintain system uptime
        except Exception:
            # Pass over routing failures to keep background tracking threads active
            pass

# Main application execution boundary matching directly on script runtime context execution
if __name__ == '__main__':
    # Initialize the low-level UDP multicast group listener thread as an asynchronous daemon
    threading.Thread(target=run_udp_multicast_listener, daemon=True).start()
    # Initialize the background bootstrap registration sequence in an independent worker thread
    threading.Thread(target=register_with_bootstrap, daemon=True).start()
    # Initialize the dynamic heartbeat synchronization loop as a concurrent daemon task
    threading.Thread(target=check_health_loop, daemon=True).start()
    # Bind and run the web server across all internal network adapters on port 5000
    app.run(host='0.0.0.0', port=MY_PORT)