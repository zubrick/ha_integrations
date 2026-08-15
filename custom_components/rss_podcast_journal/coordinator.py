"""DataUpdateCoordinator for rss_podcast_journal."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import RssPodcastJournalApiClientError
from .const import CONF_FEEDS

if TYPE_CHECKING:
    from datetime import date, timedelta
    from logging import Logger

    from homeassistant.core import HomeAssistant

    from .api import LatestEpisode
    from .data import RssPodcastJournalConfigEntry


class RssPodcastJournalDataUpdateCoordinator(
    DataUpdateCoordinator["LatestEpisode | None"]
):
    """Coordinator that periodically checks for and downloads today's episode."""

    config_entry: RssPodcastJournalConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        logger: Logger,
        name: str,
        update_interval: timedelta,
        config_entry: RssPodcastJournalConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            logger,
            name=name,
            update_interval=update_interval,
            config_entry=config_entry,
        )
        self._last_downloaded_date: date | None = None

    async def _async_update_data(self) -> LatestEpisode | None:
        """Check the configured feeds and download today's episode if it is new."""
        runtime_data = self.config_entry.runtime_data
        try:
            episode = await runtime_data.client.async_find_todays_episode(
                self.config_entry.data[CONF_FEEDS],
            )
            if episode is not None and episode.published != self._last_downloaded_date:
                await runtime_data.client.async_download_episode(
                    episode.audio_url,
                    runtime_data.destination,
                )
                self._last_downloaded_date = episode.published
        except RssPodcastJournalApiClientError as exception:
            raise UpdateFailed(str(exception)) from exception

        return episode
