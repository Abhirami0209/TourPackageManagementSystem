# Generated by Django 5.2.1 on 2025-05-20 16:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tours', '0009_remove_booking_pickup_point_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='role',
            field=models.CharField(choices=[('user', 'User'), ('vendor', 'Vendor')], max_length=10),
        ),
    ]
