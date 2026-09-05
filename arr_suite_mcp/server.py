"""Main MCP server implementation for arr suite."""

import logging
import asyncio
from typing import Any, Optional, Dict, List
from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

from .config import ArrSuiteConfig, PlexConfig
from .clients import (
    SonarrClient,
    RadarrClient,
    ProwlarrClient,
    BazarrClient,
    SeerrClient,
    PlexClient,
    TracearrClient,
    ArrClientError
)
from .routers import IntentRouter, ArrIntent
from .routers.intent_router import ArrService, OperationType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ArrSuiteMCPServer:
    """MCP Server for the arr suite with intelligent routing."""

    def __init__(self, config: Optional[ArrSuiteConfig] = None):
        """Initialize the MCP server."""
        self.config = config or ArrSuiteConfig()
        self.server = Server("arr-suite-mcp")
        self.router = IntentRouter()

        # Initialize clients
        self.clients: dict[str, Any] = {}
        self.plex_clients: dict[str, PlexClient] = {}  # Multiple Plex servers
        self._initialize_clients()

        # Register MCP handlers
        self._register_handlers()

        logger.info(f"Arr Suite MCP Server initialized with services: {self.config.enabled_services}")

    def _initialize_clients(self) -> None:
        """Initialize API clients for enabled services."""
        if self.config.sonarr and self.config.sonarr.api_key:
            self.clients["sonarr"] = SonarrClient(
                base_url=self.config.sonarr.base_url,
                api_key=self.config.sonarr.api_key,
                timeout=self.config.request_timeout,
                max_retries=self.config.max_retries
            )

        if self.config.radarr and self.config.radarr.api_key:
            self.clients["radarr"] = RadarrClient(
                base_url=self.config.radarr.base_url,
                api_key=self.config.radarr.api_key,
                timeout=self.config.request_timeout,
                max_retries=self.config.max_retries
            )

        if self.config.prowlarr and self.config.prowlarr.api_key:
            self.clients["prowlarr"] = ProwlarrClient(
                base_url=self.config.prowlarr.base_url,
                api_key=self.config.prowlarr.api_key,
                timeout=self.config.request_timeout,
                max_retries=self.config.max_retries
            )

        if self.config.bazarr and self.config.bazarr.api_key:
            self.clients["bazarr"] = BazarrClient(
                base_url=self.config.bazarr.base_url,
                api_key=self.config.bazarr.api_key,
                timeout=self.config.request_timeout,
                max_retries=self.config.max_retries
            )

        if self.config.seerr and self.config.seerr.api_key:
            self.clients["seerr"] = SeerrClient(
                base_url=self.config.seerr.base_url,
                api_key=self.config.seerr.api_key,
                timeout=self.config.request_timeout,
                max_retries=self.config.max_retries
            )

        if self.config.tracearr and self.config.tracearr.api_key:
            self.clients["tracearr"] = TracearrClient(
                base_url=self.config.tracearr.base_url,
                api_key=self.config.tracearr.api_key,
                timeout=self.config.request_timeout,
            )

        # Initialize all Plex servers
        for plex_config in self.config.plex_servers:
            if plex_config.token:
                plex_client = PlexClient(
                    base_url=plex_config.base_url,
                    token=plex_config.token,
                    timeout=self.config.request_timeout,
                    max_retries=self.config.max_retries
                )
                # Store by name for multi-server access
                self.plex_clients[plex_config.name] = plex_client
                # Also store in main clients for backwards compatibility (use "plex" for first/default)
                if "plex" not in self.clients:
                    self.clients["plex"] = plex_client

    def _get_default_plex_client(self) -> Optional[PlexClient]:
        """Get the default Plex client (first one or named 'default')."""
        if "default" in self.plex_clients:
            return self.plex_clients["default"]
        if self.plex_clients:
            return next(iter(self.plex_clients.values()))
        return None

    def _get_plex_client(self, name: Optional[str] = None) -> Optional[PlexClient]:
        """Get a specific Plex client by name, or the default if name is None."""
        if name:
            return self.plex_clients.get(name)
        return self._get_default_plex_client()

    def _register_handlers(self) -> None:
        """Register MCP protocol handlers."""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available MCP tools."""
            tools = [
                Tool(
                    name="arr_execute",
                    description=(
                        "Execute arr suite operations using natural language. "
                        "Intelligently routes to the correct service (Sonarr, Radarr, "
                        "Prowlarr, Bazarr, or Seerr) based on your request. "
                        "Examples: 'add Breaking Bad', 'search for The Matrix', "
                        "'download English subtitles for Dune', 'list all indexers', "
                        "'request Inception'"
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Natural language query describing what you want to do"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="arr_explain_intent",
                    description=(
                        "Explain how a natural language query would be interpreted "
                        "and routed to arr services. Useful for understanding what "
                        "the system will do before executing."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Natural language query to explain"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="arr_list_services",
                    description="List all configured and available arr services",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="arr_get_system_status",
                    description="Get system status for all configured arr services",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
            ]

            # Add service-specific tools
            if "sonarr" in self.clients:
                tools.extend(self._get_sonarr_tools())
            if "radarr" in self.clients:
                tools.extend(self._get_radarr_tools())
            if "prowlarr" in self.clients:
                tools.extend(self._get_prowlarr_tools())
            if "bazarr" in self.clients:
                tools.extend(self._get_bazarr_tools())
            if "seerr" in self.clients:
                tools.extend(self._get_seerr_tools())
            if self.plex_clients:
                tools.extend(self._get_plex_tools())
            if "tracearr" in self.clients:
                tools.extend(self._get_tracearr_tools())

            return tools

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
            """Handle tool calls."""
            try:
                # Route to appropriate handler
                if name == "arr_execute":
                    result = await self._handle_arr_execute(arguments["query"])
                elif name == "arr_explain_intent":
                    result = self._handle_explain_intent(arguments["query"])
                elif name == "arr_list_services":
                    result = self._handle_list_services()
                elif name == "arr_get_system_status":
                    result = await self._handle_system_status()
                # Service-specific tools
                elif name.startswith("sonarr_"):
                    result = await self._handle_sonarr_tool(name, arguments)
                elif name.startswith("radarr_"):
                    result = await self._handle_radarr_tool(name, arguments)
                elif name.startswith("prowlarr_"):
                    result = await self._handle_prowlarr_tool(name, arguments)
                elif name.startswith("bazarr_"):
                    result = await self._handle_bazarr_tool(name, arguments)
                elif name.startswith("seerr_"):
                    result = await self._handle_seerr_tool(name, arguments)
                elif name.startswith("plex_"):
                    result = await self._handle_plex_tool(name, arguments)
                elif name.startswith("tracearr_"):
                    result = await self._handle_tracearr_tool(name, arguments)
                else:
                    result = {"error": f"Unknown tool: {name}"}

                return [TextContent(type="text", text=str(result))]

            except Exception as e:
                logger.error(f"Error handling tool {name}: {e}", exc_info=True)
                return [TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]

    def _get_sonarr_tools(self) -> list[Tool]:
        """Get Sonarr-specific tools."""
        return [
            Tool(
                name="sonarr_search_series",
                description="Search for TV series in Sonarr",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "term": {"type": "string", "description": "Search term"}
                    },
                    "required": ["term"]
                }
            ),
            Tool(
                name="sonarr_add_series",
                description="Add a new TV series to Sonarr",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "tvdb_id": {"type": "integer", "description": "TVDB ID"},
                        "quality_profile_id": {"type": "integer", "description": "Quality profile ID"},
                        "root_folder_path": {"type": "string", "description": "Root folder path"},
                        "monitored": {"type": "boolean", "description": "Monitor series", "default": True}
                    },
                    "required": ["tvdb_id", "quality_profile_id", "root_folder_path"]
                }
            ),
            Tool(
                name="sonarr_get_series",
                description="Get all series or a specific series",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "series_id": {"type": "integer", "description": "Optional series ID"}
                    }
                }
            ),
        ]

    def _get_radarr_tools(self) -> list[Tool]:
        """Get Radarr-specific tools."""
        return [
            Tool(
                name="radarr_search_movie",
                description="Search for movies in Radarr",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "term": {"type": "string", "description": "Search term"}
                    },
                    "required": ["term"]
                }
            ),
            Tool(
                name="radarr_add_movie",
                description="Add a new movie to Radarr",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "tmdb_id": {"type": "integer", "description": "TMDB ID"},
                        "quality_profile_id": {"type": "integer", "description": "Quality profile ID"},
                        "root_folder_path": {"type": "string", "description": "Root folder path"},
                        "monitored": {"type": "boolean", "description": "Monitor movie", "default": True}
                    },
                    "required": ["tmdb_id", "quality_profile_id", "root_folder_path"]
                }
            ),
            Tool(
                name="radarr_get_movies",
                description="Get all movies or a specific movie",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "movie_id": {"type": "integer", "description": "Optional movie ID"}
                    }
                }
            ),
        ]

    def _get_prowlarr_tools(self) -> list[Tool]:
        """Get Prowlarr-specific tools."""
        return [
            Tool(
                name="prowlarr_search",
                description="Search for releases across all indexers",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "type": {"type": "string", "description": "Search type (search, tvsearch, movie)", "default": "search"}
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="prowlarr_get_indexers",
                description="Get all configured indexers",
                inputSchema={"type": "object", "properties": {}}
            ),
            Tool(
                name="prowlarr_sync_apps",
                description="Sync indexers to all connected applications",
                inputSchema={"type": "object", "properties": {}}
            ),
        ]

    def _get_bazarr_tools(self) -> list[Tool]:
        """Get Bazarr-specific tools."""
        return [
            Tool(
                name="bazarr_search_subtitles",
                description="Search for subtitles for a movie or episode",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "media_type": {"type": "string", "description": "movie or series"},
                        "media_id": {"type": "integer", "description": "Media ID"},
                        "episode_id": {"type": "integer", "description": "Episode ID (for series)"}
                    },
                    "required": ["media_type", "media_id"]
                }
            ),
            Tool(
                name="bazarr_download_subtitle",
                description="Download a subtitle",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "media_type": {"type": "string", "description": "movie or episode"},
                        "media_id": {"type": "integer"},
                        "language": {"type": "string", "description": "Language code (e.g., 'en')"}
                    },
                    "required": ["media_type", "media_id", "language"]
                }
            ),
        ]

    def _get_seerr_tools(self) -> list[Tool]:
        """Get Seerr-specific tools."""
        return [
            Tool(
                name="seerr_search",
                description="Search for movies and TV shows",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"}
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="seerr_request",
                description="Request a movie or TV show",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "media_type": {"type": "string", "description": "movie or tv"},
                        "media_id": {"type": "integer", "description": "TMDB/TVDB ID"},
                        "is_4k": {"type": "boolean", "default": False}
                    },
                    "required": ["media_type", "media_id"]
                }
            ),
            Tool(
                name="seerr_get_requests",
                description="Get all media requests",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "filter": {"type": "string", "description": "Filter (pending, approved, available)"}
                    }
                }
            ),
            Tool(
                name="seerr_approve_request",
                description="Approve a pending media request by its request ID",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "request_id": {"type": "integer", "description": "The request ID to approve"}
                    },
                    "required": ["request_id"]
                }
            ),
        ]

    async def _handle_arr_execute(self, query: str) -> dict[str, Any]:
        """Handle natural language arr execution."""
        # Parse intent
        service, operation, context = self.router.route(query)

        # Check if service is available
        if service.value not in self.clients and service.value != "plex":
            return {
                "error": f"{service.value.capitalize()} is not configured",
                "available_services": list(self.clients.keys())
            }

        # Handle Plex with potential server selection
        if service == ArrService.PLEX:
            if not self.plex_clients:
                return {"error": "Plex is not configured"}
            
            # Check if query specifies a server (e.g., "search Plex on tank03")
            server_name = context.get("server")
            client = self._get_plex_client(server_name)
            if not client:
                available = list(self.plex_clients.keys())
                return {
                    "error": f"Plex server '{server_name}' not found" if server_name else "No Plex servers configured",
                    "available_plex_servers": available
                }
        else:
            client = self.clients.get(service.value)
            if not client:
                return {
                    "error": f"{service.value.capitalize()} is not configured",
                    "available_services": list(self.clients.keys())
                }

        # Execute operation based on service and operation type
        try:
            result = await self._execute_operation(client, service, operation, context)
            return {
                "service": service.value,
                "operation": operation.value,
                "result": result
            }
        except ArrClientError as e:
            return {
                "error": str(e),
                "service": service.value,
                "operation": operation.value
            }

    async def _execute_operation(
        self,
        client: Any,
        service: ArrService,
        operation: OperationType,
        context: dict
    ) -> Any:
        """Execute the appropriate operation on the client."""
        # This is a simplified implementation - you would expand this
        # with more sophisticated routing logic

        if service == ArrService.SONARR:
            if operation == OperationType.SEARCH:
                term = context.get("title", "")
                return await client.lookup_series(term)
            elif operation == OperationType.LIST:
                return await client.get_all_series()

        elif service == ArrService.RADARR:
            if operation == OperationType.SEARCH:
                term = context.get("title", "")
                return await client.lookup_movie(term)
            elif operation == OperationType.LIST:
                return await client.get_all_movies()

        elif service == ArrService.PROWLARR:
            if operation == OperationType.SEARCH:
                query = context.get("title", "")
                return await client.search(query)
            elif operation == OperationType.LIST:
                return await client.get_all_indexers()

        elif service == ArrService.SEERR:
            if operation == OperationType.SEARCH:
                query = context.get("title", "")
                return await client.search_media(query)
            elif operation == OperationType.REQUEST:
                # Would need more context to execute
                return {"message": "Please use seerr_request tool with media_type and media_id"}

        elif service == ArrService.PLEX:
            if operation == OperationType.SEARCH:
                query = context.get("title", "")
                return await client.search(query)
            elif operation == OperationType.LIST or operation == OperationType.GET:
                return await client.get_libraries()
            elif operation == OperationType.SCAN:
                return {"message": "Please use plex_scan_library tool with section_id"}
            elif operation == OperationType.PLAY:
                return await client.get_sessions()
            elif operation == OperationType.REFRESH:
                return await client.get_recently_added()

        return {"message": f"Operation {operation.value} not yet implemented for {service.value}"}

    def _handle_explain_intent(self, query: str) -> dict[str, Any]:
        """Explain how a query would be interpreted."""
        explanation = self.router.explain_intent(query)
        return {"explanation": explanation}

    def _handle_list_services(self) -> dict[str, Any]:
        """List all configured services."""
        services = {
            name: {
                "configured": name in self.clients,
                "url": getattr(self.config, name).base_url if hasattr(self.config, name) and getattr(self.config, name) else None
            }
            for name in ["sonarr", "radarr", "prowlarr", "bazarr", "seerr"]
        }
        
        # Add Plex servers
        plex_servers_info = {}
        for name, client in self.plex_clients.items():
            plex_config = next((p for p in self.config.plex_servers if p.name == name), None)
            plex_servers_info[name] = {
                "configured": True,
                "url": plex_config.base_url if plex_config else client.base_url
            }
        
        if plex_servers_info:
            services["plex_servers"] = plex_servers_info
        
        return {
            "enabled_services": self.config.enabled_services,
            "services": services
        }

    async def _handle_system_status(self) -> dict[str, Any]:
        """Get system status for all services."""
        statuses = {}
        
        # Handle regular services
        for name, client in self.clients.items():
            try:
                status = await client.get_system_status()
                statuses[name] = {
                    "online": True,
                    "status": status
                }
            except Exception as e:
                statuses[name] = {
                    "online": False,
                    "error": str(e)
                }
        
        # Handle Plex servers
        if self.plex_clients:
            plex_statuses = {}
            for name, client in self.plex_clients.items():
                try:
                    status = await client.get_server_identity()
                    plex_statuses[name] = {
                        "online": True,
                        "status": status
                    }
                except Exception as e:
                    plex_statuses[name] = {
                        "online": False,
                        "error": str(e)
                    }
            if plex_statuses:
                statuses["plex_servers"] = plex_statuses
        
        return statuses

    async def _handle_sonarr_tool(self, name: str, arguments: dict) -> Any:
        """Handle Sonarr-specific tools."""
        client = self.clients["sonarr"]

        if name == "sonarr_search_series":
            return await client.lookup_series(arguments["term"])
        elif name == "sonarr_add_series":
            return await client.add_series(**arguments)
        elif name == "sonarr_get_series":
            if "series_id" in arguments:
                return await client.get_series(arguments["series_id"])
            return await client.get_all_series()

    async def _handle_radarr_tool(self, name: str, arguments: dict) -> Any:
        """Handle Radarr-specific tools."""
        client = self.clients["radarr"]

        if name == "radarr_search_movie":
            return await client.lookup_movie(arguments["term"])
        elif name == "radarr_add_movie":
            return await client.add_movie(**arguments)
        elif name == "radarr_get_movies":
            if "movie_id" in arguments:
                return await client.get_movie(arguments["movie_id"])
            return await client.get_all_movies()

    async def _handle_prowlarr_tool(self, name: str, arguments: dict) -> Any:
        """Handle Prowlarr-specific tools."""
        client = self.clients["prowlarr"]

        if name == "prowlarr_search":
            return await client.search(**arguments)
        elif name == "prowlarr_get_indexers":
            return await client.get_all_indexers()
        elif name == "prowlarr_sync_apps":
            return await client.sync_all_applications()

    async def _handle_bazarr_tool(self, name: str, arguments: dict) -> Any:
        """Handle Bazarr-specific tools."""
        client = self.clients["bazarr"]

        if name == "bazarr_search_subtitles":
            if arguments["media_type"] == "series":
                return await client.search_series_subtitles(
                    arguments["media_id"],
                    arguments.get("episode_id")
                )
            return await client.search_movie_subtitles(arguments["media_id"])
        elif name == "bazarr_download_subtitle":
            if arguments["media_type"] == "episode":
                return await client.download_series_subtitle(
                    arguments["media_id"],
                    arguments["language"]
                )
            return await client.download_movie_subtitle(
                arguments["media_id"],
                arguments["language"]
            )

    async def _handle_seerr_tool(self, name: str, arguments: dict) -> Any:
        """Handle Seerr-specific tools."""
        client = self.clients["seerr"]

        if name == "seerr_search":
            return await client.search_media(arguments["query"])
        elif name == "seerr_request":
            return await client.create_request(**arguments)
        elif name == "seerr_get_requests":
            return await client.get_requests(filter=arguments.get("filter"))
        elif name == "seerr_approve_request":
            return await client.approve_request(arguments["request_id"])

    def _get_plex_tools(self) -> list[Tool]:
        """Get Plex-specific tools with optional server selection."""
        plex_servers = list(self.plex_clients.keys())
        server_description = ""
        if len(plex_servers) > 1:
            server_description = f". Available servers: {', '.join(plex_servers)}"
        
        return [
            Tool(
                name="plex_get_libraries",
                description=f"Get all Plex libraries{server_description}",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "server": {"type": "string", "description": "Plex server name (optional, uses default if not specified)"}
                    }
                }
            ),
            Tool(
                name="plex_search",
                description=f"Search Plex for media{server_description}",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "server": {"type": "string", "description": "Plex server name (optional, uses default if not specified)"}
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="plex_get_recently_added",
                description=f"Get recently added media{server_description}",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "description": "Max items", "default": 50},
                        "server": {"type": "string", "description": "Plex server name (optional, uses default if not specified)"}
                    }
                }
            ),
            Tool(
                name="plex_get_on_deck",
                description=f"Get On Deck (in progress) media{server_description}",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "server": {"type": "string", "description": "Plex server name (optional, uses default if not specified)"}
                    }
                }
            ),
            Tool(
                name="plex_get_sessions",
                description=f"Get currently playing sessions{server_description}",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "server": {"type": "string", "description": "Plex server name (optional, uses default if not specified)"}
                    }
                }
            ),
            Tool(
                name="plex_scan_library",
                description=f"Scan a Plex library for new content{server_description}",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "section_id": {"type": "integer", "description": "Library section ID"},
                        "server": {"type": "string", "description": "Plex server name (optional, uses default if not specified)"}
                    },
                    "required": ["section_id"]
                }
            ),
            Tool(
                name="plex_mark_watched",
                description=f"Mark media as watched{server_description}",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "rating_key": {"type": "string", "description": "Media rating key"},
                        "server": {"type": "string", "description": "Plex server name (optional, uses default if not specified)"}
                    },
                    "required": ["rating_key"]
                }
            ),
            Tool(
                name="plex_list_servers",
                description="List all configured Plex servers",
                inputSchema={"type": "object", "properties": {}}
            ),
        ]

    async def _handle_plex_tool(self, name: str, arguments: dict) -> Any:
        """Handle Plex-specific tools with server selection."""
        if name == "plex_list_servers":
            return {
                "servers": [
                    {
                        "name": name,
                        "host": config.host,
                        "port": config.port
                    }
                    for name, config in [(p.name, p) for p in self.config.plex_servers]
                ]
            }
        
        # Get server name from arguments (optional)
        server_name = arguments.get("server")
        client = self._get_plex_client(server_name)
        
        if not client:
            available = list(self.plex_clients.keys())
            return {
                "error": f"Plex server '{server_name}' not found" if server_name else "No Plex servers configured",
                "available_servers": available
            }

        if name == "plex_get_libraries":
            return await client.get_libraries()
        elif name == "plex_search":
            return await client.search(arguments["query"])
        elif name == "plex_get_recently_added":
            return await client.get_recently_added(limit=arguments.get("limit", 50))
        elif name == "plex_get_on_deck":
            return await client.get_on_deck()
        elif name == "plex_get_sessions":
            return await client.get_sessions()
        elif name == "plex_scan_library":
            return await client.scan_library(arguments["section_id"])
        elif name == "plex_mark_watched":
            return await client.mark_watched(arguments["rating_key"])

    async def run(self) -> None:
        """Run the MCP server."""
        from mcp.server.stdio import stdio_server

        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


    def _get_tracearr_tools(self) -> list[Tool]:
        """Get Tracearr tools for streaming access management."""
        return [
            Tool(
                name="tracearr_streams",
                description="List currently active Plex/Jellyfin streams across all servers",
                inputSchema={"type": "object", "properties": {}}
            ),
            Tool(
                name="tracearr_stats",
                description="Get Tracearr dashboard stats: active streams, total users, recent violations",
                inputSchema={"type": "object", "properties": {}}
            ),
            Tool(
                name="tracearr_users",
                description="List Tracearr-tracked users with trust scores and violation counts",
                inputSchema={"type": "object", "properties": {}}
            ),
            Tool(
                name="tracearr_violations",
                description="List account-sharing violations detected by Tracearr",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "default": 25},
                        "resolved": {"type": "boolean", "description": "Filter by resolved status (omit for all)"}
                    }
                }
            ),
            Tool(
                name="tracearr_history",
                description="Get Tracearr session history with optional username filter",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "default": 25},
                        "username": {"type": "string", "description": "Filter by username"}
                    }
                }
            ),
            Tool(
                name="tracearr_terminate",
                description="Terminate an active stream by session ID",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "stream_id": {"type": "string", "description": "Session ID from tracearr_streams"},
                        "reason": {"type": "string", "description": "Reason message shown to user"}
                    },
                    "required": ["stream_id"]
                }
            ),
        ]

    async def _handle_tracearr_tool(self, name: str, arguments: dict) -> Any:
        """Handle Tracearr tool calls."""
        client: TracearrClient = self.clients["tracearr"]

        if name == "tracearr_streams":
            return await client.streams()
        elif name == "tracearr_stats":
            return await client.stats()
        elif name == "tracearr_users":
            return await client.users()
        elif name == "tracearr_violations":
            return await client.violations(
                limit=arguments.get("limit", 25),
                resolved=arguments.get("resolved"),
            )
        elif name == "tracearr_history":
            return await client.history(
                limit=arguments.get("limit", 25),
                username=arguments.get("username"),
            )
        elif name == "tracearr_terminate":
            return await client.terminate_stream(
                stream_id=arguments["stream_id"],
                reason=arguments.get("reason"),
            )
        return {"error": f"Unknown tracearr tool: {name}"}


def main():
    """Main entry point."""
    import sys

    # Load configuration
    config = ArrSuiteConfig()

    # Create and run server
    server = ArrSuiteMCPServer(config)

    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)


if __name__ == "__main__":
    main()
