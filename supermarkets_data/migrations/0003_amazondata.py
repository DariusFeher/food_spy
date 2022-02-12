# Generated by Django 3.2.7 on 2022-02-12 22:04

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supermarkets_data', '0002_auto_20220207_1906'),
    ]

    operations = [
        migrations.CreateModel(
            name='AmazonData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('protected_tokens', django.contrib.postgres.fields.jsonb.JSONField()),
                ('products_data', django.contrib.postgres.fields.jsonb.JSONField()),
            ],
        ),
    ]
