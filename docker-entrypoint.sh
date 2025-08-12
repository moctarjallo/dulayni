#!/bin/bash
set -e

# Function to cleanup on exit
cleanup() {
    echo "Shutting down services..."
    kill $MCP_PID $API_PID 2>/dev/null || true
    wait
}

# Set trap for cleanup
trap cleanup EXIT INT TERM

# Set Python path
export PYTHONPATH="/app/src:/app:$PYTHONPATH"

# Start MCP server in background
echo "Starting MCP server on port 8001..."
cd /app
python src/dulayni/mcp/server.py &
MCP_PID=$!

# Wait a moment for MCP server to start
sleep 3

# Start FastAPI server in background
echo "Starting FastAPI server on port 8002..."
cd /app
python src/dulayni/mcp/client.py &
API_PID=$!

# Wait for both processes
echo "Both servers started. MCP PID: $MCP_PID, API PID: $API_PID"
echo "MCP server: http://0.0.0.0:8001"
echo "API server: http://0.0.0.0:8002"

# Wait for either process to exit
wait
