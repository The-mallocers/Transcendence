import uuid

from django.db import models

# # Create your models here.
class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
    session_user = models.UUIDField(default=uuid.uuid4())
    is_admin = models.BooleanField(default=False)

    # User elements
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=50)
    nickname = models.CharField(max_length=20)
    email = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    avatar = models.TextField(default="/img/img.png")

    # User information
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    @staticmethod
    def get_user(req):
        user_id = req.session.get('user_id')
        if user_id is None:
            return None
        user = User.objects.get(id=user_id)
        return user

    def update(self, data, value):
        match data:
            case "first_name":
                self.first_name = value
            case "last_name":
                self.last_name = value
            case "nickname":
                self.nickname = value
            case "email":
                self.email = value
            case "password":
                self.password = value
            case "avatar":
                self.avatar = value
            case _:
                return None
        self.update_at = models.DateTimeField(auto_now=True)
        self.save()

    def __str__(self):
        return f"ID: {self.id}, Fisrtname: {self.first_name}, email: {self.email}, is admin: {self.is_admin}"