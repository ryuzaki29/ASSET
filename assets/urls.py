from django.urls import path

from . import views

app_name = "assets"

urlpatterns = [
    path("", views.IndexView.as_view(), name="landing"),
    path("asset/<int:asset_id>/", views.asset_detail, name="asset_detail"),
    path("asset/<int:asset_id>/edit/", views.asset_edit, name="asset_edit"),
    path("asset/<int:asset_id>/delete/", views.asset_delete, name="asset_delete"),
    path("asset/<int:asset_id>/add-stock/", views.asset_add_stock, name="asset_add_stock"),
    path("asset/<int:asset_id>/logs/", views.asset_logs_json, name="asset_logs_json"),
    path("create/", views.asset_create, name="asset_create"),
    path("list/", views.asset_list, name="asset_list"),
    path("requests/create/", views.request_create, name="request_create"),
    path("requests/", views.request_list, name="request_list"),
    path("requests/<int:request_id>/approve/", views.request_approve, name="request_approve"),
    path("requests/<int:request_id>/decline/", views.request_decline, name="request_decline"),
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:user_id>/', views.user_profile, name='user_profile'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    path("users/register/", views.register_view, name="user_registration"),
    path("placeholder/", views.placeholder_view, name="placeholder"),
]
