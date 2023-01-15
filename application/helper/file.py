from flask import current_app as app
from datetime import datetime
import base64
import os
import binascii
from aiohttp import ClientSession
from requests.exceptions import HTTPError
import moviepy.editor as mp


class File:

    async def upload2bucket(self, bucket_name, file_name, file_path):
        print("[INICIO] upload2bucket {}".format(datetime.now()))
        try:
            cf_url = app.config["GCP_CF"]["upload_to_storage"]

            payload = {"bucket_name": bucket_name, "file_name": file_name}
            payload["file"] = open(file_path, 'rb')
            headers = {}
            async with ClientSession() as session:
                try:
                    response = await session.post(cf_url, headers=headers, data=payload)
                    # response.raise_for_status()
                    #print(f"Cloud Response status ({cf_url}): {response.status}")
                except HTTPError as http_err:
                    print(f"HTTP error occurred: {http_err}")
                except Exception as err:
                    print(f"An error ocurred: {err}")
                result = await response.json()

        except Exception as e:
            print('Error:' + str(e))
        print("[FIN] upload2bucket {}".format(datetime.now()))
        return {"local_url": result["bucket_url"], "public_url": result["public_url"]}

    def save_local(self, file_id, video_base64):
        try:
            print(f"save_local {datetime.now()} start")
            _video_extension = app.config["MEDIA_EXTENSIONS"]["video"]

            video_file = f"security_video_{file_id}.{_video_extension}"
            video_path = os.path.join(
                app.root_path, app.config["MEDIA_ROUTES"]["video"], video_file)

            byte = base64.b64decode(video_base64)
            video = open(video_path, "wb")
            video.write(byte)
            video.close

            file_size = os.path.getsize(video_path)
            if file_size > app.config["FILE_SIZE"]["video_max_upload"]:
                video_name_resized = f"security_video_{file_id}_resized.{_video_extension}"
                video_path_resized = os.path.join(app.root_path, app.config["MEDIA_ROUTES"]["video"], video_name_resized)

                clip = mp.VideoFileClip(video_path)
                if clip.rotation in (90, 270):
                    clip = clip.resize(clip.size[::-1])
                    clip.rotation = 0

                clip.write_videofile(video_path_resized, preset="superfast")

                resized_file = os.path.getsize(video_path_resized)
                if resized_file > app.config["FILE_SIZE"]["video_max_upload"]:
                    return -1
                else:
                    os.rename(video_path_resized, video_path)
        except binascii.Error:
            return False
        print(f"save_local {datetime.now()} end")
        return {"video_path": video_path, "video_name": video_file}

    def delete_local(self, file_path):
        os.remove(file_path)
