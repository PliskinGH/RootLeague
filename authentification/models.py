from django.db import models

from django.contrib.auth.models import AbstractUser

# Create your models here.

class Player(AbstractUser):
    """
    Model for players registered in the league database.
    """
    ig_name = models.CharField(max_length=200)
    ig_id = models.IntegerField(blank=True, null=True)
    
    def __str__(self):
        result = ""
        if (self.ig_name not in [None, ""]):
            result = self.ig_name
            if (self.ig_id is not None):
                result = result + "#" + str(self.ig_id)
        if (result == ""):
            result = super().__str__()
        return result