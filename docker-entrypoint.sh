#!/bin/bash
set -e

cleanup() {
    echo "Shutting down services..."
    kill $MCP_PID 2>/dev/null || true
    wait
}

trap cleanup EXIT INT TERM

export PYTHONPATH="/app/src:/app:$PYTHONPATH"
export DULAYNI_ENV=${DULAYNI_ENV:-"development"}
export DEBUG_TOOLS=${DEBUG_TOOLS:-"false"}

# Enable ipdb debugging
if [ "$DEBUG_TOOLS" = "true" ]; then
    export PYTHONBREAKPOINT="ipdb.set_trace"
fi

# Start MCP server in background
echo "Starting MCP server on port 8001..."
dulayni-server --server_host 0.0.0.0 --server_port 8001 > /proc/1/fd/1 2>/proc/1/fd/2 &
MCP_PID=$!
sleep 3

# Start FastAPI server in FOREGROUND
echo "Starting FastAPI server on port 8002..."
if [ "$DEBUG_TOOLS" = "true" ]; then
    dulayni-api --api_host 0.0.0.0 --api_port 8002 --debug-tools
else
    dulayni-api --api_host 0.0.0.0 --api_port 8002
fi
