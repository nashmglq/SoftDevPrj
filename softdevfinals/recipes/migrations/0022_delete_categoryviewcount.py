# Generated by Django 5.1.1 on 2024-10-06 02:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_remove_profile_category_views'),
        ('recipes', '0021_categoryviewcount'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CategoryViewCount',
        ),
    ]
