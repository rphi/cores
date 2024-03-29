# Generated by Django 2.2.2 on 2019-06-18 12:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='asset_no',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name='host',
            name='asset_no',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='host',
            name='rack',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='inventory.Rack'),
        ),
        migrations.AlterField(
            model_name='host',
            name='serial_no',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='nic',
            name='model',
            field=models.CharField(blank=True, max_length=30),
        ),
    ]
