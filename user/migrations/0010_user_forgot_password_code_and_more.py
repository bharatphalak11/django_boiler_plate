# Generated by Django 5.1.6 on 2025-02-24 06:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0009_user_email_code_created_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='forgot_password_code',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='forgot_password_code_created_date',
            field=models.DateTimeField(null=True),
        ),
    ]
