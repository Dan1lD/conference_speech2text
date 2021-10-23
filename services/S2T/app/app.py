import sys
sys.path.append('/app/punctuation-restoration/src/')

from vosk import Model, KaldiRecognizer, SetLogLevel
import wave
import os
import json
from flask import Flask
from celery import Celery
from celery.result import AsyncResult
import requests
import funct

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
def recognize(filename):
    fn = filename.split('.')[0]
    os.system(f"ffmpeg -i /audio/{filename} -acodec pcm_s16le -ac 1 -ar 16000 /audio/wav/{fn}.wav -y -af 'apad=pad_dur=10'")

    wf = wave.open(f'/audio/wav/{fn}.wav', "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        return json.dumps({"ok": False, "error": "Audio file must be WAV format mono PCM."})
    
    rec = KaldiRecognizer(model, wf.getframerate())

    result = ""

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            print(res)
            result += ' ' + res['text']

    print(result)
    result_text = result

    # paragraphs = ['']
    # ps = ['а', 'но', 'или', 'что', 'как', 'чтобы', 'с', 'к', 'на', 'от', 'над', 'по', 'у', 'о', 'под', 'из', 'без', 'для', 'до', 'в', 'около', 'об', 'за']
    # for i in range(1, len(result)):
    #     if result[i]['start'] - result[i-1]['end'] < 1:
    #         paragraphs[-1] += result[i-1]['word'] + ' '
    #     else:
    #         if result[i-1]['word'] in ps:
    #             paragraphs[-1] += result[i-1]['word'] + ' '
    #         else:
    #             paragraphs[-1] += result[i-1]['word']
    #             paragraphs.append('')
    # paragraphs[-1] += result[len(result)-1]['word']
    #
    # result_text = " ".join(paragraphs)
    result_text = funct.inference("weights.pt", result_text)

    requests.post("http://nginx/uploadText", data={"text": result_text, "filename": filename})
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