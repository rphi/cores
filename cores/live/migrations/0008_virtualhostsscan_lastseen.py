# Generated by Django 2.2.2 on 2019-07-16 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('live', '0007_auto_20190716_1157'),
    ]

    operations = [
        migrations.AddField(
            model_name='virtualhostsscan',
            name='lastseen',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
