import asyncio, os
from datetime import datetime
from flask import current_app as app
from application.helper.speech import Speech
from application.helper.media import Media
from application.helper.file import File
from application.helper.liveness import Liveness
#import moviepy.editor as mp

async def worker_liveness(file_id, settings, video_path):
    print(f"==== TASK worker_liveness start {datetime.now()}")
    liveness = Liveness(settings)
    r = await liveness.getLiveness(file_id, video_path)
    print(f"==== TASK worker_liveness end {datetime.now()}")
    return r


async def worker_speech(file_id, settings, video_path, video_name, company_id):
    print(f"==== TASK worker_speech start {datetime.now()}")
    speech = Speech(
        file_id, video_path, video_name, settings, company_id)
    r = await speech.videoToAudio()
    print(f"==== TASK worker_speech end {datetime.now()}")
    return r


async def worker_getFrame(file_id, settings, video_path):
    print("==== TASK worker_getFrame {} start".format(datetime.now()))
    media = Media(settings)
    imagenes = media.captureFrame(file_id, video_path)
    frame = media.converImageBase64(imagenes["images"])
    print("==== TASK worker_getFrame {} end".format(datetime.now()))
    return frame

#async def resize_video(video_path, video_path_resized):
#    print("==== TASK resize_video {} start".format(datetime.now()))
#    #compresion video
#    clip = mp.VideoFileClip(video_path)
#    if clip.rotation in (90, 270):
#        clip = clip.resize(clip.size[::-1])
#        clip.rotation = 0
#
#    clip.write_videofile(video_path_resized, preset="superfast")
#    print("==== TASK resize_video {} end".format(datetime.now()))

async def worker_upload_video(file_id, video_path):
    print("==== TASK worker_video_resize {} start".format(datetime.now()))
    _video_extension = app.config["MEDIA_EXTENSIONS"]["video"]
    video_name = f"security_video_{file_id}.{_video_extension}"

    bucket_path = await File().upload2bucket(app.config["MEDIA_ROUTES"]["video_bucket"], video_name, video_path)
    print("||||", bucket_path)
    #os.remove(video_path_resized)
    print("==== TASK worker_video_resize {} end".format(datetime.now()))
    return bucket_path

async def analysis_tasks(file_id, kargs):
    kliveness = kargs["liveness"]
    kaudio = kargs["audio"]
    kframe = kargs["frame"]

    rupload_video, rspeech, rliveness, rframe  = await asyncio.gather(
        worker_upload_video(file_id, kframe["video_path"]),
        worker_speech(file_id, kaudio["settings"], kaudio["video_path"],
                           kaudio["video_name"], kaudio["company_id"]),
        worker_liveness(
            file_id, kliveness["settings"], kliveness["video_path"]),
        worker_getFrame(
            file_id, kframe["settings"], kframe["video_path"]),

    )
    return (rupload_video, rspeech, rliveness, rframe)