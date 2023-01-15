from flask import current_app as app
import asyncio
import json
from datetime import datetime
from .media import Media
from aiohttp import ClientSession
from requests.exceptions import HTTPError


class Liveness:

    def __init__(self, settings):
        #self.common = Common(config)
        self.media = Media(settings)
        self.settings = settings["liveness"]

    async def getLiveness(self, file_id, video_path):
        url = app.config["RECONOSERID"]["liveness_url"]

        try:
            print("***** Comenzamos Liveness {}".format(datetime.now()))
            short_path = self.media.shortVideo(file_id, video_path)
            payload = {"account_token": app.config["RECONOSERID"]["token"],
                       "file": open(short_path, 'rb')}

            headers = {}

            async with ClientSession() as session:
                try:
                    response = await session.post(url, headers=headers, data=payload)
                    # response.raise_for_status()
                    #print(f"Response status ({url}): {response.status}")
                except HTTPError as http_err:
                    print(f"HTTP error occurred: {http_err}")
                except Exception as err:
                    print(f"An error ocurred: {err}")
                result = await response.json()

            if "result:" in result:
                if result["result:"]["avg_prob"] == 'N/A':
                    client_percentage = False
                else:
                    client_percentage = True if float(result["result:"]["avg_prob"]) >= float(
                        self.config["real"]) else False
                return {"percentage": result["result:"]["avg_prob"], "prediction": result["result:"]["video_prediction"], "client_percentage": client_percentage}
        except Exception as e:
            print("***getLiveness[ERROR] [URL]{} [Files]{} [Error]{}".format(
                url, str(short_path), str(e)))
            return False
