# Generated by Django 3.2.5 on 2021-07-23 03:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscribe', '0009_alter_subscriber_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscriber',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]
