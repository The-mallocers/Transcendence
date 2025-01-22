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

    def __str__(self):
        return f'Email: {self.email}\nUsername: {self.username}'

    def save(self, *args, **kwargs):
        from shared.models import Clients

        if self.email is None or self.username is None:
            raise ValueError("Email or username can't be empty")

        client = Clients.get_client_by_email(self.email)

        if client is None:
            return super().save(*args, **kwargs)
        # if not client.rights.has_permission('edit_profile'):
        #     raise PermissionDenied('You do not have permission to edit profile')

        super().save(*args, **kwargs)

    #Functions
    @staticmethod
    def get_profile(email):
        try:
            return Profile.objects.filter(email=email).first()
        except Profile.DoesNotExist:
            return None

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

