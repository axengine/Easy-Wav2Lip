from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
from werkzeug.utils import secure_filename
import secrets
import json
from collections import defaultdict
import uuid, os, time,sys

# TASK
task_schedule = defaultdict(str)

# APP
app = Flask(__name__, static_folder="static")
CORS(app)

# 设置允许上传的文件扩展名
ALLOWED_EXTENSIONS = {"mp4", "avi", "mov", "mp3", "wav"}

# 配置文件上传的路径
app.config["FACE_UPLOAD_FOLDER"] = "static/uploads_face/"
app.config["AUDIO_UPLOAD_FOLDER"] = "static/uploads_audio/"


# 检查文件扩展名是否被允许
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# 内置视频和音频列表
@app.route("/v1/config", methods=["GET"])
def config():
    with open("config.json") as f:
        config = json.load(f)
    return jsonify({"face": config["face"], "speaker": config["speaker"]}), 200


# 处理上传的文件
@app.route("/v1/process", methods=["POST"])
def process_files():
    video_path, audio_path = "", ""
    if "video" in request.files:
        video_file = request.files["video"]
        if not allowed_file(video_file.filename):
            return (
                jsonify(
                    {
                        "error": "Invalid file format. Allowed formats are: mp4, avi, mov."
                    }
                ),
                400,
            )
        video_filename = secure_filename(video_file.filename)
        video_path = app.config["FACE_UPLOAD_FOLDER"] + video_filename
        video_file.save(video_path)
    if "audio" in request.files:
        audio_file = request.files["audio"]
        if not allowed_file(audio_file.filename):
            return (
                jsonify(
                    {"error": "Invalid file format. Allowed formats are: mp3, wav."}
                ),
                400,
            )
        audio_filename = secure_filename(audio_file.filename)
        audio_path = app.config["AUDIO_UPLOAD_FOLDER"] + audio_filename
        audio_file.save(audio_path)

    if video_path == "":
        video_path = request.form.get("face")
    if audio_path == "":
        text = request.form.get("text")
        language = request.form.get("language")
        speaker = request.form.get("speaker")
        audio_path = app.config["AUDIO_UPLOAD_FOLDER"] + secrets.token_hex(4) + ".wav"
        from tts import tts

        tts.tts_to_file(
            text=text,
            speaker_wav=speaker,
            language=language,
            file_path=audio_path,
            speed=1.0,
        )

    taskId = request.args.get("taskId")
    if taskId is None:
        taskId = str(uuid.uuid4())
    if taskId in task_schedule:
        return (
            jsonify({"error": "Invalid taskId, exist."}),
            400,
        )
    result = defaultdict()
    result["taskId"] = taskId
    task_schedule[taskId] = result
    outfile = os.path.join("static", "output", taskId + ".mp4")

    # 在此处添加视频和音频处理的代码
    # 处理完毕后，生成处理后的视频文件
    t1 = threading.Thread(
        target=video_retalking_handle,
        args=(video_path, audio_path, outfile, result),
    )
    t1.start()

    # 返回处理后的视频文件
    return jsonify({"taskId": taskId}), 200


@app.route("/v1/result", methods=["GET"])
def query_result():
    task_id = request.args.get("taskId")
    result = task_schedule[task_id]
    if not result:
        return jsonify({"fatal": "not found.system fatal."})
    if result:
        if "end" in result:
            result["elapse"] = result["end"] - result["begin"]
        else:
            result["elapse"] = time.time() - result["begin"]
    return jsonify(result)


def video_retalking_handle(face, audio, output, result):
    import subprocess

    command = [
        sys.executable,
        "run_concurrency.py",
        "-video_file",
        face,
        "-vocal_file",
        audio,
        "-output_file",
        output,
    ]
    result["begin"] = time.time()
    try:
        subprocess.run(command)
        result["result"] = output
    except Exception as e:
        result["error"] = str(e)
    result["end"] = time.time()

# def video_retalking_handle(face, audio, output, result):
#     import subprocess

#     command = [
#         "python3",
#         "inference.py",
#         "--Wav2Lip_path",
#         "./checkpoints/checkpoint_step000405000.pth",
#         "--face",
#         face,
#         "--audio",
#         audio,
#         "--outfile",
#         output,
#     ]
#     result["begin"] = time.time()
#     try:
#         process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
#         result["stdout"]=''
#         result["stderr"]=''
#         # 实时获取输出
#         while True:
#             stdout = process.stdout.readline()
#             stderr = process.stderr.readline()
#             if stdout == '' and stderr == '' and process.poll() is not None:
#                 break
#             if stdout:
#                 result["stdout"]+=stdout.strip()
#             if stderr:
#                 result["stderr"]+=stderr.strip()

#         # 等待命令执行完毕
#         process.wait()
#         # 获取最终的返回值
#         result["returncode"] = process.returncode
#         result["result"] = output
#     except Exception as e:
#         result["error"] = str(e)
#     result["end"] = time.time()

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, host="0.0.0.0", port=6002)
