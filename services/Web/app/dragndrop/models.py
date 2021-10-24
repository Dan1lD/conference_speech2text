from django.db import models
from django.utils import timezone


# Create your models here.
class AudioRecord(models.Model):
    audioFileName = models.CharField(max_length=259)
    actualFileName = models.CharField(max_length=68)
    actualTranscriptionFileName = models.CharField(max_length=68)
    actualWordCloudFileName = models.CharField(max_length=68)
    hashCode = models.CharField(max_length=64)
    keyWords = models.TextField()
    transcriptionShort = models.CharField(max_length=32)
    title = models.CharField(max_length=32)
    creationDate = models.DateTimeField(editable=False)
    v2t_response = models.CharField(max_length=8000000)
    def __str__(self):
        return self.title
    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        self.creationDate = timezone.now()
        return super(AudioRecord, self).save(*args, **kwargs)