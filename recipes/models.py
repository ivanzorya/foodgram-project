from django.db import models
from django.contrib.auth.models import User


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор рецепта"
    )
    image = models.ImageField(upload_to='recipes/', blank=True, null=True)
    title = models.TextField(
        verbose_name="Название рецепта",
        max_length=200,
        help_text="Соблюдайте правила орфографии и пунктуации"
    )
    description = models.TextField(
        verbose_name="Описание рецепта",
        max_length=2000,
        help_text="Соблюдайте правила орфографии и пунктуации"
    )
    time = models.PositiveIntegerField(
        verbose_name="Время приготовления",
    )
    is_lunch = models.BooleanField(default=False)
    is_breakfast = models.BooleanField(default=False)
    is_dinner = models.BooleanField(default=False)


class Ingredient(models.Model):
    title = models.TextField(
        verbose_name="Название ингредиента",
        max_length=200
    )
    dimension = models.TextField(
        verbose_name="Единица измерения ингредиента",
        max_length=200
    )


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        null=True,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Рецепт"
    )
    ingredient = models.ForeignKey(
        Ingredient,
        null=True,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Ингредиент"
    )
    count = models.PositiveIntegerField(
        verbose_name="Количество",
    )


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Пользователь"
    )
    recipe = models.ForeignKey(
        Recipe,
        null=True,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Рецепт"
    )
