from django.urls import path, include
from rest_framework.routers import SimpleRouter, Route, DefaultRouter

from api import views


urlpatterns = [

    path('ingredients/', views.get_ingredient),
]
