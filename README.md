# Arr Suite MCP Server

A comprehensive Model Context Protocol (MCP) server that provides AI assistants with intelligent access to your entire arr suite media automation stack.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## Overview

The Arr Suite MCP Server is a powerful integration that connects AI assistants like Claude to your media automation infrastructure. It uses intelligent natural language processing to automatically route requests to the appropriate service, making media management feel natural and intuitive.

### Supported Services

- **Sonarr** - TV Series management
- **Radarr** - Movie management
- **Prowlarr** - Indexer management and search
- **Bazarr** - Subtitle management
- **Seerr** - Media request and discovery
- **Plex** - Media Server management and playback

### Key Features

- **🧠 Intelligent Intent Recognition**: Uses natural language understanding to automatically determine which service to use
- **🎯 Unified Interface**: Single API for all arr services
- **🔌 Easy Integration**: Simple environment variable configuration
- **🛡️ Type-Safe**: Built with Pydantic for robust validation
- **⚡ Async-First**: Built on httpx for high-performance async operations
- **📝 Comprehensive**: Full API coverage for all supported services
- **🎨 Natural Language**: Talk to your media server like a human

## Installation

### From PyPI (recommended)

```bash
pip install arr-suite-mcp
```

### From Source

```bash
git clone https://github.com/kevonob/arr-suite-mcp-server.git
cd arr-suite-mcp-server
pip install -e .
```

## Quick Start

### 1. Configure Environment

Create a `.env` file:

```bash
# Sonarr Configuration
SONARR_HOST=localhost
SONARR_PORT=8989
SONARR_API_KEY=your_sonarr_api_key

# Radarr Configuration
RADARR_HOST=localhost
RADARR_PORT=7878
RADARR_API_KEY=your_radarr_api_key

# Prowlarr Configuration
PROWLARR_HOST=localhost
PROWLARR_PORT=9696
PROWLARR_API_KEY=your_prowlarr_api_key

# Bazarr Configuration
BAZARR_HOST=localhost
BAZARR_PORT=6767
BAZARR_API_KEY=your_bazarr_api_key

# Seerr Configuration
SEERR_HOST=localhost
SEERR_PORT=5055
SEERR_API_KEY=your_seerr_api_key
```

### 2. Run the Server

```bash
arr-suite-mcp
```

### 3. Configure Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "arr-suite": {
      "command": "arr-suite-mcp",
      "env": {
        "SONARR_HOST": "localhost",
        "SONARR_PORT": "8989",
        "SONARR_API_KEY": "your_api_key"
      }
    }
  }
}
```

## Usage Examples

The beauty of this MCP server is its natural language understanding. Here are some examples:

### TV Shows (Sonarr)

```
"Add Breaking Bad to my collection"
"Search for The Mandalorian"
"List all my TV shows"
"Get episodes for Game of Thrones season 8"
"Monitor The Office for new episodes"
```

### Movies (Radarr)

```
"Add The Matrix to my movies"
"Search for Inception"
"Show all my 4K movies"
"Get details for The Godfather"
"Find movies from 2023"
```

### Indexers (Prowlarr)

```
"Search for Dune across all indexers"
"List all my indexers"
"Test all indexers"
"Sync indexers to Radarr and Sonarr"
"Show indexer statistics"
```

### Subtitles (Bazarr)

```
"Download English subtitles for Dune"
"Search for Spanish subtitles for episode 3"
"Show movies missing subtitles"
"Get subtitle providers"
```

### Requests (Seerr)

```
"Request Avatar 2"
"Show pending requests"
"Approve request 123"
"Search for trending movies"
"Discover new TV shows"
```

### Plex Media Server

```
"Search Plex for Breaking Bad"
"Show my Plex libraries"
"What's recently added to Plex?"
"Show what's playing on Plex"
"Get On Deck items"
"Scan my Movies library"
"Mark The Matrix as watched"
```

### Advanced Operations

```
"Backup all Sonarr databases"
"Update quality profile in Radarr"
"Configure download client in Prowlarr"
"Get system status for all services"
```

## MCP Tools

The server provides both high-level intelligent tools and service-specific tools:

### Intelligent Tools

- `arr_execute` - Execute any arr operation using natural language
- `arr_explain_intent` - Understand how your query will be interpreted
- `arr_list_services` - Show configured services
- `arr_get_system_status` - Get health status of all services

### Service-Specific Tools

Each service has dedicated tools for precise control:

#### Sonarr Tools
- `sonarr_search_series` - Search for TV series
- `sonarr_add_series` - Add a new series
- `sonarr_get_series` - Get all or specific series
- And 20+ more operations

#### Radarr Tools
- `radarr_search_movie` - Search for movies
- `radarr_add_movie` - Add a new movie
- `radarr_get_movies` - Get all or specific movies
- And 20+ more operations

#### Prowlarr Tools
- `prowlarr_search` - Search across indexers
- `prowlarr_get_indexers` - List all indexers
- `prowlarr_sync_apps` - Sync to applications
- And 15+ more operations

#### Plex Tools
- `plex_search` - Search Plex media
- `plex_get_libraries` - List all libraries
- `plex_get_recently_added` - Recently added content
- `plex_get_sessions` - Currently playing
- `plex_scan_library` - Scan library for new content
- `plex_mark_watched` - Mark as watched
- And more...

## Configuration

### Environment Variables

The server uses environment variables with prefixes for each service:

```bash
# Format: {SERVICE}_{SETTING}
SONARR_HOST=localhost
SONARR_PORT=8989
SONARR_API_KEY=abc123
SONARR_SSL=false

