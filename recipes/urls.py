from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("new/", views.new, name="new"),
    path("edit/<int:recipe_id>", views.edit_recipe, name="edit"),
    path("recipes/<int:recipe_id>", views.get_recipe, name="recipe"),
    path("delete/<int:recipe_id>", views.delete_recipe, name="delete"),
    path("favorite/", views.get_favorities, name="favorite"),
    path("follow/", views.get_follows, name="follow"),
    path("author/<int:user_id>", views.get_author, name="author"),
    path("shopping/", views.get_shopping_list, name="shopping"),
    path("shopping/<int:recipe_id>", views.delete_shopping_list, name="delete_shopping"),
    path("print/", views.get_txt, name="print"),
    # path("group/<str:slug>", views.group_posts, name="group"),
    # path("new", views.new_post, name="new_post"),
    # path("follow/", views.follow_index, name="follow_index"),
    # path("<str:username>/", views.profile, name="profile"),
    # path("<str:username>/<int:post_id>/", views.post_view, name="post"),
    # path(
    #     "<str:username>/<int:post_id>/edit/",
    #     views.post_edit,
    #     name="post_edit"
    # ),
    # path("<str:username>/<int:post_id>/comment/", views.add_comment, name="add_comment"),
    # path("<str:username>/follow/", views.profile_follow, name="profile_follow"),
    # path("<str:username>/unfollow/", views.profile_unfollow, name="profile_unfollow"),
]
