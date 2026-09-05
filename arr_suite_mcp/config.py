"""Configuration management for arr suite MCP server."""

import os
from typing import Optional, List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ArrServiceConfig(BaseSettings):
    """Base configuration for arr services."""

    host: str = Field(default="localhost", description="Service host address")
    port: int = Field(description="Service port")
    api_key: str = Field(description="Service API key")
    ssl: bool = Field(default=False, description="Use HTTPS")
    base_path: str = Field(default="", description="Base path for the service")

    @property
    def base_url(self) -> str:
        """Construct the base URL for the service."""
        protocol = "https" if self.ssl else "http"
        base = f"{protocol}://{self.host}:{self.port}"
        if self.base_path:
            base += f"/{self.base_path.strip('/')}"
        return base


class SonarrConfig(ArrServiceConfig):
    """Sonarr-specific configuration."""

    port: int = Field(default=8989)

    model_config = SettingsConfigDict(env_prefix="SONARR_")


class RadarrConfig(ArrServiceConfig):
    """Radarr-specific configuration."""

    port: int = Field(default=7878)

    model_config = SettingsConfigDict(env_prefix="RADARR_")


class ProwlarrConfig(ArrServiceConfig):
    """Prowlarr-specific configuration."""

    port: int = Field(default=9696)

    model_config = SettingsConfigDict(env_prefix="PROWLARR_")


class BazarrConfig(ArrServiceConfig):
    """Bazarr-specific configuration."""

    port: int = Field(default=6767)

    model_config = SettingsConfigDict(env_prefix="BAZARR_")


class SeerrConfig(ArrServiceConfig):
    """Seerr-specific configuration."""

    port: int = Field(default=5055)

    model_config = SettingsConfigDict(env_prefix="SEERR_")


class TracearrConfig(ArrServiceConfig):
    """Tracearr configuration — streaming access manager."""

    port: int = Field(default=3000)

    model_config = SettingsConfigDict(env_prefix="TRACEARR_")


class PlexConfig(BaseSettings):
    """Plex Media Server configuration."""

    name: str = Field(default="default", description="Plex server name/identifier")
    host: str = Field(default="localhost", description="Plex server host address")
    port: int = Field(default=32400, description="Plex server port")
    token: str = Field(description="Plex authentication token")
    ssl: bool = Field(default=False, description="Use HTTPS")

    # Backwards compatibility - also support PLEX_ prefix for single server
    model_config = SettingsConfigDict(
        env_prefix="PLEX_",
        extra="ignore"
    )

    @property
    def base_url(self) -> str:
        """Construct the base URL for Plex."""
        protocol = "https" if self.ssl else "http"
        return f"{protocol}://{self.host}:{self.port}"


class ArrSuiteConfig(BaseSettings):
    """Main configuration for the arr suite MCP server."""

    # Service configurations
    sonarr: Optional[SonarrConfig] = None
    radarr: Optional[RadarrConfig] = None
    prowlarr: Optional[ProwlarrConfig] = None
    bazarr: Optional[BazarrConfig] = None
    seerr: Optional[SeerrConfig] = None
    tracearr: Optional[TracearrConfig] = None

    # Legacy single plex config (for backwards compatibility)
    plex: Optional[PlexConfig] = None
    
    # Multiple plex servers support
    plex_servers: List[PlexConfig] = []

    # Global settings
    request_timeout: int = Field(default=30, description="API request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum number of retry attempts")
    log_level: str = Field(default="INFO", description="Logging level")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore"
    )

    def __init__(self, **kwargs):
        """Initialize configuration, attempting to load each service."""
        super().__init__(**kwargs)

        # Try to initialize each service config from environment
        try:
            self.sonarr = SonarrConfig()
        except Exception:
            pass

        try:
            self.radarr = RadarrConfig()
        except Exception:
            pass

        try:
            self.prowlarr = ProwlarrConfig()
        except Exception:
            pass

        try:
            self.bazarr = BazarrConfig()
        except Exception:
            pass

        try:
            self.seerr = SeerrConfig()
        except Exception:
            pass

        try:
            self.tracearr = TracearrConfig()
        except Exception:
            pass

        # Backwards compatibility: try to load single PLEX_ config
        try:
            self.plex = PlexConfig()
            # If we have a single plex config, add it to plex_servers
            if self.plex and self.plex.token:
                self.plex_servers.append(self.plex)
        except Exception:
            pass

        # Load multiple Plex servers from PLEX_1_, PLEX_2_, etc.
        self._load_plex_servers()

    def _load_plex_servers(self) -> None:
        """Load multiple Plex servers from numbered environment variables."""
        # Scan for PLEX_N_ prefixed env vars
        plex_indices = set()
        for key in os.environ.keys():
            if key.startswith("PLEX_") and key[5].isdigit():
                # Extract the number (e.g., PLEX_1_HOST -> 1)
                parts = key[5:].split("_", 1)
                if parts[0].isdigit():
                    plex_indices.add(int(parts[0]))

        # Load each Plex server config
        for idx in sorted(plex_indices):
            try:
                prefix = f"PLEX_{idx}_"
                
                # Create custom PlexConfig with this prefix
                class NumberedPlexConfig(BaseSettings):
                    name: str = Field(default=f"plex{idx}")
                    host: str = Field(default="localhost")
                    port: int = Field(default=32400)
                    token: str = Field(...)
                    ssl: bool = Field(default=False)
                    
                    model_config = SettingsConfigDict(env_prefix=prefix)
                
                config = NumberedPlexConfig()
                if config.token:
                    plex_config = PlexConfig(
                        name=config.name,
                        host=config.host,
                        port=config.port,
                        token=config.token,
                        ssl=config.ssl
                    )
                    # Avoid duplicates (if PLEX_1_ is same as PLEX_)
                    if not any(s.token == plex_config.token and s.host == plex_config.host for s in self.plex_servers):
                        self.plex_servers.append(plex_config)
                        
            except Exception:
                # Skip if required fields missing
                pass

    @property
    def enabled_services(self) -> list[str]:
        """Return list of enabled services."""
        services = []
        if self.sonarr and self.sonarr.api_key:
            services.append("sonarr")
        if self.radarr and self.radarr.api_key:
            services.append("radarr")
        if self.prowlarr and self.prowlarr.api_key:
            services.append("prowlarr")
        if self.bazarr and self.bazarr.api_key:
            services.append("bazarr")
        if self.seerr and self.seerr.api_key:
            services.append("seerr")
        if self.tracearr and self.tracearr.api_key:
            services.append("tracearr")
        # Add each Plex server with its name
        for plex in self.plex_servers:
            if plex.token:
                services.append(f"plex:{plex.name}")
        return services

    def get_plex_config(self, name: Optional[str] = None) -> Optional[PlexConfig]:
        """Get a specific Plex config by name, or the first one if name is None."""
        if not self.plex_servers:
            return None
        if name:
            for plex in self.plex_servers:
                if plex.name == name:
                    return plex
            return None
        return self.plex_servers[0] if self.plex_servers else None
