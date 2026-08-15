"""Adds config flow for RSS Podcast Journal."""

from __future__ import annotations

from pathlib import Path

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import RssPodcastJournalApiClient, RssPodcastJournalApiClientError
from .const import (
    CONF_FEEDS,
    CONF_FILENAME,
    DEFAULT_FEEDS,
    DEFAULT_FILENAME,
    DOMAIN,
    LOGGER,
)


def _parse_feeds(raw_feeds: str) -> list[str]:
    """Split the textarea input into a list of non-empty feed URLs."""
    return [line.strip() for line in raw_feeds.splitlines() if line.strip()]


def _is_valid_filename(filename: str) -> bool:
    """
    Return True if `filename` is a bare file name with no path components.

    `hass.config.path()` joins this value with os.path.join, which silently
    discards the config/www prefix if the value is (or contains) an absolute
    path, e.g. "/etc/passwd". Rejecting anything but a bare name prevents
    writing outside the www directory.
    """
    return filename not in ("", ".", "..") and Path(filename).name == filename


class RssPodcastJournalFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for RSS Podcast Journal."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        _errors = {}
        feeds: list[str] = []
        if user_input is not None:
            feeds = _parse_feeds(user_input[CONF_FEEDS])
            if not feeds:
                _errors["base"] = "no_feeds"
            elif not _is_valid_filename(user_input[CONF_FILENAME]):
                _errors["base"] = "invalid_filename"
            else:
                try:
                    await self._test_feeds(feeds)
                except RssPodcastJournalApiClientError as exception:
                    LOGGER.warning(exception)
                    _errors["base"] = "invalid_feed"

            if not _errors:
                return self.async_create_entry(
                    title="RSS Podcast Journal",
                    data={
                        CONF_FEEDS: feeds,
                        CONF_FILENAME: user_input[CONF_FILENAME],
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_FEEDS,
                        default="\n".join(feeds or DEFAULT_FEEDS),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(multiline=True),
                    ),
                    vol.Required(
                        CONF_FILENAME,
                        default=(user_input or {}).get(CONF_FILENAME, DEFAULT_FILENAME),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT
                        ),
                    ),
                },
            ),
            errors=_errors,
        )

    async def _test_feeds(self, feeds: list[str]) -> None:
        """Validate that the feeds can be parsed."""
        client = RssPodcastJournalApiClient(
            hass=self.hass,
            session=async_get_clientsession(self.hass),
        )
        await client.async_validate_feeds(feeds)
