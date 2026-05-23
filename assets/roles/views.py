from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django import forms
from .models import Role

# List all Roles
class RoleForm(forms.ModelForm):
    name = forms.CharField(max_length=20)

    class Meta:
        model = Role
        fields = ['name', 'description']
        
class RoleListView(ListView):
    model = Role
    template_name = 'roles/role_list.html'
    context_object_name = 'roles'

# Create a Role
class RoleCreateView(CreateView):
    model = Role
    form_class = RoleForm
    template_name = 'roles/role_form.html'
    success_url = reverse_lazy('roles:role_list')

# Update a Role
class RoleUpdateView(UpdateView):
    model = Role
    form_class = RoleForm
    template_name = 'roles/role_form.html'
    success_url = reverse_lazy('roles:role_list')  

# Delete a Role
class RoleDeleteView(DeleteView):
    model = Role
    template_name = 'roles/role_delete.html'  
    success_url = reverse_lazy('roles:role_list')

# Detail a Role
class RoleDetailView(DetailView):
    model = Role
    template_name = 'roles/role_detail.html'
    context_object_name = 'role'