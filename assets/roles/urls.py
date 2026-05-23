from django.urls import path
from . import views

app_name = 'roles'

urlpatterns = [
    path('', views.RoleListView.as_view(), name='role_list'),
    path('add/', views.RoleCreateView.as_view(), name='role_create'),        # ✅ moved up
    path('<int:pk>/', views.RoleDetailView.as_view(), name='role_detail'),
    path('<int:pk>/edit/', views.RoleUpdateView.as_view(), name='role_update'),
    path('<int:pk>/delete/', views.RoleDeleteView.as_view(), name='role_delete'),
]