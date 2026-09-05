# 🚀 Quick Start - Arr Suite MCP Server

## ✅ Configuration Complete!

Your MCP server is **ready to use** in Claude Code and VS Code (Roo/Cline).

## 🎯 Immediate Actions

### 1. Test in Claude Code (Right Now!)

Open Claude Code in either project directory and try:

```
List all configured arr services
```

You should see: Sonarr, Radarr, Prowlarr, Seerr, and Plex (pending token)

### 2. Try Natural Language

```
Search Radarr for The Matrix
```

```
Show all my TV series in Sonarr
```

```
What indexers are configured in Prowlarr?
```

### 3. Get Plex Token (Optional but Recommended)

**Quick Method:**
1. Go to https://app.plex.tv
2. Play any media
3. Click "..." → "Get Info" → "View XML"
4. Copy the `X-Plex-Token` from URL

**Add to `.env`:**
```bash
PLEX_TOKEN=your_actual_token
```

Then restart Claude Code or reload the MCP server.

## 📝 What's Configured

### ✅ Services Ready
- **Sonarr** @ 192.168.1.100:8989 — API v3
- **Radarr** @ 192.168.1.100:7878 — API v3
- **Prowlarr** @ 192.168.1.100:9696 — API **v1** (differs from other arr apps)
- **Seerr** @ 192.168.1.101:5055 — status at `/api/v1/status`
- **Bazarr** @ 192.168.1.100:6767
- **Plex** @ localhost:32400 (needs token)

### ✅ MCP Configuration
- `/claude/homelab-mcp/arr-suite/.claude/mcp_config.json`

## 🎮 Example Commands

### Media Management
```
Add Breaking Bad to Sonarr
```

```
Search for movies from 2023 in Radarr
```

```
Request Avatar 2 through Seerr
```

### System Operations
```
Show download queue status
```

```
Get system status for all services
```

```
List all quality profiles in Radarr
```

### Plex (after adding token)
```
What's recently added to Plex?
```

```
Search Plex for Breaking Bad
```

```
Show what's currently playing
```

## 📚 Documentation

- **Full Setup Guide**: [CLAUDE_CODE_SETUP.md](CLAUDE_CODE_SETUP.md)
- **Plex Integration**: [PLEX_INTEGRATION.md](PLEX_INTEGRATION.md)
- **Usage Examples**: [EXAMPLES.md](EXAMPLES.md)
- **README**: [README.md](README.md)

## 🔧 For VS Code / Roo / Cline Users

The `.claude/mcp_config.json` file is already created and will be auto-detected.

If not working, see [CLAUDE_CODE_SETUP.md](CLAUDE_CODE_SETUP.md) for manual configuration.

## ✨ Smart Features

### Natural Language Understanding
Just describe what you want:
- "Add this movie" → Routes to Radarr
- "Download subtitles" → Routes to Bazarr
- "Search indexers" → Routes to Prowlarr
- "Request media" → Routes to Seerr

### Intelligent Routing
The system automatically detects:
- Service (Sonarr, Radarr, etc.)
- Operation (search, add, delete, etc.)
- Context (titles, years, quality, etc.)

## 🎯 First Steps Checklist

- [ ] Test: `List all configured services`
- [ ] Try: `Search Radarr for a movie`
- [ ] Get Plex token and add to `.env`
- [ ] Test: `What's new on Plex?`
- [ ] Explore: Use `arr_explain_intent` to understand queries

## 🐛 Issues?

See [CLAUDE_CODE_SETUP.md](CLAUDE_CODE_SETUP.md) → Troubleshooting section

---

**Everything is configured and ready to go!** 🎉

Start using it immediately in Claude Code by asking: `"List all configured arr services"`
