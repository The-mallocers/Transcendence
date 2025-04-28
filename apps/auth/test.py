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
        print("\nRunning test: PasswordModelTest.test_password_creation")
        password = Password.objects.get(id=self.password.id)
        self.assertTrue(password.password.startswith('$2b$'))
        self.assertNotEqual(password.password, "testpassword123")

    def test_check_pwd(self):
        """Test password verification"""
        print("\nRunning test: PasswordModelTest.test_check_pwd")
        password = Password.objects.get(id=self.password.id)
        self.assertTrue(password.check_pwd("testpassword123"))
        self.assertFalse(password.check_pwd("wrongpassword"))


class TwoFAModelTest(TestCase):
    """Test the TwoFA model"""

    def setUp(self):
        """Set up test data"""
        self.twofa = TwoFA.objects.create()

    def test_twofa_creation(self):
        """Test that a TwoFA instance is created with default values"""
        print("\nRunning test: TwoFAModelTest.test_twofa_creation")
        twofa = TwoFA.objects.get(key=self.twofa.key)
        self.assertFalse(twofa.enable)
        self.assertFalse(twofa.scanned)
        self.assertIsNotNone(twofa.key)
        self.assertEqual(len(twofa.key), 32)

    def test_update_method(self):
        """Test the update method for TwoFA"""
        print("\nRunning test: TwoFAModelTest.test_update_method")
        twofa = TwoFA.objects.get(key=self.twofa.key)
        twofa.update("enable", True)
        self.assertTrue(twofa.enable)
        twofa.update("scanned", True)
        self.assertTrue(twofa.scanned)
        new_key = pyotp.random_base32()
        twofa.update("key", new_key)
        self.assertEqual(twofa.key, new_key)
        twofa.update("invalid_field", "value")  # Should not raise


class InvalidatedTokenModelTest(TestCase):
    """Test the InvalidatedToken model"""

    def setUp(self):
        """Set up test data"""
        future_time = timezone.now() + timedelta(hours=1)
        self.token = InvalidatedToken.objects.create(
            jti=uuid.uuid4(),
            token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U",
            exp=future_time,
            type=JWTType.ACCESS.name
        )
        past_time = timezone.now() - timedelta(hours=1)
        self.expired_token = InvalidatedToken.objects.create(
            jti=uuid.uuid4(),
            token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJleHBpcmVkIn0.9oSFH97qLCKKbo3pAHj1THYnuR1PV-Ta8g33-XhVWoU",
            exp=past_time,
            type=JWTType.REFRESH.name
        )

    def test_token_creation(self):
        """Test that tokens are created correctly"""
        print("\nRunning test: InvalidatedTokenModelTest.test_token_creation")
        token = InvalidatedToken.objects.get(jti=self.token.jti)
        self.assertEqual(token.type, JWTType.ACCESS.name)
        self.assertEqual(token.token, self.token.token)
        expired = InvalidatedToken.objects.get(jti=self.expired_token.jti)
        self.assertEqual(expired.type, JWTType.REFRESH.name)

    def test_delete_expired_token(self):
        """Test the delete_expired_token class method"""
        print("\nRunning test: InvalidatedTokenModelTest.test_delete_expired_token")
        before_count = InvalidatedToken.objects.count()
        self.assertEqual(before_count, 2)
        deleted = InvalidatedToken.delete_expired_token()
        self.assertEqual(deleted, 1)
        after_count = InvalidatedToken.objects.count()
        self.assertEqual(after_count, 1)
        with self.assertRaises(InvalidatedToken.DoesNotExist):
            InvalidatedToken.objects.get(jti=self.expired_token.jti)
        token = InvalidatedToken.objects.get(jti=self.token.jti)
        self.assertEqual(token.type, JWTType.ACCESS.name)
