# Generated by Django 3.2.7 on 2021-09-15 07:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0004_alter_category_cat_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='cat_items',
            field=models.ManyToManyField(null=True, to='auctions.Listing'),
        ),
    ]