# Generated by Django 5.1.5 on 2025-02-01 06:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mydash', '0002_alter_researchcenter_numbering'),
    ]

    operations = [
        migrations.CreateModel(
            name='TimeRange',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
            ],
        ),
    ]
