# Generated by Django 2.2.2 on 2019-06-17 15:08

import booking.models.bookable
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bookable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('created', 'Created'), ('active', 'Active'), ('suspended', 'Suspended'), ('inactive', 'Inactive')], default=booking.models.bookable.BookableStatus('Created'), max_length=30)),
                ('comment', models.CharField(blank=True, max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField(blank=True, null=True)),
                ('comment', models.CharField(max_length=300)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('bookable', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservations', to='booking.Bookable')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='reservations', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('comment', models.CharField(max_length=300)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('bookable', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='booking.Bookable')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bookings', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]