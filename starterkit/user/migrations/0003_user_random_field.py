# Generated by Django 3.1 on 2021-04-19 21:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_user_unique_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='random_field',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
    ]
