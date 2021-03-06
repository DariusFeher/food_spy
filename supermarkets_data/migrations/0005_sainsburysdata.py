# Generated by Django 3.2.7 on 2022-02-16 13:57

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supermarkets_data', '0004_amazondata_products_entities'),
    ]

    operations = [
        migrations.CreateModel(
            name='SainsburysData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('protected_tokens', django.contrib.postgres.fields.jsonb.JSONField()),
                ('products_data', django.contrib.postgres.fields.jsonb.JSONField()),
                ('products_entities', django.contrib.postgres.fields.jsonb.JSONField()),
            ],
        ),
    ]
