from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django import forms
from .models import Role


class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['name', 'code', 'description']

class RoleListView(ListView):
    model = Role
    template_name = 'roles/role_list.html'
    context_object_name = 'roles'

    def get_queryset(self):
        if not Role.objects.exists():
            for code, name in Role.ROLE_CHOICES:
                Role.objects.create(code=code, name=name)
        return Role.objects.all()

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