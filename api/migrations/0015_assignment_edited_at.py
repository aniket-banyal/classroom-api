# Generated by Django 4.0.2 on 2022-02-22 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_submission'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='edited_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
