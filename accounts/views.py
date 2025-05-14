from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView
from django.contrib.auth.views import LoginView, LogoutView

from .forms import SignUpForm, CustomLoginForm
from .models import Profile

class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        user = form.save()
        avatar = self.request.FILES.get('avatar')
        if avatar:
            user.profile.avatar = avatar
            user.profile.save()
        login(self.request, user)
        return redirect(self.success_url)

class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'registration/login.html'

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('accounts:login')
