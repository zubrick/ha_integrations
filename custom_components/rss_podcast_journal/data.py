"""Custom types for rss_podcast_journal."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import RssPodcastJournalApiClient
    from .coordinator import RssPodcastJournalDataUpdateCoordinator


type RssPodcastJournalConfigEntry = ConfigEntry[RssPodcastJournalData]


@dataclass
class RssPodcastJournalData:
    """Runtime data for the RSS Podcast Journal integration."""

    client: RssPodcastJournalApiClient
    coordinator: RssPodcastJournalDataUpdateCoordinator
    integration: Integration
    destination: str
