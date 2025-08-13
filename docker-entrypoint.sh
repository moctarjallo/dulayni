#!/bin/bash
set -e

# Function to cleanup on exit
cleanup() {
    echo "Shutting down services..."
    kill $MCP_PID $API_PID 2>/dev/null || true
    wait
}

trap cleanup EXIT INT TERM

export PYTHONPATH="/app/src:/app:$PYTHONPATH"

# Start MCP server (port 8001) and redirect its logs to Docker stdout
echo "Starting MCP server on port 8001..."
cd /app
python src/dulayni/mcp/server.py > /proc/1/fd/1 2>/proc/1/fd/2 &
MCP_PID=$!

sleep 3

# Start FastAPI server (port 8002) and redirect its logs to Docker stdout
echo "Starting FastAPI server on port 8002..."
cd /app
python src/dulayni/mcp/client.py > /proc/1/fd/1 2>/proc/1/fd/2 &
API_PID=$!

echo "Both servers started. MCP PID: $MCP_PID, API PID: $API_PID"
echo "MCP server: http://0.0.0.0:8001"
echo "API server: http://0.0.0.0:8002"

# Wait for both processes (so both logs stream)
wait

