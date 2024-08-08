from django.utils.translation import gettext_lazy as _
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class PlayerRegisterForm(UserCreationForm):
  email = forms.EmailField(required=True)
  
  def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      self.helper = FormHelper()
      self.helper.add_input(Submit("submit", _("Sign up"), css_class="btn btn-outline-secondary"))

  class Meta:
      model = get_user_model()
      fields = ('username', 'email', 'discord_name',
                'in_game_name', 'in_game_id')

class PlayerLoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", _("Log in"), css_class="btn btn-outline-secondary"))

class PlayerPasswordChangeForm(PasswordChangeForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", _("Save"), css_class="btn btn-outline-secondary"))
    