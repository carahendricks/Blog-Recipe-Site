from django.urls import path
from . import views
from .feeds import LatestPostsFeed

app_name = 'blog'

urlpatterns = [
    # Blog Post Views
    path('', views.post_list, name='post_list'),  # Main blog list
    path('tag/<slug:tag_slug>/', views.post_list_by_tag, name='post_list_by_tag'),  # Filter blog posts by tag
    path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.post_detail, name='post_detail'),  # Blog post detail
    path('<int:post_id>/share/', views.post_share, name='post_share'),  # Share a blog post
    path('<int:post_id>/comment/', views.post_comment, name='post_comment'),  # Comment on a blog post
    path('feed/', LatestPostsFeed(), name='post_feed'),  # RSS feed for blog posts
    path('search/', views.post_search, name='post_search'),  # Search blog posts

    # Recipe Views
    path('recipes/', views.recipe_list, name='recipe_list'),  # Main recipe list
    path('recipes/tag/<slug:tag_slug>/', views.recipe_list_by_tag, name='recipe_list_by_tag'),  # Filter recipes by tag
    path('recipes/cuisine/<slug:tag_slug>/', views.recipe_list_by_cuisine, name='recipe_list_by_cuisine'),  # Filter recipes by cuisine
    path('recipes/<slug:slug>/', views.recipe_detail, name='recipe_detail'),  # Recipe detail view
    path('recipes/<int:recipe_id>/share/', views.recipe_share, name='recipe_share'),  # Share a recipe via email
]