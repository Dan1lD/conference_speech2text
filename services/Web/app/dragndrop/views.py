import base64
import codecs
import hashlib
import os
import shutil
import time
from hashlib import sha256
from os import remove
from os.path import exists, splitext
from shutil import copyfile
import json

import matplotlib.pyplot as plt
import requests
from django.conf import settings
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from dragndrop.models import AudioRecord
from wordcloud import STOPWORDS, WordCloud

os.environ['NO_PROXY'] = '127.0.0.1'

# Create your views here.
def index(request):
    # calculate records with searched keywords
    audioRecordsList = []
    if(request.GET.__contains__('find')):
        find = request.GET['find'].lower().split(' ')
        for audioRecord in AudioRecord.objects.all():
            for findWord in find:
                if(str(audioRecord.keyWords).lower().find(findWord) != -1):
                    audioRecordsList.append(audioRecord)
                    break
    else:
        audioRecordsList = AudioRecord.objects.all()
    return render(request, 'dragndrop/index.html', {
                 'audioRecordsList': audioRecordsList,
                 'SERVER_IP': settings.SERVER_IP
                 })

@csrf_exempt
def uploadFile(request):
    file = request.FILES['file']
    # calculate hashCode
    fileBytes = file.read()
    hashCode = sha256(fileBytes).hexdigest()
    # check if file already in database
    for audioRecord in AudioRecord.objects.all():
        if audioRecord.hashCode == hashCode:
            return HttpResponse('Error 409: file already exist: "' + audioRecord.audioFileName + '".', status=409)
    #  Saving POST'ed file to storage
    actualFileName = hashCode + ".wav"
    filedir = '/app/dragndrop/uploadedfiles/' + actualFileName
    default_storage.save(filedir, file)
    # save filename without flag
    title = splitext(file.name)[0]
    # requestiong transcription
    copyfile(filedir, "/audio/" + actualFileName)
    v2t_response = requests.get(f"http://speech_recognition:8000/recognize/{actualFileName}")

    keyWords = "Обрабатывается"
    wordcloud = WordCloud(width = 1200, height = 650, random_state=1, background_color='white', colormap='bone', collocations=False, stopwords = STOPWORDS).generate(keyWords)
    plt.figure(figsize=(12, 6.5))
    plt.imshow(wordcloud) 
    plt.axis("off")
    actualWordCloudFileName = hashCode + '.png'
    wordCloudPath = '/app/dragndrop/uploadedfiles/' + actualWordCloudFileName
    plt.savefig(wordCloudPath)

    txtFileName = hashCode + ".txt"

    txtFileDir = '/app/dragndrop/uploadedfiles/' + txtFileName
    open(txtFileDir, "w").write("Обрабатывается...")
    transcriptionShort = "Обрабатывается..."

    # add note to database
    newTableLine = AudioRecord(audioFileName=file.name,
                               actualFileName=actualFileName,
                               actualTranscriptionFileName=txtFileName,
                               actualWordCloudFileName=actualWordCloudFileName,
                               hashCode=hashCode,
                               keyWords=keyWords,
                               transcriptionShort=transcriptionShort, 
                               title=title,
                               v2t_response=v2t_response.text,
                               )
    newTableLine.save()
    # return OK
    return HttpResponse("File upload successully")


