# Generated by Django 2.1.1 on 2019-04-27 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0018_logs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logs',
            name='content',
            field=models.CharField(max_length=251),
        ),
    ]
