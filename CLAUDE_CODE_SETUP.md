# Claude Code & VS Code Setup Guide

This MCP server is now configured for use with Claude Code and VS Code (Roo/Cline).

## ✅ What's Been Configured

### 1. Environment Variables (`.env`)
All your arr suite services are configured with API keys:
- ✅ Sonarr (192.168.1.100:8989)
- ✅ Radarr (192.168.1.100:7878)
- ✅ Prowlarr (192.168.1.100:9696) — uses API **v1**
- ✅ Seerr (192.168.1.101:5055) — status at `/api/v1/status`
- ✅ Bazarr (192.168.1.100:6767)
- ✅ Plex (localhost:32400) - **Token needed**

### 2. MCP Configuration Files Created

**For this project** (`.claude/mcp_config.json`):
- Located in `/claude/homelab-mcp/arr-suite/.claude/`

Both configurations point to the same MCP server with all your credentials.

## 🚀 Usage in Claude Code

The MCP server is automatically detected in Claude Code when you're working in:
- `/claude/homelab-mcp/arr-suite/` (this project)

### Try These Commands

```
List all configured arr services
```

```
Search Radarr for The Matrix
```

```
Show my Sonarr TV series
```

```
Get recently added Plex media
```

```
List all Prowlarr indexers
```

## 🔧 For VS Code / Roo / Cline

### Option 1: Use MCP Extension (Recommended)

1. Install MCP extension in VS Code Insiders
2. The `.claude/mcp_config.json` will be auto-detected
3. Reload window
4. MCP server will be available

### Option 2: Manual Roo/Cline Configuration

Add to your Roo/Cline settings:

```json
{
  "mcp": {
    "servers": {
      "arr-suite": {
        "command": "arr-suite-mcp",
        "env": {
          "SONARR_HOST": "your_sonarr_host",
          "SONARR_PORT": "8989",
          "SONARR_API_KEY": "your_sonarr_api_key_here",
          "RADARR_HOST": "localhost",
          "RADARR_PORT": "7878",
          "RADARR_API_KEY": "your_radarr_api_key_here",
          "PROWLARR_HOST": "localhost",
          "PROWLARR_PORT": "9696",
          "PROWLARR_API_KEY": "your_prowlarr_api_key_here",
          "SEERR_HOST": "localhost",
          "SEERR_PORT": "5055",
          "SEERR_API_KEY": "your_seerr_api_key_here",
          "PLEX_HOST": "localhost",
          "PLEX_PORT": "32400",
          "PLEX_TOKEN": "your_plex_token_here"
        }
      }
    }
  }
}
```

## 📝 Getting Plex Token (Optional but Recommended)

You currently don't have a Plex token configured. To enable Plex features:

### Method 1: From Plex Web App
1. Open https://app.plex.tv
2. Browse to any media item
3. Click "..." → "Get Info" → "View XML"
4. Look for `X-Plex-Token` in the URL
5. Copy the token value

### Method 2: Using curl
```bash
curl -X POST 'https://plex.tv/users/sign_in.json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'user[login]=YOUR_EMAIL&user[password]=YOUR_PASSWORD'
```

### Add Token
Once you have the token, add it to your `.env` file:
```bash
PLEX_TOKEN=your_actual_token_here
```

And update the MCP config environment:
```json
"PLEX_TOKEN": "your_actual_token_here"
```

## 🧪 Testing the MCP Server

### Test in Claude Code
```
Explain what "Add Breaking Bad to Sonarr" would do
```

Should show you how it would route the request.

### Test Direct Tool Access
```
Use the sonarr_get_series tool to list all my TV shows
```

### Test Natural Language
```
Search Radarr for movies released in 2023
```

## 📊 Available MCP Tools

### Intelligent Router
- `arr_execute` - Execute any operation using natural language
- `arr_explain_intent` - See how your query will be interpreted
- `arr_list_services` - Show which services are configured
- `arr_get_system_status` - Check health of all services

### Service-Specific Tools

**Sonarr** (3 tools + more):
- `sonarr_search_series`
- `sonarr_add_series`
- `sonarr_get_series`

**Radarr** (3 tools + more):
- `radarr_search_movie`
- `radarr_add_movie`
- `radarr_get_movies`

**Prowlarr** (3 tools):
- `prowlarr_search`
- `prowlarr_get_indexers`
- `prowlarr_sync_apps`

**Bazarr** (2 tools):
- `bazarr_search_subtitles`
- `bazarr_download_subtitle`

**Seerr** (3 tools):
- `seerr_search`
- `seerr_request`
- `seerr_get_requests`

**Plex** (7 tools):
- `plex_get_libraries`
- `plex_search`
- `plex_get_recently_added`
- `plex_get_on_deck`
- `plex_get_sessions`
- `plex_scan_library`
- `plex_mark_watched`

## 🔍 Troubleshooting

### MCP Server Not Showing in Claude Code

1. Check if `.claude/mcp_config.json` exists:
   ```bash
   ls -la /claude/homelab-mcp/arr-suite/.claude/
   ```

2. Verify the MCP server binary is available:
   ```bash
   which arr-suite-mcp
   arr-suite-mcp --help
   ```

3. Check MCP server logs in Claude Code output panel

### Services Not Connecting

Verify services are reachable (note the correct API versions):
```bash
# Sonarr / Radarr — v3
curl -H "X-Api-Key: YOUR_API_KEY" http://YOUR_HOST:8989/api/v3/system/status

# Prowlarr — v1 (not v3!)
curl -H "X-Api-Key: YOUR_API_KEY" http://YOUR_HOST:9696/api/v1/system/status

# Seerr — /status (not /system/status!)
curl -H "X-Api-Key: YOUR_API_KEY" http://YOUR_HOST:5055/api/v1/status
```

### Prowlarr or Seerr Show Offline

If `arr_get_system_status` shows these services offline even when they're running, the installed package may be out of date. Reinstall from source:
```bash
cd /claude/homelab-mcp/arr-suite/repo
pipx install . --force
pkill -f arr-suite-mcp
```

## 🎯 Next Steps

1. ✅ MCP configs are created
2. ⏳ Get Plex token and add to `.env`
3. ⏳ Test in Claude Code: "List all configured services"
4. ⏳ Try natural language queries
5. ⏳ Explore all the available tools

## 📁 File Locations

- **MCP Config**: `/claude/homelab-mcp/arr-suite/.claude/mcp_config.json`
- **Environment Variables**: `/claude/homelab-mcp/arr-suite/repo/.env`
- **Server Code**: `/claude/homelab-mcp/arr-suite/repo/arr_suite_mcp/`
- **Installed Binary**: `/root/.local/bin/arr-suite-mcp`
- **Installed Package**: `/root/.local/share/pipx/venvs/arr-suite-mcp/`

## 💡 Pro Tips

1. **Use Natural Language**: The router is smart - just describe what you want
2. **Check Intent First**: Use `arr_explain_intent` to see how it will be interpreted
3. **Direct Tools**: For precise control, use service-specific tools
4. **System Status**: Regularly check `arr_get_system_status`
5. **Database Backup**: The server includes database management utilities

---

**Ready to use in both Claude Code and VS Code (Roo/Cline)!** 🚀
