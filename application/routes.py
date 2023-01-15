from flask import request, jsonify, url_for
from flask import current_app as app
from application import dal
import os, json
import asyncio
from application.modules.analysis import analysis_tasks
from application.helper.file import File
from application.helper.media import Media

def add_log(request, response, status_code, company_id):
    if 'video' in request:
        del request["video"]

    if 'images' in response:
        del response["images"]

    try:
        klog = {"request": json.dumps(request), "response": json.dumps(response), "code": status_code, "company_id": company_id}
        dal.save_log(klog)
    except Exception as e:
        print("Oops!  ", e.__class__, "occurred.")
        message = [str(x) for x in e.args]
        print(message)


@app.route('/')
def root():

    return jsonify({"message": "security", "path": url_for('static', filename='audio/demo.mp3')})


@app.route('/getToken', methods=["POST"])
def get_token():
    _auth = request.authorization
    _djson = request.get_json(force=True)

    status_code = app.config["CODE_OK"]
    if 'company_id' in _djson:
        company_id = _djson["company_id"]
        r_creds = dal.get_credentials(company_id)
        valid = False
        if r_creds is not None:
            _user, _pwd = r_creds["user"], r_creds["password"]
            if (_auth.username == _user and _auth.password == _pwd):
                valid = True

        if valid:
            token = dal.generate_token()["token"]
            dal.set_token(token, company_id)
            dict_rst = {"token": token}
        else:
            status_code = app.config["CODE_UNAUTHORIZED"]
            dict_rst = {'error': 'Unauthorized'}
    else:
        status_code = app.config["CODE_BAD_REQUEST"]
        dict_rst = {'error': 'Bad Request'}

    return jsonify(dict_rst), status_code
'''
@app.route('/media')
def media():
    try:
        file_name = request.args.get('file_name')
        file_type = request.args.get('file_type')
        company_id = request.args.get('company_id')
        host = request.headers.get('host')
        print(host)
    except Exception as e:
        status_code = app.config["CODE_BAD_REQUEST"]
        dict_rst = {'error': 'Bad Request or invalid parameters'}

    if (file_name == '' or file_name == None) or (file_type == '' or file_type == None) or (company_id == '' or company_id == None):
        return jsonify({"error": "Bad Request"}), 400
    config_class = Config()
    local_config = config_class.getConfig(company_id)
    common = Common(local_config)
    route = common.getDirectoryFile(file_type)
    file = "{}{}".format(route, file_name)
    return send_file(file, as_attachment=True, attachment_filename=file_name)
'''
@app.route('/getTextFromVideo', methods=["POST"])
def video_text():
    _auth = request.headers["authorization"]
    _djson = request.get_json(force=True)

    status_code = app.config["CODE_OK"]
    _company_id = None
    if set(('company_id', 'transaction_id', 'otp', 'video')) == set(_djson):
        _auth_tk = _auth.replace("Bearer ", "")
        _company_id, _otp = _djson["company_id"], _djson["otp"]
        _transaction_id = _djson["transaction_id"].strip()
        _b64_video = _djson["video"].strip()

        r_tk = dal.get_token(_company_id)

        valid = False
        if r_tk is not None:
            if r_tk["token"] == _auth_tk:
                valid = True

        if valid:
            r_save_local = File().save_local(_transaction_id, _b64_video)

            if r_save_local == False:
                status_code = app.config["CODE_BAD_REQUEST"]
                dict_rst = {"error": "Bad Request",
                            "message": "invalid base64 video"}
            elif r_save_local == -1:
                status_code = app.config["CODE_BAD_REQUEST"]
                dict_rst = {"error": "Bad Request",
                            "message": "The uploaded file exceeds the maximum allowed size"}
            else:
                settings = dal.get_settings(_company_id)
                media = Media(settings)

                worker_data = {"settings": settings, "video_path": r_save_local["video_path"]}
                audio_data = worker_data.copy()
                audio_data.update({"video_name": r_save_local["video_name"], "company_id": _company_id})

                ktasks = {"liveness": worker_data, "audio": audio_data, "frame": worker_data }
                r_bucket_video, rspeech, rliveness, rframe64 = asyncio.run(
                    analysis_tasks(_transaction_id, ktasks))
                print(r_bucket_video)
                # print(rspeech, rliveness, rframe64)

                text = media.clearNumber(rspeech["text"])
                dict_rst = {"transaction_id": _transaction_id, "otp": text,
                            "liveness": {
                                "percentage": rliveness["percentage"],
                                "prediction": rliveness["prediction"],
                                "client_percentage": rliveness["client_percentage"]},
                            "images": rframe64["images"],
                            "video_bucket": rspeech["paths"]["video_bucket"]}
        else:
            status_code = app.config["CODE_UNAUTHORIZED"]
            dict_rst = {'error': 'Unauthorized'}
    else:
        status_code = app.config["CODE_BAD_REQUEST"]
        dict_rst = {'error': 'Bad Request or invalid parameters'}

    response = dict_rst.copy()
    add_log(_djson, response, status_code, _company_id)

    return jsonify(dict_rst), status_code
