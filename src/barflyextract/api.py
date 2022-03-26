import json
import os

import googleapiclient.discovery  # type: ignore[import]

TARGET_USER_ID = "UCu9ArHUJZadlhwt3Jt0tqgA"


def scrape_playlist_items(youtube, playlist_id):
    items_per_page = 50
    items_yielded = 0
    max_items = 999
    request_kwargs = dict(
        maxResults=items_per_page, part="snippet", playlistId=playlist_id
    )

    request = youtube.playlistItems().list(**request_kwargs)
    response = request.execute()
    for item in response["items"]:
        yield item["snippet"]

        items_yielded += 1
        if items_yielded >= max_items:
            return

    while response.get("nextPageToken"):
        request_kwargs.update({"pageToken": response.get("nextPageToken")})
        request = youtube.playlistItems().list(**request_kwargs)
        response = request.execute()

        for item in response["items"]:
            yield item["snippet"]

            items_yielded += 1
            if items_yielded >= max_items:
                return


def run():
    youtube = googleapiclient.discovery.build(
        "youtube", "v3", developerKey=os.environ["API_KEY"]
    )

    request = youtube.channels().list(  # pylint: disable=no-member
        id=TARGET_USER_ID, part="contentDetails"
    )
    response = request.execute()

    playlist_id = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    playlist = scrape_playlist_items(youtube, playlist_id)

    print(json.dumps(list(playlist), indent=4))


if __name__ == "__main__":
    run()
