# Generated by Django 3.0.7 on 2021-02-09 07:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recorder', '0009_auto_20210209_0736'),
    ]

    operations = [
        migrations.AddField(
            model_name='recording',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
