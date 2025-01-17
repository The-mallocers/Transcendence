from django.db import models

from Transcendence.settings import USERNAME_LENGHT, FIRSTNAME_LENGHT, \
    LASTNAME_LENGHT
from django.db import models

from Transcendence.settings import USERNAME_LENGHT, FIRSTNAME_LENGHT, \
    LASTNAME_LENGHT


class Profile(models.Model):
    #Primary key
    email = models.EmailField(primary_key=True, null=False, editable=True, default='default@default.fr')

    #Secondary key
    username = models.CharField(null=False, max_length=USERNAME_LENGHT, editable=True, default='default')
    first_name = models.CharField(null=True, max_length=FIRSTNAME_LENGHT, editable=True)
    last_name = models.CharField(null=True, max_length=LASTNAME_LENGHT, editable=True)
    profile_picture = models.ImageField(upload_to='profile_picture/', editable=True, null=True)

    #Functions
    @staticmethod
    def get_profile(email) -> email:
        if email is None:
            return None
        profile = Profile.objects.filter(email=email).first()
        if profile is None:
            return None
        return profile

    def update(self, data, value):
        match data:
            case "username":
                self.username = value
            case "first_name":
                self.first_name = value
            case "last_name":
                self.last_name = value
            case "email":
                self.email = value
            case "profile_picture":
                self.profile_picture = value
            case _:
                return None
        self.save()

