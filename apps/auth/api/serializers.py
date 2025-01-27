from rest_framework import serializers
from apps.auth.models import Password


class PasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Password
        fields = ['id', 'password']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    def validate_password(self, value):
        if not value or value.strip() == '':
            raise serializers.ValidationError("Password cannot be empty")
        return value