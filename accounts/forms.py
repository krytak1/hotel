from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    username = forms.CharField(
        label='Имя пользователя',
        widget=forms.TextInput(attrs={
            'class': 'border rounded p-2 w-full',
            'placeholder': 'Имя пользователя'
        })
    )
    email = forms.EmailField(
        label='Электронная почта',
        widget=forms.EmailInput(attrs={
            'class': 'border rounded p-2 w-full',
            'placeholder': 'example@mail.ru'
        })
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'border rounded p-2 w-full',
            'placeholder': 'Пароль'
        })
    )
    password2 = forms.CharField(
        label='Повтор пароля',
        widget=forms.PasswordInput(attrs={
            'class': 'border rounded p-2 w-full',
            'placeholder': 'Повторите пароль'
        })
    )
    avatar = forms.ImageField(
        label='Аватар',
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'border rounded p-2 w-full'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'avatar']

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Это имя пользователя уже занято.")
        return username

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'border rounded p-2 w-full',
            'placeholder': 'Имя пользователя'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'border rounded p-2 w-full',
            'placeholder': 'Пароль'
        })
    )
