# Generated by Django 4.2.8 on 2024-10-04 08:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0013_remove_recipe_category_delete_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='category',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
