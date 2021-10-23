import sys

sys.path.append('/app/punctuation-restoration/src/')

import json
import os
import wave

import funct
import requests
from celery import Celery
from celery.result import AsyncResult
from flask import Flask
from vosk import KaldiRecognizer, Model, SetLogLevel

model = Model("/app/model")


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


@celery.task(name="tasks.recognize")
def recognize(filename_ext):
    fn = filename_ext.split('.')[0]
    if filename_ext.split('.')[-1] == "mp4":
        os.system(f"ffmpeg -i /audio/{filename_ext} -vn -acodec libmp3lame -ac 2 -ab 160k -ar 48000 /audio/{fn}.mp3")
        os.remove(f"/audio/{filename_ext}")
        filename_ext = fn + ".mp3"
    os.system(
        f"ffmpeg -i /audio/{filename_ext} -acodec pcm_s16le -ac 1 -ar 16000 /audio/wav/{fn}.wav -y -af 'apad=pad_dur=10'")

    wf = wave.open(f'/audio/wav/{fn}.wav', "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        return json.dumps({"ok": False, "error": "Audio file must be WAV format mono PCM."})

    rec = KaldiRecognizer(model, wf.getframerate())

    result_with_timestamps = []
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            result_with_timestamps.append(res)

    full_result = json.loads(rec.FinalResult())
    full_text = full_result.pop("text")
    """
    full_result in format:
    {'result': [{'conf': 1.0, 'end': 0.51, 'start': 0.09, 'word': 'родион'}, {'conf': 1.0, 'end': 1.29, 'start': 0.51, 'word': 'потапыч'}, {'conf': 0.939228, 'end': 2.31, 'start': 1.5, 'word': 'высчитывал'}, {'conf': 1.0, 'end': 2.88, 'start': 2.31057, 'word': 'каждый'}, {'conf': 1.0, 'end': 3.21, 'start': 2.88, 'word': 'новый'}, {'conf': 1.0, 'end': 3.72, 'start': 3.21, 'word': 'вершок'}, {'conf': 1.0, 'end': 4.53, 'start': 3.72, 'word': 'углубления'}, {'conf': 1.0, 'end': 4.95, 'start': 4.8, 'word': 'и'}, {'conf': 1.0, 'end': 5.43, 'start': 4.95, 'word': 'давно'}, {'conf': 1.0, 'end': 6.24, 'start': 5.46, 'word': 'определил'}, {'conf': 1.0, 'end': 6.45, 'start': 6.27, 'word': 'про'}, {'conf': 1.0, 'end': 6.96, 'start': 6.45, 'word': 'себя'}], 'text': 'родион потапыч высчитывал каждый новый вершок углубления и давно определил про себя'}
    """
    result_text = funct.inference("weights.pt", full_text)
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


@flask_app.route('/runRawKeywords')
def run_raw_keywords():
    res = calculate_and_save_raw_keywords.delay()
    return json.dumps({"ok": True, "error": None, "task_id": res.id})


if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=8000)


"""
ps = ['а', 'но', 'или', 'что', 'как', 'чтобы', 'с', 'к', 'на', 'от', 'над', 'по', 'у', 'о', 'под', 'из', 'без', 'для', 'до', 'в', 'около', 'об', 'за']
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