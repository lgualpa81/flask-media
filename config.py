class Config:
    FLASK_ENV = 'development'
    SECRET_KEY = '7110c8ae51a4b5af97be6534caef90e4bb9bdcb3380af008f90b23a5d1616bf319bc298105da20fe'

    FLASK_DEBUG = True
    DEBUG = True
    # Database configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # environ.get("DB_URI")
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://gcp-instance/analysis"

    CODE_BAD_REQUEST = 400
    CODE_NOT_FOUND = 404
    CODE_OK = 200
    CODE_UNAUTHORIZED = 401

    MEDIA_ROUTES = {
        "video": "static/video/",
        "image": "static/image/",
        "audio": "static/audio/",
        "audio_bucket": "security-multimedia",
        "video_bucket": "security-multimedia",
        "public_file": "https://gcp-bucket/media"
    }

    RECONOSERID = {
        "liveness_url": "https://datahubprod.reconoserid.net/video",
        "token": ""
    }

    MEDIA_EXTENSIONS = {
        "audio": "ogg",
        "video": "mp4",
        "image": "png"
    }

    FILE_SIZE = {
        "video_max_upload": 10*1024*1024
    }

    IMAGE_RESOLUTION = {
        "height": 1024,
        "width": 720
    }

    GCP_CF = {
        "upload_to_storage": "https://gcp.cloudfunctions.net/upload_to_storage",
        "speech_to_text": "https://gcp.cloudfunctions.net/SpeechToText"
    }
