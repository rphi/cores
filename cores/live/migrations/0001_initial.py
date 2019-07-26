# Generated by Django 2.2.2 on 2019-06-17 15:08

from django.db import migrations, models
import django.db.models.deletion
import live.models
import polymorphic.showfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScanSession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('agent_identifier', models.CharField(max_length=100)),
                ('raw_data', models.TextField()),
                ('processed', models.BooleanField(default=False, help_text="Has this session's data been successfully processed?")),
                ('result', models.TextField(help_text='Output of ingest process')),
            ],
        ),
        migrations.CreateModel(
            name='ScanConflict',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('new', 'New'), ('resolved', 'Resolved'), ('ignore', 'Ignored'), ('super', 'Superseded')], default='new', max_length=8)),
                ('polymorphic_ctype', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_live.scanconflict_set+', to='contenttypes.ContentType')),
                ('scan', models.ForeignKey(on_delete=live.models.NON_POLYMORPHIC_CASCADE, to='live.ScanSession')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=(polymorphic.showfields.ShowFieldType, models.Model),
        ),
        migrations.CreateModel(
            name='NicScanConflict',
            fields=[
                ('scanconflict_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='live.ScanConflict')),
                ('newip', models.GenericIPAddressField(null=True)),
                ('nic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.Nic')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('live.scanconflict',),
        ),
        migrations.CreateModel(
            name='LocationScanConflict',
            fields=[
                ('scanconflict_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='live.ScanConflict')),
                ('host', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.Host')),
                ('newlab', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='inventory.Lab')),
                ('nsc', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='live.NicScanConflict')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('live.scanconflict',),
        ),
    ]