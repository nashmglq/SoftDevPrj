# Generated by Django 5.1.1 on 2024-09-28 02:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0008_alter_rating_score'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rating',
            name='score',
            field=models.DecimalField(decimal_places=1, max_digits=4),
        ),
    ]
