from django.db import models

class Profile(models.Model):
    #Primary key
    email = models.EmailField(primary_key=True, null=False, editable=True, default='default@default.fr')

    #Secondary key
    username = models.CharField(null=False, max_length=100, editable=True,
                                default='default')
    first_name = models.CharField(null=True, max_length=100, editable=True)
    last_name = models.CharField(null=True, max_length=100, editable=True)
    profile_picture = models.ImageField(upload_to='profile/',
                                        default="profile/default.png",
                                        editable=True, null=True)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ SURCHARGE ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    def __str__(self):
        return f'Email: {self.email}\nUsername: {self.username}'

    def save(self, *args, **kwargs):
        if self.email is None or self.username is None:
            raise ValueError("Email or username can't be empty")

        from shared.models import Clients
        client = Clients.get_client_by_email(self.email)

        if client is None:  # When i want to create profile
            return super().save(*args, **kwargs)

        super().save(*args, **kwargs)  #When I want to edit profile

    def delete(self, *args, **kargs):
        super().delete(*args, **kargs)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ FUNCTIONS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    @staticmethod
    def get_profile_by_email(email):
        try:
            return Profile.objects.filter(email=email).first()
        except Profile.DoesNotExist:
            return None

