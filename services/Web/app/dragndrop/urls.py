from django.urls import path

from . import views

urlpatterns = [
    path('', views.index),
    path('downloadFile', views.downloadFile),
    path('uploadFile', views.uploadFile),
    path('uploadUrl', views.updloadUrl),
    path('transcription', views.transcription),
    path('deleteAudio', views.deleteAudio),
    path('showImg', views.showImg),
    path('uploadText', views.uploadText),
    path('uploadKeywords', views.uploadKeywords),
    path('saveText', views.saveText)
]
