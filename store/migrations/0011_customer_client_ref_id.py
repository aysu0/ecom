# Generated by Django 5.0.2 on 2024-05-01 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0010_alter_profile_address1_alter_profile_address2_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='client_ref_id',
            field=models.CharField(default=23, max_length=20, unique=True),
            preserve_default=False,
        ),
    ]
