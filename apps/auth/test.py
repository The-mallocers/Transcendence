import uuid
from datetime import timedelta

import pyotp
from django.test import TestCase
from django.utils import timezone

from apps.auth.models import Password, TwoFA, InvalidatedToken
from utils.enums import JWTType


class PasswordModelTest(TestCase):
    """Test the Password model"""

    def setUp(self):
        """Set up test data"""
        self.password = Password.objects.create(
            password="testpassword123"
        )

    def test_password_creation(self):
        """Test that a password is created and hashed"""
        # Get the password from the database
        password = Password.objects.get(id=self.password.id)

        # Check that the password is hashed (starts with bcrypt prefix)
        self.assertTrue(password.password.startswith('$2b$'))

        # Check that the original password is not stored
        self.assertNotEqual(password.password, "testpassword123")

    def test_check_pwd(self):
        """Test password verification"""
        # Get the password from the database
        password = Password.objects.get(id=self.password.id)

        # Check that the correct password verifies
        self.assertTrue(password.check_pwd("testpassword123"))

        # Check that an incorrect password fails
        self.assertFalse(password.check_pwd("wrongpassword"))


class TwoFAModelTest(TestCase):
    """Test the TwoFA model"""

    def setUp(self):
        """Set up test data"""
        self.twofa = TwoFA.objects.create()

    def test_twofa_creation(self):
        """Test that a TwoFA instance is created with default values"""
        twofa = TwoFA.objects.get(key=self.twofa.key)

        # Check default values
        self.assertFalse(twofa.enable)
        self.assertFalse(twofa.scanned)
        # self.assertIsNone(twofa.qrcode)

        # Check that a key was generated
        self.assertIsNotNone(twofa.key)
        self.assertEqual(len(twofa.key), 32)  # Base32 key length

    def test_update_method(self):
        """Test the update method for TwoFA"""
        twofa = TwoFA.objects.get(key=self.twofa.key)

        # Update enable status
        twofa.update("enable", True)
        self.assertTrue(twofa.enable)

        # Update scanned status
        twofa.update("scanned", True)
        self.assertTrue(twofa.scanned)

        # Update key
        new_key = pyotp.random_base32()
        twofa.update("key", new_key)
        self.assertEqual(twofa.key, new_key)

        # Update with invalid field (should do nothing)
        twofa.update("invalid_field", "value")
        # No assertion needed, just checking it doesn't raise an error


class InvalidatedTokenModelTest(TestCase):
    """Test the InvalidatedToken model"""

    def setUp(self):
        """Set up test data"""
        # Create a token that expires in the future
        future_time = timezone.now() + timedelta(hours=1)
        self.token = InvalidatedToken.objects.create(
            jti=uuid.uuid4(),
            token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U",
            exp=future_time,
            type=JWTType.ACCESS.name
        )

        # Create a token that has already expired
        past_time = timezone.now() - timedelta(hours=1)
        self.expired_token = InvalidatedToken.objects.create(
            jti=uuid.uuid4(),
            token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJleHBpcmVkIn0.9oSFH97qLCKKbo3pAHj1THYnuR1PV-Ta8g33-XhVWoU",
            exp=past_time,
            type=JWTType.REFRESH.name
        )

    def test_token_creation(self):
        """Test that tokens are created correctly"""
        # Check the active token
        token = InvalidatedToken.objects.get(jti=self.token.jti)
        self.assertEqual(token.type, JWTType.ACCESS.name)
        self.assertEqual(token.token, self.token.token)
        expired = InvalidatedToken.objects.get(jti=self.expired_token.jti)
        self.assertEqual(expired.type, JWTType.REFRESH.name)

    def test_delete_expired_token(self):
        """Test the delete_expired_token class method"""
        # Count tokens before deletion
        before_count = InvalidatedToken.objects.count()
        self.assertEqual(before_count, 2)

        # Delete expired tokens
        deleted = InvalidatedToken.delete_expired_token()
        self.assertEqual(deleted, 1)  # One token should be deleted

        # Count tokens after deletion
        after_count = InvalidatedToken.objects.count()
        self.assertEqual(after_count, 1)

        # Check that only the expired token was deleted
        with self.assertRaises(InvalidatedToken.DoesNotExist):
            InvalidatedToken.objects.get(jti=self.expired_token.jti)

        # Check that the active token still exists
        token = InvalidatedToken.objects.get(jti=self.token.jti)
        self.assertEqual(token.type, JWTType.ACCESS.name)
