from django.contrib import admin

from .models import Recipe, Ingredient, RecipeIngredient, Favorite


class RecipeAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", 'author', 'favorite')
    list_filter = ("title", 'author', 'is_breakfast', 'is_dinner', 'is_lunch')

    def favorite(self, recipe):
        return len(recipe.favorites.all())
    favorite.short_description = "Число добавлений в избранное"


class IngredientAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", 'dimension')
    list_filter = ("title", )


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ("pk", 'recipe', 'ingredient', 'count')
    list_filter = ('recipe',)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "recipe")


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(Favorite, FavoriteAdmin)
