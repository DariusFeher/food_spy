# Generated by Django 3.2.7 on 2022-02-07 19:06

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('supermarkets_data', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tescodata',
            name='products_data',
            field=django.contrib.postgres.fields.jsonb.JSONField(),
        ),
        migrations.AlterField(
            model_name='tescodata',
            name='protected_tokens',
            field=django.contrib.postgres.fields.jsonb.JSONField(),
        ),
    ]
