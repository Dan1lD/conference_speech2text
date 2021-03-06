import shutil
import sys

sys.path.append('/app/punctuation-restoration/src/')

import json
import os
import wave
import torch

import requests
from celery import Celery
from celery.result import AsyncResult
from flask import Flask
from vosk import KaldiRecognizer, Model
from neuro_comma.src.neuro_comma.predict import RepunctPredictor
from pathlib import Path

model = Model("/app/model")
predictor = RepunctPredictor(model_name='repunct-model-new',
                             models_root=Path('neuro_comma/models'),
                             model_weights='quantized_weights_ep6_9912.pt',
                             quantization=True)


def make_celery(app):
    print(app.import_name)
    celery = Celery(
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL'],
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


flask_app = Flask(__name__)
flask_app.config.update(
    CELERY_BROKER_URL=os.environ.get("CELERY_BROKER"),
    CELERY_RESULT_BACKEND=os.environ.get("CELERY_BACKEND")
)

celery = make_celery(flask_app)


def convert_with_command(ffmpeg_command, fn, filename_ext):
    """ffmpeg_command should convert to wav and save in /audio/wav/{fn}.wav"""
    os.system(ffmpeg_command)
    os.remove(f"/audio/{filename_ext}")
    os.system(
        f"ffmpeg -i /audio/wav/{fn}.wav -acodec pcm_s16le -ac 1 -ar 16000 /audio/wav/{fn}_normalized.wav -y -af 'apad=pad_dur=10'")
    os.remove(f"/audio/wav/{fn}.wav")
    return "/audio/wav/{fn}_normalized.wav"


@celery.task(name="tasks.recognize")
def recognize(filename_ext):
    fn = filename_ext.split('.')[0]
    if filename_ext.split('.')[-1].lower() in ("mp4", "mp3", "ogg", "ape", "aiff"):
        path_wav = convert_with_command(f"ffmpeg -i /audio/{filename_ext} /audio/wav/{fn}.wav", fn, filename_ext)
    else:
        os.system(
            f"ffmpeg -i /audio/{filename_ext} -acodec pcm_s16le -ac 1 -ar 16000 /audio/wav/{fn}_normalized.wav -y -af 'apad=pad_dur=10'")
        path_wav = f"/audio/wav/{fn}_normalized.wav"

    wf = wave.open(path_wav, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        return json.dumps({"ok": False, "error": "Audio file must be WAV format mono PCM."})

    rec = KaldiRecognizer(model, wf.getframerate())

    result_with_timestamps = []
    full_result = ''
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            print(res)
            full_result += ' ' + res['text']

    print(rec.PartialResult())
    # full_result = json.loads(rec.FinalResult())
    print(full_result)
    # full_text = full_result.pop("text")
    result_text = predictor(full_result)
    requests.post("http://nginx/uploadText", data={"text": result_text, "filename": filename_ext, "extra_info": full_result})
    os.remove(f"/audio/{filename_ext}")
    return result_text


@flask_app.route('/getRecognition/<string:process_id>')
def get_recognition(process_id):
    res = AsyncResult(process_id, app=celery)

    if res.state == "SUCCESS":
        return json.dumps({"ok": True, "text": res.get(), "done": True})
    return json.dumps({"ok": False})


@flask_app.route('/recognize/<string:filename>')
def run_recognition(filename):
    res = recognize.delay(filename)
    return json.dumps({"ok": True, "error": None, "task_id": res.id})


# @flask_app.route('/runRawKeywords')
# def run_raw_keywords():
#     res = calculate_and_save_raw_keywords.delay()
#     return json.dumps({"ok": True, "error": None, "task_id": res.id})


if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=8000)


"""
ps = ['??', '????', '??????', '??????', '??????', '??????????', '??', '??', '????', '????', '??????', '????', '??', '??', '??????', '????', '??????', '??????', '????', '??', '??????????', '????', '????']
for i in range(1, len(result)):
    if result[i]['start'] - result[i-1]['end'] < 1:
        paragraphs[-1] += result[i-1]['word'] + ' '
    else:
        if result[i-1]['word'] in ps:
            paragraphs[-1] += result[i-1]['word'] + ' '
        else:
            paragraphs[-1] += result[i-1]['word']
            paragraphs.append('')
paragraphs[-1] += result[len(result)-1]['word']

result_text = " ".join(paragraphs)
"""