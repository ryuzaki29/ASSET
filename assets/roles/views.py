from django.contrib.auth.models import Group, Permission
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from assets.utils.permissions import is_admin_user
from .forms import GroupForm

# ROLE LIST
class RoleListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = "auth.view_group"
    model = Group
    template_name = "roles/role_list.html"
    context_object_name = "groups"

# ROLE DETAIL
class RoleDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = "auth.view_group"
    model = Group
    template_name = "roles/role_detail.html"
    context_object_name = "role"

# ROLE CREATE
class RoleCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = "auth.add_group" 
    model = Group
    form_class = GroupForm
    template_name = "roles/role_form.html"
    success_url = reverse_lazy("roles:role_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.permissions.set(form.cleaned_data.get("permissions", []))
        return response

# ROLE UPDATE
class RoleUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = "auth.change_group"
    model = Group
    form_class = GroupForm
    template_name = "roles/role_form.html"
    success_url = reverse_lazy("roles:role_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.object
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.permissions.set(form.cleaned_data.get("permissions", []))
        return response

# ROLE DELETE
class RoleDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = "auth.delete_group"
    model = Group
    template_name = "roles/role_delete.html"
    success_url = reverse_lazy("roles:role_list")
