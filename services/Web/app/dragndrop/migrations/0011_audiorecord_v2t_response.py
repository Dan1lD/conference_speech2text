# Generated by Django 3.1.6 on 2021-10-24 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dragndrop', '0010_audiorecord_actualwordcloudfilename'),
    ]

    operations = [
        migrations.AddField(
            model_name='audiorecord',
            name='v2t_response',
            field=models.CharField(default='', max_length=8000000),
            preserve_default=False,
        ),
    ]