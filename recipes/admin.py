from django.contrib import admin

from .models import Recipe, Ingredient, RecipeIngredient, Favorite


class RecipeAdmin(admin.ModelAdmin):
    list_display = ("pk", "title")


class IngredientAdmin(admin.ModelAdmin):
    list_display = ("pk", "title")


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ("pk",)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "recipe")


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(Favorite, FavoriteAdmin)
