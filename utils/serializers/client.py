from django.db import transaction
from rest_framework import serializers

from apps.admin.models import Rights
from apps.notifications.models import Friend
from apps.auth.models import Password, TwoFA
from apps.client.models import Clients, Stats
from apps.profile.models import Profile
from utils.serializers.auth import PasswordSerializer
from utils.serializers.profile import ProfileSerializer


class ClientSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(many=False)
    password = PasswordSerializer(many=False)

    class Meta:
        model = Clients
        fields = ['profile', 'password', 'passwordcheck']
        
    def validate(self, data):
        password = data['password']['password']
        passwordcheck = data['password']['passwordcheck']
        
        if password != passwordcheck:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        password_data = validated_data.pop('password')

        try:
            with transaction.atomic():
                profile = Profile.objects.create(**profile_data)
                passwrod = Password.objects.create(**password_data)
                two_fa = TwoFA.objects.create()
                right = Rights.objects.create(is_admin=False)
                friend = Friend.objects.create()
                stats = Stats.objects.create()
                client = Clients.objects.create(profile=profile, password=passwrod, twoFa=two_fa, rights=right, friend=friend, stats=stats)

                if validated_data.get('is_admin', False):
                    client.rights.is_admin = True
                    client.rights.save()

        except Exception as e:
            raise serializers.ValidationError(f"Error creating client: {str(e)}")

        return client