# Global Settings
REQUEST_TIMEOUT=30
MAX_RETRIES=3
LOG_LEVEL=INFO
```

### Finding API Keys

#### Sonarr/Radarr
1. Open the web UI
2. Settings → General
3. Security section → API Key

#### Prowlarr
1. Open the web UI
2. Settings → General
3. Security section → API Key

#### Bazarr
1. Open the web UI
2. Settings → General
3. Security section → API Key

#### Seerr
1. Open the web UI
2. Settings → General
3. API Key section

## Architecture

```
┌─────────────────────────────────────────┐
│         AI Assistant (Claude)           │
└────────────────┬────────────────────────┘
                 │ MCP Protocol
┌────────────────▼────────────────────────┐
│         Arr Suite MCP Server            │
│  ┌─────────────────────────────────┐   │
│  │    Intent Router (NLP)          │   │
│  │  - Analyzes natural language    │   │
│  │  - Determines service & action  │   │
│  └─────────────┬───────────────────┘   │
│                │                        │
│  ┌─────────────▼───────────────────┐   │
│  │      Service Clients            │   │
│  │  ┌──────────┐  ┌──────────┐    │   │
│  │  │ Sonarr   │  │ Radarr   │    │   │
│  │  ├──────────┤  ├──────────┤    │   │
│  │  │ Prowlarr │  │ Bazarr   │    │   │
│  │  ├──────────┤  ├──────────┤    │   │
│  │  │Seerr │  │  More... │    │   │
│  │  └──────────┘  └──────────┘    │   │
│  └─────────────────────────────────┘   │
└────────────────┬────────────────────────┘
                 │ HTTP/REST APIs
┌────────────────▼────────────────────────┐
│        Your Arr Stack Services          │
│   Sonarr│Radarr│Prowlarr│Bazarr│etc.   │
└─────────────────────────────────────────┘
```

## OpenWebUI Integration (mcpo)

OpenWebUI 0.8.5+ supports external tool servers via **OpenAPI/Streamable HTTP**. Use
[mcpo](https://github.com/open-webui/mcpo) to wrap the MCP stdio server and expose each
tool as a standard OpenAPI endpoint.

### Architecture

```
OpenWebUI (:8080)
  └─ HTTP → mcpo (:8766)          ← OpenAPI proxy
              └─ stdio → arr-suite-mcp
                          ├─ Sonarr   :8989
                          ├─ Radarr   :7878
                          ├─ Prowlarr :9696
                          └─ Seerr :5055

supergateway SSE (:8765) → LocalAI (unchanged)
```

### Setup

**1. Install mcpo**

```bash
pipx install mcpo
```

**2. Create config** (`mcpo-config.json` — not committed, contains API keys):

```json
{
  "mcpServers": {
    "arr-suite": {
      "command": "/root/.local/bin/arr-suite-mcp",
      "args": [],
      "env": {
        "SONARR_HOST": "...", "SONARR_PORT": "8989", "SONARR_API_KEY": "...",
        "RADARR_HOST": "...", "RADARR_PORT": "7878", "RADARR_API_KEY": "...",
        "PROWLARR_HOST": "...", "PROWLARR_PORT": "9696", "PROWLARR_API_KEY": "...",
        "SEERR_HOST": "...", "SEERR_PORT": "5055", "SEERR_API_KEY": "..."
      }
    }
  }
}
```

**3. Run as systemd service** (`/etc/systemd/system/arr-suite-mcpo.service`):

```ini
[Unit]
Description=arr-suite MCP → OpenAPI proxy for OpenWebUI
After=network.target arr-suite-mcp.service

[Service]
Type=simple
User=root
ExecStart=/root/.local/bin/mcpo --port 8766 --host 0.0.0.0 \
  --config /claude/homelab-mcp/arr-suite/mcpo-config.json
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload && systemctl enable --now arr-suite-mcpo
```

**4. Register in OpenWebUI** — Admin > Settings > External Tools:

- URL: `http://192.168.1.100:8766/arr-suite`
- Path: `openapi.json`
- Type: `openapi`

