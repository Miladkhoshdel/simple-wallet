# Generated by Django 4.2.13 on 2024-05-24 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallets', '0005_remove_scheduledwithdrawal_settle_transaction_settle'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='bank_message',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='bank_status_code',
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
    ]
