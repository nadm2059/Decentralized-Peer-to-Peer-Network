# Import socket to establish low-level point-to-point TCP infrastructure pipelines
import socket
# Import threading to manage multiple concurrent client proxy connections simultaneously
import threading
# Import hashlib to run SHA-1 calculations for the anycast consistent hash ring
import hashlib
# Import json to translate raw network byte streams into structured dictionary configurations
import json
# Import requests to pull cluster map information directly from the bootstrap registry
import requests

# Define the single external-facing access port representing the Anycast TCP Layer
ANYCAST_PORT = 6000
# Target locator configuration referencing the centralized cluster bootstrap registry location
BOOTSTRAP_URL = "http://bootstrap:5000"

# Generate a SHA-1 unique signature coordinate value from an entry storage identity string
def get_hash(key):
    # Convert string to bytes, execute SHA-1 hash, convert hex digest to numerical base-10 value
    return int(hashlib.sha1(key.encode()).hexdigest(), 16)

# Select the target storage node based on modular ring calculations
def get_responsible_node(key, nodes_list):
    # Guard against calculation exceptions when zero peer locations are active
    if not nodes_list: return None
    # Sort host layout addresses to guarantee matching hash placement consensus
    sorted_nodes = sorted(list(nodes_list))
    # Execute modulo math to map the lookup key signature cleanly down to a node index
    index = get_hash(key) % len(sorted_nodes)
    # Yield the exact node endpoint matching the computed hash ring coordinates
    return sorted_nodes[index]

# Retrieve the current system mapping dictionary straight from the bootstrap lookup service
def fetch_cluster_nodes():
    # Isolate network calls within an error handling boundary against transient connection faults
    try:
        # Dispatch a synchronous GET request to pull the complete peer tracking registry array
        r = requests.get(f"{BOOTSTRAP_URL}/peers", timeout=2)
        # Parse out and return the raw node array structure extracted from the JSON response
        return r.json().get('peers', [])
    # Catch connectivity exceptions smoothly, returning an empty set to keep the loop alive
    except:
        # Provide an empty array reference back if the bootstrap endpoint is temporarily offline
        return []

# Thread handler to intercept client TCP socket streams and execute inline anycast routing
def client_proxy_handler(client_socket):
    """Parses raw TCP payload context and performs dynamic inline routing."""
    # Wrap the entire proxy session within an exception intercept boundary to isolate data faults
    try:
        # Extract the raw data packet payload block arriving across the active client TCP channel
        request_data = client_socket.recv(4096).decode('utf-8')
        # Reconstruct the raw text stream character sequences back into an editable JSON dictionary
        payload = json.loads(request_data)
        # Isolate the explicit lookup key tracking token assigned to the payload payload
        key = payload.get("key")
        
        # Download the latest system node layout configuration metrics from the registry
        nodes = fetch_cluster_nodes()
        # Compute the destination host location using the SHA-1 hash utility algorithm
        target_node_url = get_responsible_node(key, nodes)
        
        # Deny request processing if all storage nodes are unreachable
        if not target_node_url:
            # Alert the client by writing a structured JSON failure down the socket connection
            client_socket.send(json.dumps({"error": "No available DHT nodes"}).encode('utf-8'))
            # Terminate execution because no physical target is available to forward the data
            return
            
        # Parse out the container's raw virtual hostname from the URL schema configuration
        # converts 'http://node_host:5000' -> 'node_host'
        target_host = target_node_url.replace("http://", "").split(":")[0]
        
        # Construct an out-of-band point-to-point TCP stream connection targeting the node host
        backend_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Terminate the raw socket configuration handshake targeting the peer node on port 5000
        backend_sock.connect((target_host, 5000))
        
        # Format the payload into an HTTP/1.1 REST syntax string for the downstream backend server
        http_request = (
            f"POST /kv HTTP/1.1\r\n"
            f"Host: {target_host}:5000\r\n"
            f"Content-Type: application/json\r\n"
            f"Content-Length: {len(request_data)}\r\n"
            f"Connection: close\r\n\r\n"
            f"{request_data}"
        )
        # Dispatch the raw serialized byte stream string out across the node network connection
        backend_sock.sendall(http_request.encode('utf-8'))
        
        # Capture the final confirmation data returned from the processing storage node container
        response = backend_sock.recv(4096)
        # Relay the response data directly back up the original client pipeline connection
        client_socket.sendall(response)
        
        # Shutdown backend connection channels to recycle operating system file descriptors
        backend_sock.close()
    # Intercept decoding, network, or structural calculation failures during processing
    except Exception as e:
        # Attempt to inform the client of the proxy failure before severing the channel
        try: client_socket.send(json.dumps({"error": str(e)}).encode('utf-8'))
        # Block sub-exceptions if the client drops connection prematurely
        except: pass
    # Guarantee execution of cleanup logic regardless of success or intercept metrics
    finally:
        # Close out the primary user client socket connection channel cleanly
        client_socket.close()

# Core system execution setup running the primary TCP server mapping engine
def main():
    # Instantiate an IPv4 stream-based socket configuration bound to the TCP protocol stack
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Configure the interface layer to support instant binding recycling for rapid hot reboots
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Bind the socket interface to accept traffic across all active system adapters on port 6000
    server.bind(('0.0.0.0', ANYCAST_PORT))
    # Listen for connections, setting a kernel back-log queue boundary limit of 128 items
    server.listen(128)
    # Log an infrastructure receipt stating that the Anycast TCP Engine is ready
    print(f"[Anycast TCP Engine] Server running on port {ANYCAST_PORT}...", flush=True)
    
    # Enter an execution loop to accept inbound socket handshakes continuously
    while True:
        # Halt execution block until an inbound connection stream hits the interface
        client_sock, addr = server.accept()
        # Delegate the socket stream directly out to a worker daemon thread to ensure non-blocking scalability
        threading.Thread(target=client_proxy_handler, args=(client_sock,), daemon=True).start()

# Conditional entry check to boot the gateway infrastructure only when run directly
if __name__ == '__main__':
    # Launch the main anycast routing daemon routine loop
    main()