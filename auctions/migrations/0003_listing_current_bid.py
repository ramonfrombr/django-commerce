# Generated by Django 4.1.5 on 2023-01-13 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_alter_listing_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='current_bid',
            field=models.FloatField(null=True),
        ),
    ]
