"""Functions for scraping from our data source."""

import json
import os
import sys
from collections.abc import Iterator
from contextlib import AbstractContextManager, nullcontext
from typing import Any, TextIO, TypedDict

import googleapiclient.discovery

TARGET_USER_ID = "UCu9ArHUJZadlhwt3Jt0tqgA"


class PlaylistItem(TypedDict):
    """A subset of fields from a YouTube playlist item."""

    title: str
    description: str


def scrape_playlist_items(youtube: Any, playlist_id: str) -> Iterator[PlaylistItem]:
    """Scrape the given YouTube playlist for all its items."""
    items_per_page = 50
    items_yielded = 0
    max_items = 999
    request_kwargs = {
        "maxResults": items_per_page,
        "part": "snippet",
        "playlistId": playlist_id,
    }

    response = None
    while not response or response.get("nextPageToken"):
        if response:
            request_kwargs["pageToken"] = response.get("nextPageToken")

        request = youtube.playlistItems().list(**request_kwargs)
        response = request.execute()

        for item in response["items"]:
            yield item["snippet"]

            items_yielded += 1
            if items_yielded >= max_items:
                return


def scrape_user_uploads(api_key: str, user_id: str) -> Iterator[PlaylistItem]:
    """Scrape the given YouTube user's uploads playlist for all its items."""
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)

    request = youtube.channels().list(id=user_id, part="contentDetails")
    response = request.execute()

    playlist_id = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    return scrape_playlist_items(youtube, playlist_id)


def run() -> None:
    """Scrape the YouTube user's uploads playlist for all its items.

    If a filename is given, writes the resulting JSON to that file. Otherwise,
    writes to stdout.
    """
    playlist = scrape_user_uploads(os.environ["API_KEY"], TARGET_USER_ID)
    cm: TextIO | AbstractContextManager[TextIO] = (
        nullcontext(sys.stdout) if len(sys.argv) <= 1 else open(sys.argv[1], "w")
    )
    with cm as outfile:
        print(json.dumps(list(playlist), indent=4), file=outfile)


if __name__ == "__main__":
    run()
