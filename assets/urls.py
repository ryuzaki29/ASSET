from django.urls import path

from . import views

app_name = "assets"

urlpatterns = [
    path("", views.index, name="landing"),
    path("asset/<int:asset_id>/", views.asset_detail, name="asset_detail"),
    path("asset/<int:asset_id>/edit/", views.asset_edit, name="asset_edit"),
    path("create/", views.asset_create, name="asset_create"),
    path("list/", views.asset_list, name="asset_list"),
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:user_id>/', views.user_profile, name='user_profile'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    path("users/register/", views.register_view, name="user_registration"),
]