**Verify:**

```bash
# Service status
systemctl status arr-suite-mcpo

# OpenAPI schema (should list ~16 tool paths)
curl http://localhost:8766/arr-suite/openapi.json | python3 -m json.tool | grep '"summary"'
```

## Database Management

The server includes utilities for managing arr suite databases:

```python
from arr_suite_mcp.utils.db_manager import ArrDatabaseManager

# Backup all databases
manager = ArrDatabaseManager(config_path="/path/to/arr/configs")
await manager.backup_all()

# Restore a database
await manager.restore("sonarr", "/path/to/backup.db")

# Execute SQL query
result = await manager.execute_query("sonarr", "SELECT * FROM Series")
```

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=arr_suite_mcp --cov-report=html
```

### Code Quality

```bash
# Format code
black arr_suite_mcp

# Lint
ruff check arr_suite_mcp

# Type check
mypy arr_suite_mcp
```

## API Coverage

### Sonarr
✅ Series Management (add, update, delete, search)
✅ Episode Management
✅ Quality Profiles
✅ Root Folders
✅ Tags
✅ Queue Management
✅ History
✅ Calendar
✅ Commands (refresh, rescan, rename, backup)
✅ Configuration

### Radarr
✅ Movie Management (add, update, delete, search)
✅ Collections
✅ Quality Profiles
✅ Root Folders
✅ Tags
✅ Queue Management
✅ History
✅ Calendar
✅ Commands (refresh, rescan, rename, backup)
✅ Configuration
✅ Import Lists
✅ Notifications

### Prowlarr
✅ Indexer Management (add, update, delete, test)
✅ Search across Indexers
✅ Application Management (Sonarr, Radarr connections)
✅ Tags
✅ History
✅ Statistics
✅ Download Clients
✅ Notifications
✅ Configuration
✅ Sync Operations

### Bazarr
✅ Series Subtitle Management
✅ Movie Subtitle Management
✅ Subtitle Search
✅ Subtitle Download
✅ History
✅ Languages
✅ Providers
✅ System Status
✅ Settings
✅ Wanted Subtitles
✅ Blacklist

### Seerr
✅ Request Management (create, approve, decline)
✅ Media Search
✅ Discovery (movies, TV)
✅ Trending Content
✅ User Management
✅ Settings (Plex, Radarr, Sonarr)
✅ System Status
✅ Issues

## Troubleshooting

### Connection Issues

```bash
# Test Sonarr/Radarr (use v3)
curl http://localhost:8989/api/v3/system/status?apikey=YOUR_API_KEY

# Test Prowlarr (uses v1, NOT v3)
curl http://localhost:9696/api/v1/system/status?apikey=YOUR_API_KEY

# Test Seerr (uses /status, not /system/status)
curl http://localhost:5055/api/v1/status?apikey=YOUR_API_KEY

# Check logs
arr-suite-mcp --log-level DEBUG
```

### Common Issues

1. **API Key Invalid**: Double-check your API keys in the web UI
2. **Connection Refused**: Ensure services are running and accessible
3. **SSL Errors**: Set `{SERVICE}_SSL=false` for local deployments
4. **Prowlarr/Seerr shows offline in `arr_get_system_status`**: Prowlarr uses the **v1** API (not v3 like Sonarr/Radarr), and Seerr's status endpoint is `/api/v1/status` (not `/api/v1/system/status`). Fix by reinstalling from source.
5. **Bazarr shows offline in `arr_get_system_status`**: Bazarr does **not** use a versioned API path. Earlier versions incorrectly called `/api/v4/system/status` (which returns HTML), causing a JSON parse failure. Fixed in `clients/bazarr.py` by overriding `_build_url()` to produce `/api/{endpoint}` with no version segment. Reinstall from source if still affected:
   ```bash
   cd /path/to/arr-suite-mcp-server
   pipx install . --force
   # Then restart the MCP server process
   ```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- Built with [MCP](https://modelcontextprotocol.io/) by Anthropic
- Powered by the amazing [arr suite](https://wiki.servarr.com/) projects
- Inspired by the home media automation community

## Support

- 📖 [Documentation](https://github.com/kevonob/arr-suite-mcp-server)
- 🐛 [Issue Tracker](https://github.com/kevonob/arr-suite-mcp-server/issues)
- 💬 [Discussions](https://github.com/kevonob/arr-suite-mcp-server/discussions)

## Roadmap

- [ ] Lidarr support (music)
- [ ] Readarr support (books)
- [ ] Whisparr support (adult content)
- [ ] Advanced filtering and sorting
- [ ] Batch operations
- [ ] Custom scripts integration
- [ ] WebSocket support for real-time updates
- [ ] Metrics and monitoring
- [ ] Multi-instance support

---

**Made with ❤️ for the media automation community**
