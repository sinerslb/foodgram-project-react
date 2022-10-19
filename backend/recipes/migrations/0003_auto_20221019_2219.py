# Generated by Django 2.2.19 on 2022-10-19 22:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_auto_20221018_0413'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(db_index=True, max_length=100, verbose_name='Название ингредиента'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='name',
            field=models.CharField(db_index=True, max_length=100, verbose_name='Название рецепта'),
        ),
    ]