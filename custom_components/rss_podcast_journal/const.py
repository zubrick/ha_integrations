"""Constants for rss_podcast_journal."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "rss_podcast_journal"

CONF_FEEDS = "feeds"
CONF_FILENAME = "filename"

DEFAULT_FEEDS = [
    "https://www.rts.ch/la-1ere/programmes/le-journal-de-6h/podcast/?flux=rss",
    "https://www.rts.ch/la-1ere/programmes/le-journal-horaire/podcast/?flux=rss",
    "https://www.lfm.ch/chronique/lfm-info-journal/feed/",
]
DEFAULT_FILENAME = "journal.mp3"

SERVICE_DOWNLOAD_LATEST_EPISODE = "download_latest_episode"
