from django.utils.translation import gettext_lazy as _
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm, _unicode_ci_compare
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django_select2 import forms as s2forms
from django.utils.text import capfirst

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

class PlayerProfileEditForm(forms.ModelForm):
  email = forms.EmailField(required=True)
  
  def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      self.helper = FormHelper()
      self.helper.add_input(NonPrimarySubmit("submit", _("Save"), css_class="btn-outline-secondary"))

  class Meta:
      model = get_user_model()
      fields = ('username', 'email', 'discord_name',
                'in_game_name', 'in_game_id')

class PlayerLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        UserModel = get_user_model()
        self.email_field = UserModel._meta.get_field(UserModel.EMAIL_FIELD)
        self.fields["username"].label = capfirst(self.username_field.verbose_name) + \
                                        _(" or ") + \
                                        capfirst(self.email_field.verbose_name)
        self.helper = FormHelper()
        self.helper.add_input(NonPrimarySubmit("submit", _("Log in"), css_class="btn-outline-secondary"))

class PlayerPasswordChangeForm(PasswordChangeForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(NonPrimarySubmit("submit", _("Save"), css_class="btn-outline-secondary"))

class PlayerPasswordResetForm(PasswordResetForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(NonPrimarySubmit("submit", _("Send confirmation"), css_class="btn-outline-secondary"))

    def get_users(self, email):
        """Given an email, return matching user(s) who should receive a reset.

        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.

        Reimplemented to allow unusable passwords to be reset.
        """
        UserModel = get_user_model()
        email_field_name = UserModel.get_email_field_name()
        active_users = UserModel._default_manager.filter(
            **{
                "%s__iexact" % email_field_name: email,
                "is_active": True,
            }
        )
        return (
            u
            for u in active_users
            if _unicode_ci_compare(email, getattr(u, email_field_name))
        )

class PlayerPasswordResetConfirmForm(SetPasswordForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(NonPrimarySubmit("submit", _("Save"), css_class="btn-outline-secondary"))
    