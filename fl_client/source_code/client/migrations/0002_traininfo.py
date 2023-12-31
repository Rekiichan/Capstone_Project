# Generated by Django 4.2.3 on 2023-07-15 10:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrainInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('epoch', models.IntegerField(blank=True, default=0, max_length=50, null=True, verbose_name='epoch')),
                ('batch', models.IntegerField(blank=True, default=0, max_length=50, null=True, verbose_name='batch')),
                ('round', models.IntegerField(blank=True, default=0, max_length=50, null=True, verbose_name='round')),
                ('learning_rate', models.FloatField(blank=True, default=0, max_length=50, null=True, verbose_name='learning_rate')),
                ('percentage_of_dataset', models.FloatField(blank=True, default=0, max_length=50, null=True, verbose_name='percentage_of_dataset')),
                ('mode', models.CharField(blank=True, max_length=50, null=True, verbose_name='mode')),
                ('dataset_name', models.CharField(blank=True, max_length=50, null=True, verbose_name='mode')),
            ],
            options={
                'db_table': 'train_info',
            },
        ),
    ]
