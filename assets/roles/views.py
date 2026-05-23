from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from .models import Role

# List all Roles
class RoleListView(ListView):
    model = Role
    template_name = 'role_list.html' 
    context_object_name = 'roles'

# Create a Role
class RoleCreateView(CreateView):
    model = Role
    fields = ['name', 'description']
    template_name = 'role_form.html'
    success_url = reverse_lazy('role_list')

# Update a Role
class RoleUpdateView(UpdateView):
    model = Role
    fields = ['name', 'description']
    template_name = 'role_form.html'
    success_url = reverse_lazy('role_list')

# Delete a Role
class RoleDeleteView(DeleteView):
    model = Role
    template_name = 'role_confirm_delete.html'
    success_url = reverse_lazy('role_list')

# Detail view for a Role
class RoleDetailView(DetailView):
    model = Role
    template_name = 'roles/role_detail.html'
    context_object_name = 'role'