def download_file(url):
    local_filename = url.split('/')[-1]
    dirname = '/app/dragndrop/uploadedfiles/'
    filename = hashlib.md5(local_filename.encode('utf-8')).hexdigest() + "." + local_filename.split('.')[-1]
    abs_path = dirname + filename
    with requests.get(url, stream=True) as r:
        with open(abs_path, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
    return filename, dirname, abs_path


@csrf_exempt
def updloadUrl(request):
    if "url" not in request.GET.keys():
        return HttpResponse("field 'url' is required ", status=200)
    try:
        url: str = base64.b64decode(request.GET['url'].encode()).decode()
        raw_filename = url.split('/')[-1].split('.')[0]
        filename, dirname, abs_path = download_file(url)
    except Exception as e:
        return HttpResponse("Error in file download ", status=200)
    hash = filename.split(".")[0]
    copyfile(abs_path, "/audio/" + filename)
    v2t_response = requests.get(f"http://speech_recognition:8000/recognize/{filename}")

    keyWords = "Обрабатывается"
    wordcloud = WordCloud(width=1200, height=650, random_state=1, background_color='white', colormap='bone',
                          collocations=False, stopwords=STOPWORDS).generate(keyWords)
    plt.figure(figsize=(12, 6.5))
    plt.imshow(wordcloud)
    plt.axis("off")
    actualWordCloudFileName = hash + '.png'
    wordCloudPath = '/app/dragndrop/uploadedfiles/' + actualWordCloudFileName
    plt.savefig(wordCloudPath)

    txtFileName = hash + ".txt"

    txtFileDir = '/app/dragndrop/uploadedfiles/' + txtFileName
    open(txtFileDir, "w").write("Обрабатывается...")
    transcriptionShort = "Обрабатывается..."

    # add note to database
    newTableLine = AudioRecord(audioFileName=raw_filename,
                               actualFileName=filename,
                               actualTranscriptionFileName=txtFileName,
                               actualWordCloudFileName=actualWordCloudFileName,
                               hashCode=hash,
                               keyWords=keyWords,
                               transcriptionShort=transcriptionShort,
                               title=raw_filename,
                               v2t_response=v2t_response.text,
                               )
    newTableLine.save()
    # return OK
    return HttpResponse("File upload successully")


@csrf_exempt
def uploadText(request):
    text = request.POST["text"]
    filename = request.POST["filename"]

    text = text[0].upper() + text[1:]

    au = AudioRecord.objects.get(actualFileName=filename)
    txtFileName = filename.split(".")[0] + ".txt"
    txtFileDir = '/app/dragndrop/uploadedfiles/' + txtFileName
    open(txtFileDir, "w").write(text)

    copyfile(txtFileDir, "/texts/key_extractor/" + txtFileName)

    requests.get(f"http://deeppavlov:8080/runKeywords/{txtFileName}")

    # get and save keywords
    transcriptionShort = text[:32]
    # make word cloud
    au.transcriptionShort = transcriptionShort
    au.save()
    return HttpResponse("OK")


@csrf_exempt
def uploadKeywords(request):
    filename = request.POST["filename"]
    keyWords = request.POST["keywords"]

    hashCode = filename.split(".")[0]
    actualFileName = hashCode + ".wav"
    au = AudioRecord.objects.get(actualFileName=actualFileName)
    
    wordcloud = WordCloud(width = 1200, height = 650, random_state=1, background_color='white', colormap='bone', collocations=False, stopwords = STOPWORDS).generate(keyWords)
    plt.figure(figsize=(12, 6.5))
    plt.imshow(wordcloud) 
    plt.axis("off")
    actualWordCloudFileName = hashCode + '.png'
    wordCloudPath = '/app/dragndrop/uploadedfiles/' + actualWordCloudFileName
    plt.savefig(wordCloudPath)
    keyWords = keyWords.replace(',', '')
    keyWords = keyWords.replace('.', '')
    keyWords = ", ".join(keyWords.split())
    au.keyWords = keyWords
    au.save()
    return HttpResponse("OK")


def downloadFile(request):
    fileName = request.GET['fileName']
    actualFileName = request.GET['actualFileName']
    file_path = "/app/dragndrop/uploadedfiles/" + actualFileName
    content_types = {'png': 'image/png',
                     'wav': 'audio/wav',
                     'txt': 'text/plain'}
    if exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type=content_types.get(fileName.split('.')[-1], None))
            response['Content-Disposition'] = 'inline; filename=' + fileName
            return response
    return HttpResponse("Error 404: file not found.", status=404)

def transcription(request):
    hashCode = request.GET['hashCode']
    for audioRecord in AudioRecord.objects.all():
        if audioRecord.hashCode == hashCode:
            txtFile = audioRecord.actualTranscriptionFileName
            txtFilePath = '/app/dragndrop/uploadedfiles/' + txtFile
            transcriptionFile = codecs.open(txtFilePath, encoding='utf-8') # magic with ML model of extracting text
            transcriptionText = transcriptionFile.read()
            return render(request, 'dragndrop/transcription.html', {
                'audioRecord': audioRecord,
                'transcriptionText': transcriptionText,
                'SERVER_IP': settings.SERVER_IP,
                'v2t': audioRecord.v2t_response,
            })
    return HttpResponse("Error 404: not found.")


@csrf_exempt
def saveText(request):
    data = json.loads(request.body.decode("utf-8"))
    text = data['text']
    fileName = data['fileName']
    txtFilePath = '/app/dragndrop/uploadedfiles/' + fileName
    with open(txtFilePath, 'w') as file:
        file.write(text)
    return HttpResponse("OK")


def deleteAudio(request):
    hashCode = request.GET['hashCode']
    for audioRecord in AudioRecord.objects.all():
        if audioRecord.hashCode == hashCode:
            audioFilePath = '/app/dragndrop/uploadedfiles/' + audioRecord.actualFileName
            txtFilePath = '/app/dragndrop/uploadedfiles/' + audioRecord.actualTranscriptionFileName
            pngFilePath = '/app/dragndrop/uploadedfiles/' + audioRecord.actualWordCloudFileName
            if exists(audioFilePath):
                remove(audioFilePath)
            if exists(txtFilePath):
                remove(txtFilePath)
            if exists(pngFilePath):
                remove(pngFilePath)
            AudioRecord.objects.filter(id=audioRecord.id).delete()
            return HttpResponse("Audio record deleted successfully")
    return HttpResponse("Error 404: not found.")

def showImg(request):
    actualFileName = request.GET['actualFileName']
    file_path = "/app/dragndrop/static/dragndrop/img/" + actualFileName
    if exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="image/*")
            response['Content-Disposition'] = 'inline; filename=' + actualFileName
            return response
    return HttpResponse("Error 404: file not found.", status=404)
