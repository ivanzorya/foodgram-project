from django.urls import path, include
from rest_framework.routers import SimpleRouter, Route, DefaultRouter

from api import views


urlpatterns = [
    path('ingredients/', views.get_ingredient),
    path('favorites/', views.add_favorite),
    path('favorites/<int:recipe_id>/', views.delete_favorite),
    path('favorites/', views.add_favorite),
    path('favorites/<int:recipe_id>/', views.delete_favorite),

]
