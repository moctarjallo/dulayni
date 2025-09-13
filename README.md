

# dulayni-client

A CLI client and Python library for interacting with dulayni RAG agents via API with support for multiple authentication methods.

---

## Installation

1. **Clone the repository**:

    ```bash
    git clone https://github.com/moctarjallo/dulayni-client.git
    cd dulayni-client
    ```

2. **Ensure Python 3.12 is installed**:

    ```bash
    python --version  # should output 3.12.x
    ```

3. **Create a virtual environment & install dependencies**:

    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install -e .
    ```

4. **Initialize your project**:

    ```bash
    dulayni init
    ```

---

## Authentication Methods

The dulayni-client supports two authentication methods:

### 1. WhatsApp Authentication
1. **Request Verification**: Client sends phone number to `/auth` endpoint
2. **Receive Code**: Server sends 4-digit verification code via WhatsApp
3. **Verify Code**: Client submits the code to `/verify` endpoint
4. **Get Token**: Server returns authentication token for API access
5. **Make Queries**: All subsequent queries include the auth token

### 2. Dulayni API Key Authentication
1. **Provide API Key**: Set your Dulayni API key (starts with `sk-`)
2. **Automatic Authentication**: No verification code needed
3. **Make Queries**: All queries include the API key in headers

---

## Quick Start

### Project Initialization

Initialize a new dulayni project:

```bash
dulayni init
```

This will:
- Set up Git repository (if not already present)
- Create configuration files
- Set up FRPC tunneling for MCP servers
- Guide you through authentication setup

### Authentication Setup

During initialization, you'll choose between:
1. WhatsApp authentication (requires phone number)
2. Dulayni API key authentication (requires API key)

---

## Usage

### As a Library

```python
from dulayni import DulayniClient

# Initialize with WhatsApp authentication
client = DulayniClient(
    phone_number="+1234567890",
    api_url="http://localhost:8002"
)

# Or initialize with Dulayni API key
client = DulayniClient(
    dulayni_api_key="sk-your-api-key-here",
    api_url="http://localhost:8002"
)

# Authenticate (WhatsApp only - will prompt for verification code)
def get_verification_code():
    return input("Enter 4-digit verification code: ")

client.request_verification_code()
code = get_verification_code()
client.verify_code(code)

# Now you can make queries
response = client.query("What's the weather like?")
print(response)

# Check account balance (WhatsApp authentication only)
balance = client.get_balance()
print(f"Account balance: {balance['balance']:.2f}")

# Stream responses
for message in client.query_stream("Tell me a story"):
    print(message["content"])
