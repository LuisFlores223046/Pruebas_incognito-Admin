"""Formularios para el módulo de autenticación."""
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Usuario


class LoginForm(AuthenticationForm):
    """Formulario de inicio de sesión."""

    username = forms.CharField(
        label='Usuario',
        widget=forms.TextInput(attrs={
            'class': 'input-campo',
            'placeholder': 'Nombre de usuario',
            'autofocus': True,
        }),
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'input-campo',
            'placeholder': 'Contraseña',
        }),
    )


class UsuarioForm(forms.ModelForm):
    """Formulario para crear un nuevo usuario."""

    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'input-campo'}),
        help_text='Mínimo 8 caracteres.',
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={'class': 'input-campo'}),
    )

    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'rol']
        widgets = {
            'username': forms.TextInput(
                attrs={'class': 'input-campo'}
            ),
            'first_name': forms.TextInput(
                attrs={'class': 'input-campo'}
            ),
            'last_name': forms.TextInput(
                attrs={'class': 'input-campo'}
            ),
            'email': forms.EmailInput(
                attrs={'class': 'input-campo'}
            ),
            'rol': forms.Select(
                attrs={'class': 'input-campo'}
            ),
        }
        labels = {
            'username': 'Nombre de usuario',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo electrónico',
            'rol': 'Rol',
        }

    def clean_password2(self):
        """Valida que las contraseñas coincidan."""
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError(
                'Las contraseñas no coinciden.'
            )
        return p2

    def save(self, commit=True):
        """Guarda el usuario con la contraseña hasheada (RN-009)."""
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data['password1'])
        if commit:
            usuario.save()
        return usuario


class EditarRolForm(forms.ModelForm):
    """Formulario para cambiar el rol de un usuario."""

    class Meta:
        model = Usuario
        fields = ['rol']
        widgets = {
            'rol': forms.Select(attrs={'class': 'input-campo'}),
        }
        labels = {'rol': 'Rol'}
