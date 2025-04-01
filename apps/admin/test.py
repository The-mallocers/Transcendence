from django.test import TestCase

from apps.client.models import Clients


class AdminTestCase(TestCase):
    def test_animals_can_speak(self):
        admin = Clients.objects.get(profile__username='admin')
        self.assertEqual(admin.profile.email, 'admin@transcendence.fr')