```

---

### CLI Usage

#### Project Initialization

```bash
dulayni init
```

#### Interactive Mode

Start an interactive REPL:

```bash
dulayni run
```

#### Batch Query Mode

Run a single query non-interactively:

```bash
dulayni run -q "What's (3 + 5) x 12?" --print_mode rich
```

#### Check Account Balance

```bash
dulayni balance
```

#### Check Project Status

```bash
dulayni status
```

#### Logout (Clear WhatsApp Session)

```bash
dulayni logout
```

---

### CLI Options for `dulayni run`

* `-m, --model`: Model name (default: `gpt-4o-mini`)
* `-p, --phone-number`: Your phone number for authentication
* `-k, --dulayni-key`: Dulayni API key for authentication
* `-q, --query`: Query string for batch mode
* `-md, --markdown`: Path to markdown file containing query
* `-a, --agent_type`: Agent type (`react` or `deep_react`, default: `react`)
* `--api_url`: Dulayni server URL
* `--thread_id`: Thread ID for conversation continuity
* `--print_mode`: Output format (`json` or `rich`)
* `--system_prompt`: Custom system prompt
* `--stream`: Enable streaming mode
* `--check-balance`: Check account balance before query
* `--skip-frpc`: Skip FRPC container check

---

## Project Structure

```
dulayni-client/
├── config/
│   ├── config.json          # Main configuration
│   ├── development.json     # Development environment config
│   └── production.json      # Production environment config
├── src/dulayni/
│   ├── auth/                # Authentication management
│   ├── config/              # Configuration management
│   ├── infrastructure/      # Infrastructure utilities
│   ├── mcp/                 # Model Context Protocol integration
│   ├── project/             # Project management
│   ├── client.py            # Main client class
│   ├── cli.py               # CLI implementation
│   └── exceptions.py        # Custom exceptions
└── .dulayni_key             # API key storage (if using Dulayni auth)
```

---

## MCP Server Integration

The dulayni-client includes a built-in MCP (Model Context Protocol) filesystem server that provides:

- File reading and writing operations
- Directory listing and navigation
- Secure command execution
- File search and editing capabilities

The MCP server runs automatically on port 8003 when using the CLI.

---

## FRPC Tunneling

For remote MCP server access, the client sets up FRPC (Fast Reverse Proxy Client) tunneling:

- Automatic Docker container setup
- Secure tunneling to relay server
- Domain-based routing (`{identifier}.157.230.76.226.nip.io`)

---

## Library API Reference

### `DulayniClient`

The main client class for interacting with dulayni agents.

#### Constructor Parameters

* `api_url (str)`: URL of the Dulayni API server
* `phone_number (str)`: Phone number for WhatsApp authentication
* `dulayni_api_key (str)`: API key for Dulayni authentication
* `model (str)`: Model name to use (default: `"gpt-4o-mini"`)
* `agent_type (str)`: Type of agent (`"react"` or `"deep_react"`)
* `thread_id (str)`: Thread ID for conversation continuity
* `system_prompt (str)`: Custom system prompt for the agent
* `mcp_servers (dict)`: MCP server configurations
* `memory_db (str)`: Path to SQLite database for conversation memory
* `pg_uri (str)`: PostgreSQL URI for memory storage
* `request_timeout (float)`: Timeout for API requests in seconds

#### Methods

**Authentication**

* `request_verification_code(phone_number: str = None) -> dict`
* `verify_code(verification_code: str, session_id: str = None) -> dict`
* `authenticate(verification_code_callback = None) -> bool`

**Query**

* `query(content: str, **kwargs) -> str`
* `query_json(content: str, **kwargs) -> dict`
* `query_stream(content: str, **kwargs) -> Generator[Dict[str, Any], None, None]`

**Account Management**

* `get_balance() -> Dict[str, Any]` (WhatsApp authentication only)

**Utility**

* `health_check() -> dict`
* `is_healthy() -> bool`
* `set_thread_id(thread_id: str)`
* `set_system_prompt(prompt: str)`
* `set_phone_number(phone_number: str)`
* `set_dulayni_api_key(dulayni_api_key: str)`

#### Exceptions

* `DulayniClientError` – Base exception for client errors
* `DulayniConnectionError` – Raised when unable to connect to server
* `DulayniTimeoutError` – Raised when requests time out
* `DulayniAuthenticationError` – Raised when authentication fails or is required
* `DulayniPaymentRequiredError` – Raised when payment is required

---

## Examples

See the `examples/` directory for more detailed usage examples.

---

## Requirements

* dulayni server running on the specified API URL
* Phone number for WhatsApp authentication OR Dulayni API key
* Python 3.12+
* Docker (for FRPC tunneling)

---

## Development

Install development dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

Format code:

```bash
black src/ tests/
ruff check src/ tests/
```

## Troubleshooting

### FRPC Container Issues

If you encounter issues with the FRPC container:

1. Check if Docker is running: `docker info`
2. Check FRPC container status: `docker ps -a`
3. Restart FRPC container: `docker restart frpc`

### Authentication Issues

For WhatsApp authentication issues:
1. Ensure your phone number is in international format (+1234567890)
2. Check that you can receive WhatsApp messages

For API key authentication issues:
1. Ensure your API key starts with `sk-`
2. Check that the API key has not expired

### MCP Server Issues

If the MCP server fails to start:
1. Check if port 8003 is available: `lsof -i :8003`
2. Try running with a different port: `dulayni run --mcp-port 8004`
