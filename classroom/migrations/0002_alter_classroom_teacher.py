# Generated by Django 4.0.2 on 2022-05-23 13:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('classroom', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classroom',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teaching_classrooms', to=settings.AUTH_USER_MODEL),
        ),
    ]
