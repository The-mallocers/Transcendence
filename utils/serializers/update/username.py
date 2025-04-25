from django.core.validators import MinLengthValidator, \
    MaxLengthValidator, RegexValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from apps.profile.models import Profile

class UsernameSerializer(serializers.ModelSerializer):
    username = serializers.CharField(validators=[
        MinLengthValidator(3),
        MaxLengthValidator(50),
        RegexValidator(
            regex=r'^[a-zA-ZáàäâéèêëíìîïóòôöúùûüçñÁÀÄÂÉÈÊËÍÌÎÏÓÒÔÖÚÙÛÜÇÑ0-9_-]+$',
            message="Username can only contain letters, numbers, and underscores."
        ),
        UniqueValidator(
            queryset=Profile.objects.all(),
            message="This username is already taken."
        )
    ], required=True)
    
    class Meta:
        model = Profile
        fields = ['username']