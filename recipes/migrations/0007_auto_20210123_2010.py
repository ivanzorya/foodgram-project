# Generated by Django 2.2.6 on 2021-01-23 20:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_shoppinglist'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ['-pk']},
        ),
        migrations.AlterField(
            model_name='recipe',
            name='author',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to=settings.AUTH_USER_MODEL, verbose_name='Автор рецепта'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(default=1, upload_to='recipes/'),
            preserve_default=False,
        ),
    ]
