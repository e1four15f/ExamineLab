# Generated by Django 2.1.1 on 2019-04-26 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_task_solution'),
    ]

    operations = [
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('extention', models.CharField(max_length=10)),
                ('launch_command', models.CharField(max_length=50)),
                ('optional_arguments', models.CharField(max_length=150)),
            ],
            options={
                'verbose_name_plural': 'Languages',
            },
        ),
    ]
