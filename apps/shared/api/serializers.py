from rest_framework import serializers

from apps.admin.models import Rights
from apps.auth.api.serializers import PasswordSerializer
from apps.auth.models import Password, TwoFA
from apps.profile.api.serializers import ProfileSerializer
from apps.profile.models import Profile
from apps.shared.models import Clients


class ClientSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(many=False)
    password = PasswordSerializer(many=False)

    class Meta:
        model = Clients
        fields = ['profile', 'password']

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        password_data = validated_data.pop('password')

        try:
            profile =  Profile.objects.create(**profile_data)
            passwrod = Password.objects.create(**password_data)
            two_fa = TwoFA.objects.create()
            right = Rights.objects.create()
            client = Clients.objects.create(profile=profile, password=passwrod, twoFa=two_fa, rights=right)
        except Exception as e:
            raise serializers.ValidationError(f"Error creating client: {str(e)}")

        return client

