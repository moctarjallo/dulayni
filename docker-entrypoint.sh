#!/bin/bash
set -e

cleanup() {
    echo "Shutting down services..."
    kill $MCP_PID $API_PID 2>/dev/null || true
    wait
}

trap cleanup EXIT INT TERM

export PYTHONPATH="/app/src:/app:$PYTHONPATH"

# Set default environment if not specified
export DULAYNI_ENV=${DULAYNI_ENV:-"development"}
export DEBUG_TOOLS=${DEBUG_TOOLS:-"false"}

# Start MCP server (port 8001)
echo "Starting MCP server on port 8001..."
dulayni-server --server_host 0.0.0.0 --server_port 8001 > /proc/1/fd/1 2>/proc/1/fd/2 &
MCP_PID=$!

sleep 3

# Start FastAPI server (port 8002)
echo "Starting FastAPI server on port 8002..."
if [ "$DEBUG_TOOLS" = "true" ]; then
    dulayni-api --api_host 0.0.0.0 --api_port 8002 --debug-tools > /proc/1/fd/1 2>/proc/1/fd/2 &
else
    dulayni-api --api_host 0.0.0.0 --api_port 8002 > /proc/1/fd/1 2>/proc/1/fd/2 &
fi
API_PID=$!

echo "Both servers started. MCP PID: $MCP_PID, API PID: $API_PID"
echo "MCP server: http://0.0.0.0:8001"
echo "API server: http://0.0.0.0:8002"
echo "Environment: $DULAYNI_ENV"
echo "Debug tools: $DEBUG_TOOLS"

# Wait for both processes
wait
