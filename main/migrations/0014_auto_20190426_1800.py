# Generated by Django 2.1.1 on 2019-04-26 18:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_language'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='language',
            name='launch_command',
        ),
        migrations.RemoveField(
            model_name='language',
            name='optional_arguments',
        ),
    ]
