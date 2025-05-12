from django.db import models


class Profile(models.Model):
    # Primary key
    email = models.EmailField(primary_key=True, null=False, editable=True)

    # Secondary key
    username = models.CharField(null=False, max_length=50, editable=True)
    first_name = models.CharField(null=True, max_length=50, editable=True)
    last_name = models.CharField(null=True, max_length=50, editable=True)

    profile_picture = models.ImageField(upload_to='profile/',
                                        default="profile/default.png",
                                        editable=True, null=True)
    # I want to add this !
    coalition = models.CharField(null=True, max_length=50, editable=True)

    class Meta:
        db_table = "client_profile"

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ SURCHARGE ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    def __str__(self):
        return f'Email: {self.email}\nUsername: {self.username}'

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ FUNCTIONS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    @staticmethod
    def get_profile_by_email(email):
        try:
            return Profile.objects.filter(email=email).first()
        except Profile.DoesNotExist:
            return None
