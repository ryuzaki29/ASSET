from django import forms
from .models import Role


class RoleForm(forms.ModelForm):

    class Meta:
        model = Role
        fields = ['name', 'code', 'description']

        labels = {
            'name': 'Role Name',
            'code': 'Role Code',
            'description': 'Description',
        }

        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }

    def clean_code(self):
        return self.cleaned_data['code'].strip().upper()