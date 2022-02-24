# Generated by Django 4.0.2 on 2022-02-24 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_assignment_edited_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='submission',
            name='text',
        ),
        migrations.AddField(
            model_name='submission',
            name='url',
            field=models.URLField(default='https://colab.research.google.com/drive/1aH557zE-6mwyZEJSh0FdRoDQh3DHgi_f?usp=sharing', max_length=500),
            preserve_default=False,
        ),
    ]
