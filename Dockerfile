# Pull an official, optimized lightweight Python base image to minimize compilation footprint size
FROM python:3.9-slim

# Establish an absolute workspace directory track path within the internal container boundary
WORKDIR /app

# Run pip dependency adjustments, explicitly bypassing local disk caching to keep layers light
RUN pip install --no-cache-dir flask requests

# Mirror the entire immediate project workspace structure straight across into the container file tree
COPY . .

# Inform the Docker daemon that the application server loop exposes port 5000 internally
EXPOSE 5000
# Inform the Docker daemon that the Anycast reverse proxy pipeline operates across port 6000
EXPOSE 6000
# Explicitly document that the native low-level UDP multicast listening thread monitors port 10000
EXPOSE 10000/udp