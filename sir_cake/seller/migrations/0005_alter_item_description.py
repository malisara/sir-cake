# Generated by Django 4.0.4 on 2022-12-30 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seller', '0004_alter_item_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='description',
            field=models.TextField(blank=True, max_length=100, null=True),
        ),
    ]
