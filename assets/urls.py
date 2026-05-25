from django.urls import path

from . import views

app_name = "assets"

urlpatterns = [
    path("", views.index, name="landing"),
    path("asset/<int:asset_id>/", views.asset_detail, name="asset_detail"),
    path("list/", views.asset_list, name="asset_list"),
    path("users/", views.user_list, name="user_list"),
    path('register/', views.register_view, name='register'),
   path("users/<int:user_id>/edit/", views.user_edit, name="user_edit"), 
   
]
