
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

class PlayerRegisterForm(UserCreationForm):
  email = forms.EmailField(required=True)

  class Meta:
      model = get_user_model()
      fields = ('username', 'email', 'discord_name',
                'in_game_name', 'in_game_id',
                'first_name', 'last_name')