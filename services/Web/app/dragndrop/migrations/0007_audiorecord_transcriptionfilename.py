# Generated by Django 3.1.6 on 2021-02-04 23:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dragndrop', '0006_remove_audiorecord_transcription'),
    ]

    operations = [
        migrations.AddField(
            model_name='audiorecord',
            name='transcriptionFileName',
            field=models.CharField(default='', max_length=68),
            preserve_default=False,
        ),
    ]
