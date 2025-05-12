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
    passwordcheck = serializers.CharField(write_only=True)

    class Meta:
        model = Password
        fields = ['id', 'password', 'old_password', 'passwordcheck']
        write_only_fields = ['password', 'old_password']

    def validate_password(self, value):
        instance = self.instance
        if instance and not instance.check_pwd(value):
            print("Hello sir")
            raise serializers.ValidationError("New password must be different from the old password.")
        return value

    # Object level validation (validate password field)
    def validate(self, data):
        self.validate_password(data.get('password'))
        password = data.get('password', None)
        passwordcheck = data.get('passwordcheck', None)
        if password != passwordcheck:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def update(self, instance, validated_data):
        new_password = validated_data.get('password')

        # Check if the new password matches the old one using the check_pwd method
        if instance.check_pwd(new_password):
            raise serializers.ValidationError("New password must be different from the old password.")

        # Store the old password before updating
        old_password = instance.password
        instance.old_password = old_password

        # Hash the new password if it's not already hashed
        if not new_password.startswith('$2b$'):
            salt = bcrypt.gensalt(prefix=b'2b')
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt).decode('utf-8')
            instance.password = hashed_password
        else:
            instance.password = new_password
        
        instance.save()
        return instance
