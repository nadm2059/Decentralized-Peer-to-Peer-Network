# Decentralized P2P Network with Distributed Hash Table (DHT) & Native Multicast

This repository contains a containerized, decentralized peer-to-peer (P2P) storage and communication network built using Python, Flask, and Docker. The architecture features an automated topology registration protocol, a Distributed Hash Table (DHT) partition ring powered by cryptographic SHA-1 consistent hashing, and a true low-level Layer-4 UDP Multicast engine for out-of-band cluster synchronization.

---

## 🏗️ System Architecture Overview

The cluster is composed of three primary service boundaries running inside an isolated Docker virtual bridge network layer:

1. **Bootstrap Server Registry**: Acts as an initial discovery coordinator. It tracks active node endpoints via an automated liveness tracking table.


2. **Peer Nodes (`p2p_node`)**: Autonomously scaled replicas that handle decentralization mechanics. Each node runs a dual-stack configuration:


* **Layer 7 HTTP (Flask)**: Handles client actions, internal key-value (`/kv`) data access routing, and system broadcasts.


* **Layer 4 UDP Socket Interface**: Listens on a dedicated network interface to handle hardware-level multicast transmissions.




3. **Anycast Routing Gateway**: Exposes a unified single entry-point to route transaction payloads dynamically to the appropriate storage peer via a raw TCP engine running on port 6000.



---

## 📂 Repository Workspace Structure

```text
CECS327_DecentralizedP2PNetwork/
├── .history/               # Local VS Code automatic backup snapshots (Git-ignored)
├── anycast_router.py       # Layer-4 TCP socket proxy gateway routing engine
├── bootstrap.py            # Central coordinator for active peer liveness registry
├── node.py                 # Dual-stack L7 Flask API & L4 UDP Multicast cluster peer
├── Dockerfile              # Multi-stage image build recipe for Python slim runtimes
├── docker-compose.yml      # Orchestration layout managing network segments & scaling
└── README.md               # System architectural definitions & testing manuals

```

---

## 🚀 Getting Started (Windows Quick Start)

### Prerequisites

* Docker Desktop installed with Compose V2 support


* Windows Command Prompt (`cmd`) or PowerShell



### 1. Structure Cleanup & Initialization

To ensure lingering container network adapters or port definitions are fully cleared, purge your active workspace:

```cmd
docker-compose down --remove-orphans

```

### 2. Compile and Scale the Mesh Network

Spin up the orchestration layout and scale the peer nodes to **5 independent, isolated runtime replicas** in detached background execution mode:

```cmd
docker-compose up --build -d

```

### 3. Verify Cluster Initialization Streams

Monitor the unbuffered output stream of the peer node fleet to confirm that each independent replica successfully joined the multicast interface:

```cmd
docker-compose logs -f p2p_node

```

```text
p2p_node-1  | [node_b7098b10] UDP Multicast Interface listening on 224.0.0.1:10000
p2p_node-2  | [node_90aafda5] UDP Multicast Interface listening on 224.0.0.1:10000
p2p_node-3  | [node_830451dc] UDP Multicast Interface listening on 224.0.0.1:10000
p2p_node-4  | [node_d21730af] UDP Multicast Interface listening on 224.0.0.1:10000
p2p_node-5  | [node_95c1c9f5] UDP Multicast Interface listening on 224.0.0.1:10000

```

---

## 🧪 Operational Testing Matrix & Execution Traces

> ⚠️ **Note on Protocol Design:** Because the `anycast_gateway` operates as a raw Layer-4 TCP Socket Server rather than a Layer-7 HTTP server, standard shell utilities like `curl` trigger protocol anomalies (`HTTP/0.9 when not allowed`). Testing is executed using internal Python container namespaces to handle streaming socket contexts gracefully.
> 
> 

---

### Test Case 1: Native UDP Multicast Cluster Broadcast

#### Command Input

```cmd
docker-compose exec --index=3 p2p_node python -c "import requests; r = requests.post('http://localhost:5000/broadcast', json={'msg': 'System-wide automated cluster sync!'}); print(f'Status: {r.status_code}\nResponse: {r.text}')"

```

