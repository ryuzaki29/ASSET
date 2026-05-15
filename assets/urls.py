from django.urls import path

from . import views

app_name = "assets"

urlpatterns = [
    path("", views.index, name="index"),
    path("asset/<int:asset_id>/", views.asset_detail, name="asset_detail"),
    path("list/", views.asset_list, name="asset_list"),
    path("users/", views.user_list, name="user_list"),
]
