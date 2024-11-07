# Generated by Django 5.1.3 on 2024-11-05 05:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=255)),
                ('maiden_name', models.CharField(blank=True, max_length=255, null=True)),
                ('previous_name', models.CharField(blank=True, max_length=255, null=True)),
                ('birthday', models.DateField()),
                ('birth_place', models.CharField(max_length=255)),
                ('grew_up_in', models.CharField(max_length=255)),
                ('insights', models.TextField(blank=True, null=True)),
            ],
        ),
    ]
