from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django import forms
from .models import Role
from .forms import RoleForm

class RoleListView(ListView):
    model = Role
    template_name = 'roles/role_list.html'
    context_object_name = 'roles'

class RoleCreateView(CreateView):
    model = Role
    form_class = RoleForm
    template_name = 'roles/role_form.html'
    success_url = reverse_lazy('roles:role_list')


class RoleUpdateView(UpdateView):
    model = Role
    form_class = RoleForm
    template_name = 'roles/role_form.html'
    success_url = reverse_lazy('roles:role_list')


class RoleDeleteView(DeleteView):
    model = Role
    template_name = 'roles/role_delete.html'
    success_url = reverse_lazy('roles:role_list')


class RoleDetailView(DetailView):
    model = Role
    template_name = 'roles/role_detail.html'
    context_object_name = 'role'