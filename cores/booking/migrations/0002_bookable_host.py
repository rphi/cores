# Generated by Django 2.2.2 on 2019-06-17 15:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('booking', '0001_initial'),
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookable',
            name='host',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='inventory.Host'),
        ),
    ]
