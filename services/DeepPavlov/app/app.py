import os
from get_keywords import create_keywords
from sentence_transformers import SentenceTransformer
import json
import time
from flask import Flask
from celery import Celery
from celery.result import AsyncResult
from nltk.stem.snowball import SnowballStemmer
import requests


sentence_transformer_model = SentenceTransformer('/app/paraphrase-xlm-r-multilingual-v1')
stemmer = SnowballStemmer("russian") 


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


@celery.task(name="dp_tasks.calculate_and_save_keywords")
def calculate_and_save_keywords(filename):
    text = open(f"/data/key_extractor/{filename}", encoding="utf-8").read()
    keywords = create_keywords(sentence_transformer_model, text)
    keywords_text = ", ".join(keywords)
    keywords_text = keywords_text[0].upper() + keywords_text[1:]
    requests.post("http://nginx/uploadKeywords", data={"keywords": keywords_text, "filename": filename})
    return keywords



@flask_app.route('/getKeywords/<string:process_id>')
def get_keywords(process_id):
    res = AsyncResult(process_id, app=celery)

    if res.state == "SUCCESS":
        return json.dumps({"ok": True, "keywords": res.get(), "done": True})
    return json.dumps({"ok": False})


@flask_app.route('/runKeywords/<string:filename>')
def run_keywords(filename):
    res = calculate_and_save_keywords.delay(filename)
    return json.dumps({"ok": True, "error": None, "task_id": res.id})


@flask_app.route('/runRawKeywords')
def run_raw_keywords():
    res = calculate_and_save_raw_keywords.delay()
    return json.dumps({"ok": True, "error": None, "task_id": res.id})

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=8080)