# Generated by Django 2.2.4 on 2020-08-31 06:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('harrastuspassi', '0021_hobby_event_recurrence_start_event'),
    ]

    operations = [
        migrations.AddField(
            model_name='hobby',
            name='next_event',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='hobby_via_next_event', to='harrastuspassi.HobbyEvent', verbose_name='Next event'),
        ),
    ]
