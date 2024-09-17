from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin site
    path('blog/', include('blog.urls')),  # Blog app URL patterns
    path('recipes/', include('blog.urls')),  # Recipes app (if in the same blog app)
    
    # Redirect the root URL to the blog post list view
    path('', lambda request: redirect('blog:post_list')),  
]