"""API clients for arr services."""

from .base import (
    BaseArrClient,
    ArrClientError,
    ArrClientConnectionError,
    ArrClientAuthError,
    ArrClientNotFoundError
)
from .sonarr import SonarrClient
from .radarr import RadarrClient
from .prowlarr import ProwlarrClient
from .bazarr import BazarrClient
from .seerr import SeerrClient
from .plex import PlexClient
from .tracearr import TracearrClient

__all__ = [
    "BaseArrClient",
    "ArrClientError",
    "ArrClientConnectionError",
    "ArrClientAuthError",
    "ArrClientNotFoundError",
    "SonarrClient",
    "RadarrClient",
    "ProwlarrClient",
    "BazarrClient",
    "SeerrClient",
    "PlexClient",
    "TracearrClient",
]
