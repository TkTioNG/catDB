# Generated by Django 3.1.1 on 2020-10-14 04:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('breeds', '0003_auto_20201014_1129'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='human',
            name='date_of_birth',
        ),
    ]