# Generated by Django 5.0.2 on 2024-03-18 13:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_remove_product_images'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='image',
            field=models.ImageField(upload_to='uploads/product/'),
        ),
    ]
