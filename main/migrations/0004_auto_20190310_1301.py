# Generated by Django 2.1.1 on 2019-03-10 10:01

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20190310_1258'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutorial',
            name='tutorial_published',
            field=models.DateTimeField(default=datetime.datetime(2019, 3, 10, 13, 1, 12, 846424), verbose_name='date published'),
        ),
    ]
