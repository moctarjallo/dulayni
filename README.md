# dulayni

`dulayni` is a CLI tool and Python library for building and running Retrieval-Augmented Generation (RAG) agents via MCP (Multi-Channel Processing) servers. It provides a simple interface to configure, launch, and interact with AI agents backed by OpenAI and custom tool servers.

## Key Features

* **Agent Framework**: Create and customize agents (e.g., React-based) with OpenAI's chat models.
* **MCP Tooling**: Define MCP servers and tools in Python to extend agent capabilities (math, weather, custom data retrieval, etc.).
* **Configurable**: Easily set up servers, models, and prompts via JSON configuration files.
* **Interactive CLI**: Run queries interactively or in batch mode with rich Markdown output.
* **Persistence**: Built-in memory using SQLite checkpointing for conversation continuity.

## Table of Contents

- [dulayni](#dulayni)
  - [Key Features](#key-features)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Configuration](#configuration)
    - [MCP Servers](#mcp-servers)
    - [Model Settings](#model-settings)
  - [CLI Usage](#cli-usage)
    - [Interactive Mode](#interactive-mode)
    - [Batch Query Mode](#batch-query-mode)
  - [Extending the Agent](#extending-the-agent)
    - [Adding Tools](#adding-tools)
    - [Custom Agent Types](#custom-agent-types)
  - [Development](#development)
  - [Contributing](#contributing)
  - [License](#license)

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/your_org/dulayni.git
   cd dulayni
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

4. **Set environment variables** (e.g., OpenAI API key):

   ```bash
   export OPENAI_API_KEY="your_api_key_here"
   ```

## Configuration

### MCP Servers

Define your MCP tool servers in `config/mcp_servers.json`:

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

You can add multiple named servers and reference them in your agent configuration.

### Model Settings

Adjust your model and system prompt in `config/model_config.json`:

```json
{
    "model_name": "gpt-4o-mini",
    "role": "user",
    "system_prompt": "You are a high school math teacher"
}
```

> **Note**: If you override defaults, pass custom JSON path via `--path2mcp_servers_file` CLI flag.

## CLI Usage

After installation, use the `dulayni` entrypoint.

### Interactive Mode

Start an interactive REPL:

```bash
dulayni -k $OPENAI_API_KEY
```

Type queries at the prompt; enter `q` to exit.

### Batch Query Mode

Run a single query non-interactively:

```bash
dulayni -k $OPENAI_API_KEY -q "What's (3 + 5) x 12?" --print_mode rich
```

* **Options**:

  * `-m, --model`: Model name (`gpt-4.1` or `gpt-4.1-mini` by default).
  * `-k, --openai_api_key`: Your OpenAI API key (or set `OPENAI_API_KEY`).
  * `-q, --query`: Query string for batch mode.
  * `-mcp, --path2mcp_servers_file`: MCP server config path.
  * `-p, --parallel_tool_calls`: Enable parallel tool execution.
  * `-a, --agent_type`: Agent type (`react` by default).
  * `--print_mode`: `json` or `rich` Markdown output.

## Extending the Agent

### Adding Tools

1. Edit or create a new MCP server in `src/dulayni/mcp/server.py`:

   ```python
   @mcp.tool()
   def my_tool(x: int, y: int) -> int:
       return x - y
   ```
2. Run the server:

   ```bash
   python src/dulayni/mcp/server.py
   ```
3. Update `config/mcp_servers.json` if using a new host/port.
4. Query your tool from the CLI or integrate into your application.

### Custom Agent Types

* Agents inherit from `dulayni.agents.agent.Agent`.
* Add new classes under `src/dulayni/agents/` and register in `create_agent`.
* Override `_build_graph` to customize LangGraph behavior.

## Development

* **Tests**: Add unit tests under `tests/` and run via `pytest`.
* **Linting**: `flake8 src/`.
* **Formatting**: `black src/`.
* **Type Checking**: `mypy src/`.

## Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/my-feature`.
3. Commit changes and push: `git push origin feature/my-feature`.
4. Open a Pull Request describing your changes.

We welcome bug reports, feature proposals, and contributions of all sizes!

## License

This project is released under the [MIT License](LICENSE).