* **Input Meaning:** Commands container index 3 (`p2p_node-3`) to fire an internal HTTP POST request to its local `/broadcast` REST endpoint carrying a JSON payload.



#### Terminal Output

```text
Status: 200
Response: {"payload":"System-wide automated cluster sync!","status":"multicast_sent"}

```

* **Output Explanation:** Node 3's Flask server caught the trigger and opened a raw UDP datagram socket to transmit the payload to multicast IP group `224.0.0.1:10000`. HTTP Status `200` confirms that the socket call executed without network binding faults.



---

### Test Case 2: DHT Storage via the Anycast Proxy Gateway

#### Command Input

```cmd
docker-compose exec --index=3 p2p_node python -c "import socket, json; s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.connect(('anycast_gateway', 6000)); payload = json.dumps({'key': 'CS_Rocks', 'value': 'A_Grade_Project'}); s.sendall(payload.encode('utf-8')); s.shutdown(socket.SHUT_WR); print('Gateway Raw Stream:\n', s.recv(4096).decode('utf-8'))"

```

* **Input Meaning:** Connects a raw TCP streaming socket directly from Node 3 to `anycast_gateway:6000` and transmits key-value payload `{"key": "CS_Rocks", "value": "A_Grade_Project"}` down the wire.



#### Terminal Output

```text
Gateway Raw Stream:
 HTTP/1.1 200 OK
 Server: Werkzeug/3.1.8 Python/3.9.25
 Date: Sat, 15 Aug 2026 22:57:50 GMT
 Content-Type: application/json
 Content-Length: 44
 Connection: close

 {"node":"node_95c1c9f5","status":"success"}

```

* **Output Explanation:** The Anycast gateway intercepted the raw TCP stream, executed SHA-1 hashing on key `CS_Rocks`, computed the ring modulo coordinates ($\text{SHA1}(\text{Key}) \pmod 5$), and dynamically proxied the POST payload over an internal socket connection to the target container (`node_95c1c9f5`, which maps to `p2p_node-5`).



---

### Test Case 3: Distributed Partition Querying & Ownership Verification

#### Command Input

```cmd
docker-compose exec --index=5 p2p_node python -c "import requests; r = requests.get('http://localhost:5000/kv/CS_Rocks'); print(f'Status: {r.status_code}\nResponse: {r.text}')"

```

* **Input Meaning:** Dispatches a direct HTTP GET request to `/kv/CS_Rocks` on container index 5 (`p2p_node-5`).



#### Terminal Output

```text
Status: 200
Response: {"key":"CS_Rocks","node":"node_95c1c9f5","value":"A_Grade_Project"}

```

* **Output Explanation:** Container index 5 (`p2p_node-5`) holds node ID `node_95c1c9f5`. Because `node_95c1c9f5` was selected as the winning partition node during Test Case 2, it successfully returns the stored key-value pair from its local dictionary partition with an HTTP 200 OK status.



---

### Test Case 4: Process Memory Space & Isolation Inspection

#### Command Input

```cmd
docker-compose exec --index=5 p2p_node python -c "from node import kv_store; print('Node 5 Local Memory:', kv_store)"

```

* **Input Meaning:** Spawns an ad-hoc, secondary Python process inside container 5 to import the `node` module and print the `kv_store` dictionary directly from memory.



#### Terminal Output

```text
Node 5 Local Memory: {}

```

* **Output Explanation:** Returns an empty dictionary `{}` because `docker-compose exec python -c` creates an entirely new, isolated subshell execution process rather than reading the active Flask daemon's memory space. This demonstrates standard Operating System process boundary isolation within Linux container namespaces.



---

### Test Case 5: Real-Time Cluster Multicast & Routing Audit Logs

#### Command Input

```cmd
docker-compose logs -f p2p_node

```

* **Input Meaning:** Streams live unbuffered standard output logs from all 5 active peer node containers concurrently.



#### Cluster Output Stream

