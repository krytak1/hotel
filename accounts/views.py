from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView

from .forms import CustomLoginForm

class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'registration/login.html'

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('accounts:login')
