from django.db import transaction
from rest_framework import serializers

from apps.admin.models import Rights
from apps.auth.models import Password, TwoFA
from apps.client.models import Clients, Stats
from apps.notifications.models import Friend
from apps.profile.models import Profile
from utils.serializers.auth import PasswordSerializer
from utils.serializers.profile import ProfileSerializer


class ClientSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(many=False)
    password = PasswordSerializer(many=False)

    class Meta:
        model = Clients
        fields = ['profile', 'password']

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        password_data = validated_data.pop('password')
        is_admin = self.context.get('is_admin')

        # Removing passwordcheck since its not longer useful
        if 'passwordcheck' in password_data:
            password_data.pop('passwordcheck')

        try:
            with transaction.atomic():
                profile = Profile.objects.create(**profile_data)
                password = Password.objects.create(**password_data)
                two_fa = TwoFA.objects.create()
                right = Rights.objects.create(is_admin=bool(is_admin))
                friend = Friend.objects.create()
                stats = Stats.objects.create()
                client = Clients.objects.create(profile=profile, password=password, twoFa=two_fa, rights=right, friend=friend, stats=stats)

        except Exception as e:
            raise serializers.ValidationError(f"Error creating client: {str(e)}")

        return client
