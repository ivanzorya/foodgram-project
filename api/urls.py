from django.urls import path

from api import views

urlpatterns = [
    path('ingredients/', views.get_ingredient),
    path('favorites/', views.add_favorite),
    path('favorites/<int:recipe_id>/', views.delete_favorite),
    path('subscriptions/', views.add_subscription),
    path('subscriptions/<int:user_id>/', views.delete_subscription),
    path('purchases/', views.add_purchase),
    path('purchases/<int:recipe_id>/', views.delete_purchase),
]
