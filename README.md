# Decentralized P2P Network with Distributed Hash Table (DHT) & Native Multicast

This repository contains a containerized, decentralized peer-to-peer (P2P) storage and communication network built using Python, Flask, and Docker. The architecture features an automated topology registration protocol, a Distributed Hash Table (DHT) partition ring powered by cryptographic SHA-1 consistent hashing, and a true low-level Layer-4 UDP Multicast engine for out-of-band cluster synchronization.

---

## 🏗️ System Architecture Overview

The cluster is composed of three primary service boundaries running inside an isolated Docker virtual bridge network layer:

1. **Bootstrap Server Registry**: Acts as an initial discovery coordinator. It tracks active node endpoints via an automated liveness tracking table.
2. **Peer Nodes (`p2p_node`)**: Autonomously scaled replicas that handle decentralization mechanics. Each node runs a dual-stack configuration:
* **Layer 7 HTTP (Flask)**: Handles client actions, internal key-value (`/kv`) data access routing, and system broadcasts.
* **Layer 4 UDP Socket Interface**: Listens on a dedicated network interface to handle hardware-level multicast transmissions.


3. **Anycast Routing Gateway**: Exposes a unified single entry-point to route transaction payloads dynamically to the appropriate storage peer.

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

Monitor the unbuffered uncoordinated output stream of the peer node fleet to confirm that each independent replica successfully joined the multicast interface:

```cmd
docker-compose logs -f p2p_node

```

*Your console will output 5 distinct nodes initializing their internal storage interfaces and declaring tracking configurations:*

```text
p2p_node-1  | [node_ba7e928c] UDP Multicast Interface listening on 224.0.0.1:10000
p2p_node-2  | [node_0b553d1a] UDP Multicast Interface listening on 224.0.0.1:10000
p2p_node-3  | [node_1dc0a2c3] UDP Multicast Interface listening on 224.0.0.1:10000

```

---

## 🧪 Operational Testing Matrix

Because the core engine leverages `python:3.9-slim` base images to optimize production resource foot-printing, networking utilities like `curl` are omitted inside the container namespaces. Use the following explicit verification operations:

### Test Case A: Native UDP Multicast Cluster Broadcast

To trigger a true Layer-4 out-of-band broadcast without invoking point-to-point application forwarding loops, pass an inline Python execution request directly into the network namespace of **Node Index 3**:

```cmd
docker-compose exec --index=3 p2p_node python -c "import requests; r = requests.post('http://localhost:5000/broadcast', json={'msg': 'System-wide automated cluster sync!'}); print(f'Status: {r.status_code}\nResponse: {r.text}')"

```

#### Expected Log Output Verification

Switch back to your live `docker-compose logs -f p2p_node` terminal stream. You will witness a synchronized, concurrent waterfall verification where **all 5 nodes log capturing the UDP packet at the same millisecond**:

```text
p2p_node-3  | [node_1dc0a2c3] Native UDP Multicast Received from ('172.21.0.7', 37106): Broadcast from node_1dc0a2c3: System-wide automated cluster sync!
p2p_node-5  | [node_c6f8feaa] Native UDP Multicast Received from ('172.21.0.7', 37106): Broadcast from node_1dc0a2c3: System-wide automated cluster sync!
p2p_node-2  | [node_0b553d1a] Native UDP Multicast Received from ('172.21.0.7', 37106): Broadcast from node_1dc0a2c3: System-wide automated cluster sync!
p2p_node-4  | [node_cce11345] Native UDP Multicast Received from ('172.21.0.7', 37106): Broadcast from node_1dc0a2c3: System-wide automated cluster sync!
p2p_node-1  | [node_ba7e928c] Native UDP Multicast Received from ('172.21.0.7', 37106): Broadcast from node_1dc0a2c3: System-wide automated cluster sync!

```

---

## 🛠️ Low-Level Socket Blueprint

The underlying synchronization mechanics rely on Python's binary structural configuration layer to bridge communications between host architectures and the containerized virtual interfaces.

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