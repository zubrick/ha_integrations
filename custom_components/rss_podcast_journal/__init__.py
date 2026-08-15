"""
Custom integration to integrate rss_podcast_journal with Home Assistant.

For more details about this integration, please refer to
https://github.com/zubrick/rss_podcast_journal
"""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.const import Platform
from homeassistant.core import SupportsResponse
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.loader import async_get_loaded_integration

from .api import RssPodcastJournalApiClient, RssPodcastJournalApiClientError
from .const import (
    CONF_FEEDS,
    CONF_FILENAME,
    DOMAIN,
    LOGGER,
    SERVICE_DOWNLOAD_LATEST_EPISODE,
)
from .coordinator import RssPodcastJournalDataUpdateCoordinator
from .data import RssPodcastJournalData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse
    from homeassistant.helpers.typing import ConfigType

    from .data import RssPodcastJournalConfigEntry

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:  # noqa: ARG001
    """Register the integration's services."""

    async def _async_handle_download_latest_episode(
        call: ServiceCall,  # noqa: ARG001 Unused function argument: `call`
    ) -> ServiceResponse:
        """Check the feeds and download today's episode on demand."""
        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            msg = "RSS Podcast Journal is not configured"
            raise HomeAssistantError(msg)

        entry: RssPodcastJournalConfigEntry = entries[0]
        runtime_data = entry.runtime_data
        try:
            episode = await runtime_data.client.async_find_todays_episode(
                entry.data[CONF_FEEDS],
            )
            if episode is not None:
                await runtime_data.client.async_download_episode(
                    episode.audio_url,
                    runtime_data.destination,
                )
            else:
                await runtime_data.client.async_use_fallback_episode(
                    runtime_data.destination,
                )
        except RssPodcastJournalApiClientError as exception:
            raise HomeAssistantError(str(exception)) from exception

        if episode is None:
            return {"downloaded": False}

        runtime_data.coordinator.async_set_updated_data(episode)
        return {
            "downloaded": True,
            "feed_url": episode.feed_url,
            "audio_url": episode.audio_url,
        }

    hass.services.async_register(
        DOMAIN,
        SERVICE_DOWNLOAD_LATEST_EPISODE,
        _async_handle_download_latest_episode,
        supports_response=SupportsResponse.OPTIONAL,
    )
    return True


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(
    hass: HomeAssistant,
    entry: RssPodcastJournalConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    coordinator = RssPodcastJournalDataUpdateCoordinator(
        hass=hass,
        logger=LOGGER,
        name=DOMAIN,
        update_interval=timedelta(minutes=30),
        config_entry=entry,
    )
    entry.runtime_data = RssPodcastJournalData(
        client=RssPodcastJournalApiClient(
            hass=hass,
            session=async_get_clientsession(hass),
        ),
        integration=async_get_loaded_integration(hass, entry.domain),
        coordinator=coordinator,
        destination=hass.config.path("www", entry.data[CONF_FILENAME]),
    )

    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: RssPodcastJournalConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
