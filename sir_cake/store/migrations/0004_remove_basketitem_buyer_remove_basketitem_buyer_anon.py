# Generated by Django 4.0.4 on 2022-10-24 09:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_rename_order_package_basketitem_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='basketitem',
            name='buyer',
        ),
        migrations.RemoveField(
            model_name='basketitem',
            name='buyer_anon',
        ),
    ]
