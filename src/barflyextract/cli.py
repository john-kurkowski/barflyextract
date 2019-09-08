"""TODO"""

import os
import pprint

import googleapiclient.discovery

TARGET_USER_ID = "UCu9ArHUJZadlhwt3Jt0tqgA"


def run():
    """TODO"""

    youtube = googleapiclient.discovery.build(
        "youtube", "v3", developerKey=os.environ["API_KEY"]
    )

    request = youtube.channels().list(id=TARGET_USER_ID, part="contentDetails")
    response = request.execute()

    playlist_id = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    request = youtube.playlistItems().list(part="snippet", playlistId=playlist_id)
    response = request.execute()

    pprint.pprint(response)


if __name__ == "__main__":
    run()
