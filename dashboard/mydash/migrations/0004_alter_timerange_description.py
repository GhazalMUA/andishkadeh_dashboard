# Generated by Django 5.1.5 on 2025-02-01 06:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mydash', '0003_timerange'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timerange',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
