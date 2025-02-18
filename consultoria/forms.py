# consultoria/forms.py

from django import forms
from django.forms import DateTimeInput
from .models import Consultor
from .models import Client
from django.contrib.auth.forms import UserCreationForm
from consultoria.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.db import models


class ReservaForm(forms.Form):
    nome = forms.CharField(max_length=100, label="Nome")
    email = forms.EmailField(label="E-mail")
    consultor = forms.CharField(max_length=100, label="Consultor")
    data_hora = forms.DateTimeField(
        widget=DateTimeInput(attrs={'type': 'datetime-local'}),
        label="Data e Hora"
    )

class ConsultorForm(forms.ModelForm):
    class Meta:
        model =  Consultor
        fields = ['nome', 'categoria', 'especialidade', 'preco_hora', 'disponibilidade']

class ClientForm(forms.ModelForm):
    CATEGORIA_CHOICES = [
        ('IT', 'IT'),
        ('Ciências Sociais', 'Ciências Sociais'),
        ('Ciências Exatas', 'Ciências Exatas'),
        ('Todas','Todas')
    ]
    class Meta:
        model = Client
        fields = ['primeiro_nome', 'ultimo_nome', 'categoria', 'especialidade', 'email', 'telemovel', 'Morada', 'Online', 'Descricao']
        widgets = {
            'Descricao': forms.Textarea(attrs={'rows': 5, 'cols': 40, 'placeholder': 'Descreva seu pedido aqui...'}),
        }

    primeiro_nome = forms.CharField(widget=forms.HiddenInput(), required=False)
    ultimo_nome = forms.CharField(widget=forms.HiddenInput(), required=False)
    email = forms.EmailField(widget=forms.HiddenInput(), required=False)

    # Tornar os campos obrigatórios sem mudar a estrutura
    categoria = forms.ChoiceField(choices=Client.CATEGORIAS, initial='IT')
    especialidade = forms.CharField(required=True)
    telemovel = forms.CharField(required=True)
    Morada = forms.ChoiceField(choices=Client.DISTRITOS, required=True)  # Usando a var
    Descricao = forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'cols': 40}), required=True)

    def clean_email(self):
        """ Ignorar a verificação de unicidade do email na BD """
        return self.cleaned_data.get('email')

class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150,required=True)
    password = forms.CharField(widget=forms.PasswordInput,required=True)


class UserForm(UserCreationForm):
    email = forms.EmailField(label="E-mail")
    first_name = forms.CharField(max_length=150, label="Primeiro Nome")
    last_name = forms.CharField(max_length=150, label="Último Nome")

    class Meta:
        model = User  # Usa o modelo customizado
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')

        # Verifica se já existe um usuário com o mesmo e-mail
        if User.objects.filter(email=email).exists():
            raise ValidationError('Este e-mail já está registrado. Por favor, use outro e-mail.')

        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user