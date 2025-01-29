from django.core.validators import EmailValidator, MinLengthValidator, \
    MaxLengthValidator, RegexValidator, FileExtensionValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from apps.profile.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[
        EmailValidator(),
        UniqueValidator(
            queryset=Profile.objects.all(),
            message="Email already registered."
        )
    ], required=True)

    username = serializers.CharField(validators=[
        MinLengthValidator(3),
        MaxLengthValidator(50),
        RegexValidator(
            regex=r'^[a-zA-ZáàäâéèêëíìîïóòôöúùûüçñÁÀÄÂÉÈÊËÍÌÎÏÓÒÔÖÚÙÛÜÇÑ0-9_-]+$',
            message="Username can only contain letters, numbers, and underscores."
        )
    ], required=True)

    first_name = serializers.CharField(validators=[
        MaxLengthValidator(50),
        RegexValidator(
            regex=r'^[a-zA-ZáàäâéèêëíìîïóòôöúùûüçñÁÀÄÂÉÈÊËÍÌÎÏÓÒÔÖÚÙÛÜÇÑ]+$',
            message="First name can't contain specials characters."
        )
    ], allow_blank=True, required=False)

    last_name = serializers.CharField(validators=[
        MaxLengthValidator(50),
        RegexValidator(
            regex=r'^[a-zA-ZáàäâéèêëíìîïóòôöúùûüçñÁÀÄÂÉÈÊËÍÌÎÏÓÒÔÖÚÙÛÜÇÑ]+$',
            message="Last name can't contain specials characters."
        )
    ], allow_blank=True, required=False)

    profile_picture = serializers.ImageField(validators=[
        FileExtensionValidator(
            allowed_extensions=['.png', '.jpeg', '.jpg'],
        )
    ], allow_empty_file=True, required=False)

    class Meta:
        model = Profile
        fields = ['username', 'email', 'first_name', 'last_name', 'profile_picture']