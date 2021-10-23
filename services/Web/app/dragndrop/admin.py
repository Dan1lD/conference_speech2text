from django.contrib import admin
from dragndrop.models import AudioRecord

# Register your models here.
class AudioRecordAdmin(admin.ModelAdmin):
    readonly_fields = ('creationDate',)

admin.site.register(AudioRecord, AudioRecordAdmin)
