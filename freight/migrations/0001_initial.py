# Generated by Django 2.0.6 on 2018-06-20 20:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Character',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(db_index=True, max_length=64, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=256)),
                ('volume', models.DecimalField(decimal_places=5, max_digits=32)),
                ('status', models.SmallIntegerField(choices=[(0, 'Outstanding'), (1, 'In progress'), (2, 'Finished (issuer)'), (3, 'Finished (contractor)'), (4, 'Finished'), (5, 'Canceled'), (6, 'Rejected'), (7, 'Failed'), (8, 'Deleted'), (9, 'Reversed'), (10, 'Disappeared')], db_index=True)),
                ('collateral', models.DecimalField(decimal_places=2, max_digits=32)),
                ('reward', models.DecimalField(decimal_places=2, max_digits=32)),
                ('date_accepted', models.DateTimeField(null=True)),
                ('date_completed', models.DateTimeField(null=True)),
                ('date_expired', models.DateTimeField()),
                ('date_issued', models.DateTimeField()),
                ('days_to_complete', models.SmallIntegerField()),
                ('acceptor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='accepted_contracts', to='freight.Character')),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('full_name', models.CharField(max_length=64)),
                ('short_name', models.CharField(max_length=64)),
            ],
        ),
        migrations.AddField(
            model_name='contract',
            name='end_location',
            field=models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.CASCADE, related_name='end_contracts', to='freight.Location'),
        ),
        migrations.AddField(
            model_name='contract',
            name='issuer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='issued_contracts', to='freight.Character'),
        ),
        migrations.AddField(
            model_name='contract',
            name='start_location',
            field=models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.CASCADE, related_name='start_contracts', to='freight.Location'),
        ),
    ]
