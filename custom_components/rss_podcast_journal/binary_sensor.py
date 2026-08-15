"""Binary sensor platform for rss_podcast_journal."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from .entity import RssPodcastJournalEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import RssPodcastJournalDataUpdateCoordinator
    from .data import RssPodcastJournalConfigEntry

ENTITY_DESCRIPTIONS = (
    BinarySensorEntityDescription(
        key="episode_downloaded",
        name="Today's Episode Downloaded",
        icon="mdi:podcast",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: RssPodcastJournalConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary_sensor platform."""
    async_add_entities(
        RssPodcastJournalBinarySensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class RssPodcastJournalBinarySensor(RssPodcastJournalEntity, BinarySensorEntity):
    """Binary sensor indicating whether today's episode has been downloaded."""

    def __init__(
        self,
        coordinator: RssPodcastJournalDataUpdateCoordinator,
        entity_description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description

    @property
    def is_on(self) -> bool:
        """Return true if today's episode has been downloaded."""
        return self.coordinator.data is not None
