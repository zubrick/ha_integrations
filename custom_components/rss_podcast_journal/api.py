"""API client for rss_podcast_journal."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import aiohttp
import feedparser
from homeassistant.util import dt as dt_util

if TYPE_CHECKING:
    from datetime import date

    from homeassistant.core import HomeAssistant


class RssPodcastJournalApiClientError(Exception):
    """Exception to indicate a general API error."""


class RssPodcastJournalApiClientCommunicationError(
    RssPodcastJournalApiClientError,
):
    """Exception to indicate a communication error."""


@dataclass
class LatestEpisode:
    """Metadata about the latest episode found for today."""

    feed_url: str
    audio_url: str
    published: date


def _find_audio_link(entry: feedparser.FeedParserDict) -> str | None:
    """Return the audio enclosure URL for a feed entry, if any."""
    for link in entry.get("links", []):
        if link.get("type") in ("audio/mpeg", "video/mp3"):
            return link.get("href")
    return None


class RssPodcastJournalApiClient:
    """Client that finds and downloads today's podcast episode."""

    def __init__(self, hass: HomeAssistant, session: aiohttp.ClientSession) -> None:
        """Initialize the client."""
        self._hass = hass
        self._session = session

    async def async_validate_feeds(self, feeds: list[str]) -> None:
        """Raise if any of the feeds cannot be parsed."""
        for feed_url in feeds:
            await self._async_parse_feed(feed_url)

    async def async_find_todays_episode(self, feeds: list[str]) -> LatestEpisode | None:
        """Return the first feed's episode published today, if any."""
        today = dt_util.now().date()
        for feed_url in feeds:
            parsed = await self._async_parse_feed(feed_url)
            if not parsed.entries:
                continue
            entry = parsed.entries[0]
            published = entry.get("published_parsed")
            if published is None:
                continue
            if (published.tm_year, published.tm_mon, published.tm_mday) != (
                today.year,
                today.month,
                today.day,
            ):
                continue
            audio_url = _find_audio_link(entry)
            if audio_url is not None:
                return LatestEpisode(
                    feed_url=feed_url, audio_url=audio_url, published=today
                )
        return None

    async def async_download_episode(self, audio_url: str, destination: str) -> None:
        """Download the audio file at `audio_url` to `destination`."""
        try:
            async with asyncio.timeout(30):
                response = await self._session.get(audio_url)
                response.raise_for_status()
                content = await response.read()
        except TimeoutError as exception:
            msg = f"Timeout downloading episode - {exception}"
            raise RssPodcastJournalApiClientCommunicationError(msg) from exception
        except aiohttp.ClientError as exception:
            msg = f"Error downloading episode - {exception}"
            raise RssPodcastJournalApiClientCommunicationError(msg) from exception

        await self._hass.async_add_executor_job(_write_file, destination, content)

    async def _async_parse_feed(self, feed_url: str) -> feedparser.FeedParserDict:
        """Parse a feed in the executor and raise on failure."""
        parsed = await self._hass.async_add_executor_job(feedparser.parse, feed_url)
        if parsed.bozo:
            msg = f"Could not parse feed {feed_url} - {parsed.bozo_exception}"
            raise RssPodcastJournalApiClientCommunicationError(msg)
        return parsed


def _write_file(destination: str, content: bytes) -> None:
    """Write `content` to `destination`, creating the parent directory if needed."""
    Path(destination).parent.mkdir(parents=True, exist_ok=True)
    with Path(destination).open("wb") as file:
        file.write(content)
