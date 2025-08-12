# Dulayni Deployment Guide

This guide covers how to deploy and use the dulayni RAG agent system with Docker.

## Architecture

The dulayni system consists of:
1. **Main dulayni server**: Contains both the FastAPI server (port 8002) and MCP server (port 8001)
2. **dulayni-client**: Separate CLI client that connects to the server via HTTP API

## Docker Deployment

### Prerequisites

1. Docker and Docker Compose installed
2. OpenAI API key

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your_org/dulayni.git
   cd dulayni
   ```

2. **Set up environment**:
   ```bash
   # Create .env file
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   
   # Create data directory
   mkdir -p data
   ```

3. **Build and start the services**:
   ```bash
   docker-compose up --build
   ```

4. **Verify services are running**:
   ```bash
   # Check API server
   curl http://localhost:8002/health
   
   # Check MCP server (should return MCP protocol info)
   curl http://localhost:8001/mcp
   ```

### Using the Services

#### Via dulayni-client (Recommended)

1. **Install the client** (separate project):
   ```bash
   cd dulayni_client
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```

2. **Use interactive mode**:
   ```bash
   dulayni-client -k $OPENAI_API_KEY --api_url http://localhost:8002/run_agent
   ```

3. **Use batch mode**:
   ```bash
   dulayni-client -k $OPENAI_API_KEY -q "What's 5 + 3 * 2?" --api_url http://localhost:8002/run_agent
   ```

#### Via Direct API Calls

```bash
curl -X POST "http://localhost:8002/run_agent" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "react",
    "role": "user",
    "model": "gpt-4o-mini",
    "content": "What is 5 + 3 * 2?",
    "system_prompt": "You are a helpful math assistant",
    "thread_id": "test-123"
  }'
```

## Configuration

### MCP Servers

Edit `config/mcp_servers.json` to configure MCP tool servers:

```json
{
  "mcpServers": {
    "default": {
      "url": "http://127.0.0.1:8001/mcp",
      "transport": "streamable_http"
    }
  }
}
```

### Model Settings

Edit `config/model_config.json` for default model settings:

```json
{
    "model_name": "gpt-4o-mini",
    "role": "user",
    "system_prompt": "You are a helpful agent"
}
```

## Development

### Adding Custom MCP Tools

1. Edit `src/dulayni/mcp/server.py`:
   ```python
   @mcp.tool()
   def my_custom_tool(param: str) -> str:
       """Description of your tool"""
       return f"Processed: {param}"
   ```

2. Rebuild the Docker container:
   ```bash
   docker-compose up --build
   ```

### Running Locally (Development)

```bash
# Terminal 1: Start MCP server
python src/dulayni/mcp/server.py

# Terminal 2: Start API server
python src/dulayni/mcp/client.py

# Terminal 3: Use client
cd dulayni_client
dulayni-client -k $OPENAI_API_KEY --api_url http://localhost:8002/run_agent
```

## Production Considerations

1. **Environment Variables**: Use proper secrets management instead of `.env` files
2. **Persistence**: Mount volumes for persistent data storage
3. **Scaling**: Consider running multiple instances behind a load balancer
4. **Monitoring**: Add health checks and monitoring
5. **Security**: Use HTTPS and proper authentication in production

## Troubleshooting

### Common Issues

1. **Connection refused**: Check if services are running with `docker-compose ps`
2. **OpenAI API errors**: Verify your API key is set correctly
3. **MCP tools not working**: Check MCP server logs with `docker-compose logs dulayni`

### Logs

View service logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f dulayni
```

### Health Checks

```bash
# API server health
curl http://localhost:8002/health

# MCP server status
curl http://localhost:8001/mcp
```
