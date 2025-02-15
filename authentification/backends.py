from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.validators import validate_email

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        # Test if user used email to login
        try:
            validate_email(username)
            user = UserModel._default_manager.get(email=username)
            username = getattr(user, 'username', username)
        except:
            pass
        return super().authenticate(request, username=username, password=password, **kwargs)

        

