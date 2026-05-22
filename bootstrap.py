# Import the main Flask application stack components from the local python layout
from flask import Flask, request, jsonify

# Create the master bootstrap registry context instance
app = Flask(__name__)
# Initialize a central, unique set to store active container location endpoint addresses
peers = set()

# Expose a registration network endpoint accepting inbound POST payloads from new peer containers
@app.route('/register', methods=['POST'])
def register_peer():
    # Deconstruct inbound content blocks smoothly while handling empty payloads cleanly
    data = request.get_json(force=True, silent=True) or {}
    # Extract the absolute address identifier string from the registration context mapping
    peer_url = data.get('url')
    # Validate content payload properties before committing values to the database set
    if peer_url:
        # Add the unique destination endpoint address string directly into the registry set
        peers.add(peer_url)
        # Respond back with a 200 OK code payload confirming a clean cluster registration sequence
        return jsonify({"status": "registered"}), 200
    # Block incomplete or corrupt registration profiles with an explicit error payload
    return jsonify({"error": "Invalid data"}), 400

# Expose a retrieval route mapping enabling peers to download the entire system cluster layout
@app.route('/peers', methods=['GET'])
def get_peers():
    # Serialize the registration set structure as an array payload to support clean JSON parsing
    return jsonify({"peers": list(peers)}), 200

# Main execution gate controlling service initialization profiles
if __name__ == '__main__':
    # Bind the bootstrap node engine on all local container interface layers at port 5000
    app.run(host='0.0.0.0', port=5000)