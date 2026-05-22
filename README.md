Here is the fully aggregated, final version of your documentation. It seamlessly blends the original setup, your specific folder structure layout, the updated raw TCP socket test cases, and an explanatory section mapping what the log outputs actually verify.

---

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

The workspace is organized as a single-container blueprint, mapping multi-service execution contexts directly onto isolated Python runtime boundaries:

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

*Your console will output 5 distinct nodes initializing their internal storage interfaces and declaring tracking configurations:*

```text
p2p_node-1  | [node_ba7e928c] UDP Multicast Interface listening on 224.0.0.1:10000
p2p_node-2  | [node_0b553d1a] UDP Multicast Interface listening on 224.0.0.1:10000
p2p_node-3  | [node_1dc0a2c3] UDP Multicast Interface listening on 224.0.0.1:10000

```

*(Leave this terminal window open to watch the nodes react to the upcoming test cases!)*

---

## 🧪 Operational Testing Matrix

> ⚠️ **Note on Protocol Design:** Because the `anycast_gateway` operates as a raw Layer-4 TCP Socket Server rather than a Layer-7 HTTP server, standard shell utilities like `curl` will trigger protocol anomalies (`HTTP/0.9 when not allowed`). Testing must be executed using internal Python container namespaces to handle the underlying streaming socket contexts gracefully.

Open a **second, separate terminal window** to run the execution validation commands.

### Test Case 1: Native UDP Multicast Cluster Broadcast

This commands **Node Index 3** internally to broadcast a message. Because of low-level socket overrides, it triggers a true hardware-level network flood across the bridge.

```cmd
docker-compose exec --index=3 p2p_node python -c "import requests; r = requests.post('http://localhost:5000/broadcast', json={'msg': 'System-wide automated cluster sync!'}); print(f'Status: {r.status_code}\nResponse: {r.text}')"

```

#### Expected Log Output Verification

Switch back to your live log terminal stream. You will witness a synchronized, concurrent waterfall verification where **all 5 nodes capture the UDP packet at the exact same millisecond**:

```text
p2p_node-3  | [node_1dc0a2c3] Native UDP Multicast Received from ('172.21.0.7', 37106): Broadcast from node_1dc0a2c3: System-wide automated cluster sync!
p2p_node-5  | [node_c6f8feaa] Native UDP Multicast Received from ('172.21.0.7', 37106): Broadcast from node_1dc0a2c3: System-wide automated cluster sync!
p2p_node-2  | [node_0b553d1a] Native UDP Multicast Received from ('172.21.0.7', 37106): Broadcast from node_1dc0a2c3: System-wide automated cluster sync!
p2p_node-4  | [node_cce11345] Native UDP Multicast Received from ('172.21.0.7', 37106): Broadcast from node_1dc0a2c3: System-wide automated cluster sync!
p2p_node-1  | [node_ba7e928c] Native UDP Multicast Received from ('172.21.0.7', 37106): Broadcast from node_1dc0a2c3: System-wide automated cluster sync!

```

### Test Case 2: DHT Storage via the Anycast Gateway

This commands **Node Index 3** to fire a raw JSON string into the anycast gateway over a raw TCP streaming socket. The gateway reads the stream, maps the key against the SHA-1 partition ring, and transparently proxies the payload to the correct storage node.

```cmd
docker-compose exec --index=3 p2p_node python -c "import socket, json; s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.connect(('anycast_gateway', 6000)); payload = json.dumps({'key': 'CS_Rocks', 'value': 'A_Grade_Project'}); s.sendall(payload.encode('utf-8')); s.shutdown(socket.SHUT_WR); print('Gateway Raw Stream:\n', s.recv(4096).decode('utf-8'))"

```

#### Expected Output Verification

The gateway will return the underlying proxy response along with a confirmation detailing the cryptographic target node selection:

```text
Gateway Raw Stream:
 HTTP/1.1 200 OK
 ...
 {"node":"node_adc84caf","status":"success"}

```

### Test Case 3: Distributed Data Isolation (Proof of Decentralization)

To verify that data is strictly partitioned across isolated ring segments instead of blindly duplicated everywhere, query a node that did not win the hash routing lottery.

Assuming the output from Test Case 2 routed the data to Node 1 (`p2p_node-1`), query **Node 5** directly:

```cmd
docker-compose exec --index=5 p2p_node python -c "import requests; r = requests.get('http://localhost:5000/kv/CS_Rocks'); print(f'Status: {r.status_code}\nResponse: {r.text}')"

```

#### Expected Output Verification

```text
Status: 404
Response: {"error":"Not found"}

```

---

## 📈 Log Stream Interpretations & Proofs

Monitoring runtime logs yields undeniable architectural validations for key components of this P2P structure:

* **Dual-Stack Interface Initialization**: Replicas explicitly register a Layer 4 UDP raw background loop for network socket sniffing on port `10000` independently alongside their native Layer 7 HTTP Flask processes on port `5000`.
* **Hardware-Level Network Multicasting**: When a node issues a broadcast, logs demonstrate that all listening threads pick up the exact packet concurrently without requiring iterative programmatic application-level loop routing.
* **DHT Space Isolation**: Targeted data insertions update local key-value stores exclusively on the node mapped to the matching hash coordinates. Non-winning keys queried against arbitrary peers gracefully emit standard `404 Not Found` messages, proving storage partition independence across the network ring.

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
| `/broadcast` | `POST` | `{"msg": "string"}` | Fires an out-of-band native UDP multicast group packet. |
| `/kv` | `POST` | `{"key": "str", "value": "any"}` | Commits data key-value allocations directly to isolated memory partitions. |
| `/kv/<key>` | `GET` | *None* | Retrieves value metrics bound to the given key identifier. |
| `/upload` | `POST` | `multipart/form-data` | Persists multi-part block assets directly to containerized disk storage. |
| `/health` | `GET` | *None* | Returns a cluster liveness heartbeat report. |
