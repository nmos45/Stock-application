# Generated by Django 4.2.18 on 2025-01-29 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0004_alter_stockinstance_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockinstance',
            name='name',
            field=models.CharField(default='<django.db.models.query_utils.DeferredAttribute object at 0x104651850>stockroom', max_length=200),
        ),
    ]
