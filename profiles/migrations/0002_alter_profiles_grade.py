# Generated by Django 4.1.3 on 2022-12-09 17:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("profiles", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profiles",
            name="grade",
            field=models.IntegerField(default=1),
        ),
    ]
