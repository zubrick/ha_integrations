# RSS Podcast Journal

This is a Homeassistant custom integration that gets the latest podcast of the current day from a list of rss feeds in sequential order until it finds one and download it in the www directory under the desired name for playing on connected speakers.

I've done this integration, because I like to listen to the news during breakfast, and the way local radio uploads the podcast for the latest journal is so random, that I have to fallback to a less interesting feed if the episode of the day is not uploaded already and even sometime to a third one.

# Install

* You need to have HACS already installed
* Add the current repository in the custom repositories using the 3 dots on the top right
* Click download
* Restart Homeassistant
* Go in Settings -> Devices & Integration and add the integration

# Usage

Add an automation that calls the rss_podcast_journal.get_latest_episode action.

If it succeeds, the file will be placed with the configured name inside the www folder and will then be accessible on the /local path of your Homeassistant.

For exemple, if you leave journal.mp3 it will be accessible from http://homeassistant.local:8123/local/journal.mp3 (if you have your homeassistant on http://homeassistant.local:8123)
