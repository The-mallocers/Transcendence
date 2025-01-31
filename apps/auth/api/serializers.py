import bcrypt
from django.core.validators import MinLengthValidator, RegexValidator
from rest_framework import serializers

from apps.auth.models import Password


class PasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(validators=[
        MinLengthValidator(
            limit_value=4,
            message="Password must be at least 4 charcaters"
        ),
        RegexValidator(
            regex=r'^(?=.*[!@#$%^&*()_+\-=\[\]{};:\'",<>\./?\\|`~]).*(?=.*\d).+$',
            message="Password must contain at least one special character and one number."
        )
    ])

    old_password = serializers.CharField(required=False, allow_blank=False)

    class Meta:
        model = Password
        fields = ['id', 'password', 'old_password']
        write_only_fields = ['password', 'old_password']

    def validate_password(self, value):
        instance = self.instance
        if instance and not instance.check_pwd(value):
            raise serializers.ValidationError("New password must be different from the old password.")
        return value

    #Object level validation (validate password field)
    def validate(self, attrs):
        self.validate_password(attrs.get('password'))
        return attrs

    #Update custom object function
    def update(self, instance, validated_data):
        new_password = validated_data.get('password', instance.password)
        old_password = instance.password

        if not new_password.startswith('$2b$'):
            salt = bcrypt.gensalt(prefix=b'2b')
            new_password = bcrypt.hashpw(new_password.encode('utf-8'), salt).decode('utf-8')

        instance.old_password = old_password
        instance.password = new_password

        instance.save()
        return instance