"""
Archivo: forms.py
Descripción: Formularios para el módulo de autenticación del sistema RYV Rentas.
             Define los formularios de inicio de sesión, creación y edición
             de usuarios, según lo definido en RF-01, RF-28 y RF-26 del SRS.
Fecha: 2026-04-07
Versión: 1.0
"""
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Usuario


class LoginForm(AuthenticationForm):
    """
    Formulario de inicio de sesión para usuarios del sistema.

    Extiende AuthenticationForm de Django agregando estilos
    personalizados a los campos de usuario y contraseña.

    Attributes:
        username (CharField): Campo de texto para el nombre de usuario.
        password (CharField): Campo de contraseña oculta.
    """

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
    """
    Formulario para registrar un nuevo usuario en el sistema.

    Incluye validación de coincidencia de contraseñas y almacenamiento
    seguro mediante hashing, cumpliendo con RN-009 y RF-28 del SRS.

    Attributes:
        password1 (CharField): Campo para ingresar la contraseña.
        password2 (CharField): Campo para confirmar la contraseña.
    """

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
        """
        Valida que las dos contraseñas ingresadas sean idénticas.

        Retorna:
            str: El valor de password2 si las contraseñas coinciden.

        Lanza:
            ValidationError: Si password1 y password2 no coinciden.
        """
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError(
                'Las contraseñas no coinciden.'
            )
        return p2

    def save(self, commit=True):
        """
        Guarda el usuario con la contraseña almacenada de forma segura.

        Utiliza set_password() de Django para hashear la contraseña
        antes de guardarla, cumpliendo con RN-009 del SRS.

        Parámetros:
            commit (bool): Si es True, guarda el usuario en la base de datos
            inmediatamente. Por defecto es True.

        Retorna:
            Usuario: La instancia del usuario creado con la contraseña hasheada.
        """
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data['password1'])
        if commit:
            usuario.save()
        return usuario


class EditarRolForm(forms.ModelForm):
    """
    Formulario para editar el rol asignado a un usuario existente.

    Permite al Administrador cambiar el rol de cualquier usuario
    registrado en el sistema, según lo definido en RF-26 del SRS.
    """

    class Meta:
        model = Usuario
        fields = ['rol']
        widgets = {
            'rol': forms.Select(attrs={'class': 'input-campo'}),
        }
        labels = {'rol': 'Rol'}
