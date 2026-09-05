# Installation Guide

Complete installation guide for the Arr Suite MCP Server.

## Prerequisites

- Python 3.10 or higher
- At least one arr service (Sonarr, Radarr, Prowlarr, Bazarr, or Seerr)
- API keys for the services you want to use
- Claude Desktop (for MCP integration)

## Installation Methods

### Method 1: Install from PyPI (Recommended)

```bash
pip install arr-suite-mcp
```

### Method 2: Install with pipx (Recommended for servers)

```bash
# Install using pipx for isolated environment
pipx install arr-suite-mcp

# To reinstall/upgrade from source
cd /path/to/arr-suite-mcp-server
pipx install . --force
```

### Method 3: Install from Source

```bash
# Clone the repository
git clone https://gitea.yourdomain.com/arr-suite-mcp.git
cd arr-suite-mcp

# Install in development mode
pip install -e .

# Or install normally
pip install .
```

## Configuration

### Step 1: Create Environment File

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your service details:

```bash
# Sonarr
SONARR_HOST=192.168.1.100
SONARR_PORT=8989
SONARR_API_KEY=your_api_key_here

# Radarr
RADARR_HOST=192.168.1.100
RADARR_PORT=7878
RADARR_API_KEY=your_api_key_here

# Add other services as needed...
```

### Step 2: Find Your API Keys

#### For Sonarr, Radarr, and Prowlarr:

1. Open the service web UI
2. Click **Settings** (gear icon)
3. Click **General** tab
4. Scroll to **Security** section
5. Copy the **API Key**

#### For Bazarr:

1. Open Bazarr web UI
2. Click **Settings**
3. Click **General** tab
4. Scroll to **Security** section
5. Copy the **API Key**

#### For Seerr:

1. Open Seerr web UI
2. Click **Settings**
3. Click **General** tab
4. Scroll to **API Key** section
5. Copy the key or generate a new one

### Step 3: Test the Server

Run the server to verify configuration:

```bash
arr-suite-mcp
```

You should see output indicating which services are enabled.

## Claude Desktop Integration

### macOS

1. Locate Claude Desktop config file:
   ```bash
   ~/Library/Application Support/Claude/claude_desktop_config.json
   ```

2. Add the arr-suite MCP server:
   ```json
   {
     "mcpServers": {
       "arr-suite": {
         "command": "arr-suite-mcp",
         "env": {
           "SONARR_HOST": "192.168.1.100",
           "SONARR_PORT": "8989",
           "SONARR_API_KEY": "your_api_key",
           "RADARR_HOST": "192.168.1.100",
           "RADARR_PORT": "7878",
           "RADARR_API_KEY": "your_api_key"
         }
       }
     }
   }
   ```

3. Restart Claude Desktop

### Windows

1. Locate config file:
   ```
   %APPDATA%\Claude\claude_desktop_config.json
   ```

2. Add configuration as shown above

3. Restart Claude Desktop

### Linux

1. Locate config file:
   ```bash
   ~/.config/Claude/claude_desktop_config.json
   ```

2. Add configuration as shown above

3. Restart Claude Desktop

## Verifying Installation

### Check Services

Open Claude Desktop and try:

```
List all configured arr services
```

You should see a list of your configured services.

### Test Operations

Try some test queries:

```
Search for Breaking Bad
Show all my movies
List indexers
```

### View System Status

```
Get system status for all services
```

This will show if all your services are reachable.

## Troubleshooting

### "Service not configured" Error

- Verify your `.env` file has the correct settings
- Check that API keys are correct
- Ensure services are running

### Connection Refused

- Verify service host and port
- Check firewall settings
- Ensure services are accessible from where you're running the MCP server

### Prowlarr or Seerr Showing Offline

These services use different API paths than Sonarr/Radarr:

- **Prowlarr** uses API **v1** (not v3): `/api/v1/system/status`
- **Seerr** uses `/api/v1/status` (not `/api/v1/system/status`)

If running an older installed version, the wrong endpoints may be called. Fix:

```bash
# Reinstall from source to get the latest fixes
cd /path/to/arr-suite-mcp-server
pipx install . --force

# Then restart the MCP server process
pkill -f arr-suite-mcp
```

Verify the correct endpoints manually:
```bash
# Prowlarr (v1)
curl http://YOUR_HOST:9696/api/v1/system/status?apikey=YOUR_KEY

# Seerr (/status not /system/status)
curl http://YOUR_HOST:5055/api/v1/status?apikey=YOUR_KEY
```

### SSL Certificate Errors

For local installations without SSL:

```bash
SONARR_SSL=false
RADARR_SSL=false
PROWLARR_SSL=false
SEERR_SSL=false
BAZARR_SSL=false
```

### Import Errors

```bash
# Reinstall with dependencies using pipx
pipx install arr-suite-mcp --force

# Or if using pip
pip install --force-reinstall arr-suite-mcp

# Or if using source
pip install -e ".[dev]"
```

### Debug Mode

Run with debug logging:

```bash
LOG_LEVEL=DEBUG arr-suite-mcp
```

## Docker Installation (Advanced)

Create a `docker-compose.yml`:

```yaml
version: '3.8'

services:
  arr-suite-mcp:
    image: arr-suite-mcp:latest
    env_file:
      - .env
    network_mode: host
    restart: unless-stopped
```

Run:

```bash
docker-compose up -d
```

## Updating

### PyPI Installation

```bash
pip install --upgrade arr-suite-mcp
```

### Source Installation

```bash
cd arr-suite-mcp
git pull
pip install -e .
```

## Uninstallation

```bash
pip uninstall arr-suite-mcp
```

Remove Claude Desktop configuration and `.env` files as needed.

## Next Steps

- Read the [README.md](README.md) for usage examples
- Check out [EXAMPLES.md](EXAMPLES.md) for advanced usage
- Join our community for support

## Getting Help

- 📖 [Documentation](https://github.com/shaktech786/arr-suite-mcp-server)
- 🐛 [Report Issues](https://github.com/shaktech786/arr-suite-mcp-server/issues)
- 💬 [Discussions](https://github.com/shaktech786/arr-suite-mcp-server/discussions)
