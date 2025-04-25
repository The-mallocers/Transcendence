from django.core.validators import EmailValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from apps.profile.models import Profile


class EmailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[
        EmailValidator(),
        UniqueValidator(
            queryset=Profile.objects.all(),
            message="Email already registered."
        )
    ], required=True)
    
    
    class Meta:
        model = Profile
        fields = ['email']