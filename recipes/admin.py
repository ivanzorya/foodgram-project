from django.contrib import admin

from .models import Tag, Recipe, Ingredient, RecipeIngredient, \
    RecipeFakeIngredient


class TagAdmin(admin.ModelAdmin):
    list_display = ("pk", "title")


class RecipeAdmin(admin.ModelAdmin):
    list_display = ("pk", "title")


class IngredientAdmin(admin.ModelAdmin):
    list_display = ("pk", "title")


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ("pk",)


# class RecipeFakeIngredientAdmin(admin.ModelAdmin):
#     list_display = ("pk",)


admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
# admin.site.register(RecipeFakeIngredient, RecipeFakeIngredientAdmin)
