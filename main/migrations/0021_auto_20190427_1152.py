# Generated by Django 2.1.1 on 2019-04-27 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0020_auto_20190427_1138'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='language',
            name='optional_arguments',
        ),
        migrations.AddField(
            model_name='language',
            name='optional',
            field=models.CharField(default='rm <path>*', max_length=350),
        ),
    ]