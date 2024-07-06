from django.views.generic.edit import CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from . import forms

# Create your views here.

class PlayerSignUpView(SuccessMessageMixin, CreateView):
  template_name = 'authentification/register.html'
  success_url = reverse_lazy('auth:login')
  form_class = forms.PlayerRegisterForm
  success_message = "Your player account was successfully created. \
                     You are now logged in!"