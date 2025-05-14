import bcrypt
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

                if validated_data.get('is_admin', False):
                    client.rights.is_admin = True
                    client.rights.save()

        except Exception as e:
            raise serializers.ValidationError(f"Error creating client: {str(e)}")

        return client

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        password_data = validated_data.pop('password', {})
        print("In update method of client")
        print(profile_data)
        print(password_data)
        print("instance:", instance)
        # Update profile fields
        if profile_data:
            for attr, value in profile_data.items():
                setattr(instance.profile, attr, value)
            instance.profile.save()
        # Update password fields
        if password_data:
            # # Optional: remove passwordcheck
            password_data.pop('passwordcheck', None)
            if bcrypt.checkpw(password_data['password'].encode('utf-8'), instance.password.password.encode('utf-8')):
                raise serializers.ValidationError("New password must be different from the old password.")
            for attr, value in password_data.items():
                setattr(instance.password, attr, value)
            instance.password.save()
            # password_serializer = PasswordSerializer(instance=instance.password, data=password_data, partial=True)
            # password_serializer.is_valid(raise_exception=True)
            # password_serializer.save()
        print(instance)
        instance.save()
        return instance
