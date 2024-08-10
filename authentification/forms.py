from django.utils.translation import gettext_lazy as _
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django_select2 import forms as s2forms

from misc.forms import NonPrimarySubmit

class PlayerRegisterForm(UserCreationForm):
  email = forms.EmailField(required=True)
  
  def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      self.helper = FormHelper()
      self.helper.add_input(NonPrimarySubmit("submit", _("Sign up"), css_class="btn-outline-secondary"))

  class Meta:
      model = get_user_model()
      fields = ('username', 'email', 'discord_name',
                'in_game_name', 'in_game_id')

class PlayerLoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(NonPrimarySubmit("submit", _("Log in"), css_class="btn-outline-secondary"))

class PlayerPasswordChangeForm(PasswordChangeForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(NonPrimarySubmit("submit", _("Save"), css_class="outline"))

class PlayerWidget(s2forms.ModelSelect2Widget):
    model = get_user_model()
    search_fields = ['username__icontains',
                     'in_game_name__icontains',
                     'discord_name__icontains']
    