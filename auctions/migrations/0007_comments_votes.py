# Generated by Django 3.2.7 on 2021-09-15 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_alter_category_cat_items'),
    ]

    operations = [
        migrations.AddField(
            model_name='comments',
            name='votes',
            field=models.IntegerField(default=0),
        ),
    ]
