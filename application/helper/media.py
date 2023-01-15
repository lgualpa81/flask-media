from flask import current_app as app
from datetime import datetime
import cv2
import json
import ffmpeg
import os
import base64
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip


class Media:

    def __init__(self, setting):
        self.setting_video = json.loads(setting["video"])
        self.setting_frame = json.loads(setting["frame"])

    def image_resize(self, file_path, width=None, height=None, inter=cv2.INTER_AREA):
        image = cv2.imread(file_path)
        dim = None
        (h, w) = image.shape[:2]
        if width is None and height is None:
            return image
        if width is None:
            r = height / float(h)
            dim = (int(w * r), height)
        else:
            r = width / float(w)
            dim = (width, int(h * r))
        resized = cv2.resize(image, dim, interpolation=inter)
        cv2.imwrite(file_path, resized, [cv2.IMWRITE_PNG_COMPRESSION, 9])

        return resized

    def captureFrame(self, file_id, video_path):
        vidcap = cv2.VideoCapture(video_path)
        capture = self.setting_frame["tiempo"]
        images = []

        img_extension = app.config["MEDIA_EXTENSIONS"]["image"]
        img_path = app.config["MEDIA_ROUTES"]["image"]
        img_width = app.config["IMAGE_RESOLUTION"]["width"]
        img_height = app.config["IMAGE_RESOLUTION"]["height"]

        for x in capture:
            name = "frame_{}_{}.{}".format(
                str(x), file_id, img_extension)
            file_path = os.path.join(app.root_path, img_path, name)
            t = (1000 * x)
            vidcap.set(cv2.CAP_PROP_POS_MSEC, t)
            ret, frame = vidcap.read()
            cv2.imwrite(file_path, frame)

            #self.rotationImage(file_path, video_path)
            self.image_resize(file_path, height=img_height, width=img_width)
            images.append(file_path)

        return {"images": images}

    def rotationImage(self, file_path, video_path):
        try:
            print("rotationImage {} start".format(datetime.now()))
            meta_dict = ffmpeg.probe(video_path)
            rotation = int(meta_dict['streams'][0]['tags']['rotate'])
            print("Rotation " + str(rotation))
            if rotation != 0:
                img = cv2.imread(file_path)
                if rotation == 90:
                    img_rotate = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
                elif rotation == 180:
                    img_rotate = cv2.rotate(img, cv2.ROTATE_180)
                elif rotation == 270:
                    img_rotate = cv2.rotate(
                        img, cv2.ROTATE_90_COUNTERCLOCKWISE)
                cv2.imwrite(file_path, img_rotate)
        except Exception as e:
            print("Error al rotar la imagen")
        print("rotationImage {} end".format(datetime.now()))

    def converImageBase64(self, arr_image):
        print("converImageBase64 {} start".format(datetime.now()))
        images64 = []
        for x in arr_image:
            file = open(x, "rb")
            img = base64.b64encode(file.read())
            images64.append(img.decode("utf-8"))
            file.close()
            os.remove(x)
        print("converImageBase64 {} end".format(datetime.now()))
        return {"images": images64}

    def clearNumber(self, text):
        number = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
        result = ''
        for x in text:
            if x in number:
                result = result + x
        return result.strip()

    def shortVideo(self, file_id, video_path):
        video_short_file = "reconoserID_{}.{}".format(
            file_id, app.config["MEDIA_EXTENSIONS"]["video"])
        video_short_path = os.path.join(
            app.root_path, app.config["MEDIA_ROUTES"]["video"], video_short_file)
        #clip = VideoFileClip(video_path, has_constant_size=True)
        #short_clip = clip.subclip(self.config_video["initial_cut"], self.config_video["final_cut"])
        # short_clip.write_videofile(video_short_path)
        # return video_short_path

        ffmpeg_extract_subclip(
            video_path,
            self.setting_video["initial_cut"],
            self.setting_video["final_cut"],
            targetname=video_short_path)
        return video_short_path
