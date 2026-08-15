"""Sensor platform for rss_podcast_journal."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription

from .entity import RssPodcastJournalEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import RssPodcastJournalDataUpdateCoordinator
    from .data import RssPodcastJournalConfigEntry

ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="latest_episode",
        name="Latest Episode Date",
        icon="mdi:calendar-clock",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: RssPodcastJournalConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    async_add_entities(
        RssPodcastJournalSensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class RssPodcastJournalSensor(RssPodcastJournalEntity, SensorEntity):
    """Sensor exposing the date of the latest downloaded episode."""

    def __init__(
        self,
        coordinator: RssPodcastJournalDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description

    @property
    def native_value(self) -> str | None:
        """Return the date of the latest downloaded episode."""
        episode = self.coordinator.data
        return episode.published.isoformat() if episode else None

    @property
    def extra_state_attributes(self) -> dict[str, str] | None:
        """Return the feed and audio URL of the latest episode."""
        episode = self.coordinator.data
        if episode is None:
            return None
        return {"feed_url": episode.feed_url, "audio_url": episode.audio_url}