```text
p2p_node-3  | [node_830451dc] Native UDP Multicast Received from ('172.19.0.5', 55201): Broadcast from node_830451dc: System-wide automated cluster sync!
p2p_node-1  | [node_b7098b10] Native UDP Multicast Received from ('172.19.0.5', 55201): Broadcast from node_830451dc: System-wide automated cluster sync!
p2p_node-4  | [node_d21730af] Native UDP Multicast Received from ('172.19.0.5', 55201): Broadcast from node_830451dc: System-wide automated cluster sync!
p2p_node-5  | [node_95c1c9f5] Native UDP Multicast Received from ('172.19.0.5', 55201): Broadcast from node_830451dc: System-wide automated cluster sync!
p2p_node-2  | [node_90aafda5] Native UDP Multicast Received from ('172.19.0.5', 55201): Broadcast from node_830451dc: System-wide automated cluster sync!
p2p_node-3  | 127.0.0.1 - - [15/Aug/2026 22:57:25] "POST /broadcast HTTP/1.1" 200 -
p2p_node-5  | 172.19.0.4 - - [15/Aug/2026 22:57:50] "POST /kv HTTP/1.1" 200 -
p2p_node-5  | 127.0.0.1 - - [15/Aug/2026 22:58:00] "GET /kv/CS_Rocks HTTP/1.1" 200 -
p2p_node-5  | 172.19.0.8 - - [15/Aug/2026 22:58:53] "GET /kv/CS_Rocks HTTP/1.1" 200 -
p2p_node-5  | 172.19.0.8 - - [15/Aug/2026 23:00:14] "GET /kv/CS_Rocks HTTP/1.1" 200 -

```

#### Detailed Output Analysis

1. **Hardware-Level UDP Multicast Proof:** All 5 listening node threads captured the single broadcast packet from Node 3 (`172.19.0.5`) simultaneously on port `10000`, proving true out-of-band network multicasting without application-level iteration.


2. **Anycast Proxy Forwarding Trace:** `p2p_node-5` logged an incoming `POST /kv` request originating from IP `172.19.0.4` (the Anycast gateway container), proving that the TCP gateway calculated the correct target hash and successfully proxied the HTTP request.


3. **HTTP Query Tracking:** Subsequent `GET /kv/CS_Rocks` requests hit `p2p_node-5` directly from client IPs `127.0.0.1` and `172.19.0.8`, returning HTTP 200 responses for the owner node.



---

## 🛠️ Low-Level Socket Blueprint

### Core Multicast Receiver Binding (`node.py`)

```python
def run_udp_multicast_listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Force listener to capture traffic across all available network card bridges
    sock.bind(('0.0.0.0', 10000))
    
    # Standardized 4-byte binary block layout packing ("4s4s") 
    # Maps Multicast Group IP + INADDR_ANY interface boundaries explicitly
    mreq = struct.pack("4s4s", socket.inet_aton('224.0.0.1'), socket.inet_aton('0.0.0.0'))
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

```

### DHT Consistent Hashing Mechanics

Partition management utilizes modulo space reduction mappings derived from cryptographic SHA-1 signatures to isolate distinct key paths to uniform cluster storage locations:

$$\text{Target Ring Index} = \text{HexToInt}(\text{SHA1}(\text{Key})) \pmod{\text{Total Active Replicas}}$$

---

## 📂 Core API Specifications

| Route | Method | Payload Scheme | Description |
| --- | --- | --- | --- |
| `/broadcast` | `POST` | `{"msg": "string"}` | Fires an out-of-band native UDP multicast group packet.

 |
| `/kv` | `POST` | `{"key": "str", "value": "any"}` | Commits data key-value allocations directly to isolated memory partitions.

 |
| `/kv/<key>` | `GET` | *None* | Retrieves value metrics bound to the given key identifier.

 |
| `/upload` | `POST` | `multipart/form-data` | Persists multi-part block assets directly to containerized disk storage.

 |
| `/health` | `GET` | *None* | Returns a cluster liveness heartbeat report.

 |
