from flask import current_app as app
import asyncio
import json
import os
from datetime import datetime

from moviepy.editor import *

from aiohttp import ClientSession
from requests.exceptions import HTTPError
from .file import File


class Speech:

    def __init__(self, file_id, video_path, video_name, settings, company_id):
        self.file_id = file_id
        self.video_path = video_path
        self.video_name = video_name
        self.company_id = company_id

        self.settings_video = json.loads(settings["video"])


    async def speech2text(self, _bucket):
        url_function = app.config["GCP_CF"]["speech_to_text"]

        print("[INICIO] getTextToVoice {} [audio_path {}] [url {}]".format(
            datetime.now(), _bucket["local_url"], url_function))
        payload = {"url_file": _bucket["local_url"]}
        headers = {"Content-Type": "application/json"}        

        async with ClientSession() as session:
            try:
                response = await session.post(url_function, headers=headers, json=payload)
                #response.raise_for_status()
                #print(f"Response status ({url_function}): {response.status}")
            except HTTPError as http_err:
                print(f"HTTP error occurred: {http_err}")
            except Exception as err:
                print(f"An error ocurred: {err}")
            result = await response.text()
        print("[FIN] getTextToVoice {} result {} ".format(
            datetime.now(), result))
        return result

    async def __convert_video_to_audio(self, clip):
        print("__convert_video_to_audio {} start".format(datetime.now()))
        audio_file = "audio_otp_{}.{}".format(
            self.file_id, app.config["MEDIA_EXTENSIONS"]["audio"])
        audio_path = os.path.join(app.root_path, app.config["MEDIA_ROUTES"]["audio"], audio_file)
        audio = clip.audio
        audio.write_audiofile(audio_path)
        print("__convert_video_to_audio[BUCKET] {} end".format(datetime.now()))
        bucket_path = await File().upload2bucket(
            app.config["MEDIA_ROUTES"]["audio_bucket"], audio_file, audio_path)
        speech2text = await self.speech2text(bucket_path)
        return speech2text

    async def __videoProcess(self, video_path):
        clip = VideoFileClip(video_path)
        print("__videoValidate[convert_in_clip] {} {}".format(
            datetime.now(), video_path))
        if clip.duration > self.settings_video["max_duration"]:
            return {"valid": False, "message": "Video cannot exceed {} sec".format(self.settings_video["max_duration"])}
        print("__videoValidate[guardar_video] {}".format(datetime.now()))
        #audio_path = self.__convert_video_to_audio(clip)
        text = await self.__convert_video_to_audio(clip)        
        #imagenes = self.common.captureFrame(clip)
        #images = self.common.converImageBase64(imagenes["images"])

        return {"valid": True, "message": "OK", "text": text, "images": ""}

    async def videoToAudio(self):
        try:            
            video_process = await self.__videoProcess(self.video_path)
            if video_process["valid"] == False:
                return {"video_path": False, "message": video_process["message"]}
            video_public = "{}?company_id={}&file_type={}&file_name={}".format(
                app.config["MEDIA_ROUTES"]["public_file"], self.company_id, "video", self.video_name)
            return {"video_path": True, "text": video_process["text"], "paths": {"video": self.video_path, "video_bucket": video_public}, "images": video_process["images"]}
        except Exception as e:
            print("ERROR {}".format(str(e)))
            return {"video_path": False, "message": "base64 is not valid", "error": str(e)}
