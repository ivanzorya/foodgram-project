from django.urls import path

from recipes.views import (
    edit_recipe, get_recipe, delete_recipe, get_follows, get_author,
    get_shopping_list, delete_shopping_list, get_txt, new_recipe,
    RecipeListView, FavoriteListView
)


urlpatterns = [
    path('', RecipeListView.as_view(), name='index'),
    path('new/', new_recipe, name='new'),
    path('edit/<int:recipe_id>/', edit_recipe, name='edit'),
    path('recipes/<int:recipe_id>/', get_recipe, name='recipe'),
    path('delete/<int:recipe_id>/', delete_recipe, name='delete'),
    path('favorite/', FavoriteListView.as_view(), name='favorite'),
    path('follow/', get_follows, name='follow'),
    path('author/<int:user_id>/', get_author, name='author'),
    path('shopping/', get_shopping_list, name='shopping'),
    path(
        'shopping/<int:recipe_id>/',
        delete_shopping_list,
        name='delete_shopping'
    ),
    path('print/', get_txt, name='print'),
]
