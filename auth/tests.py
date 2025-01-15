from django.test import TestCase, Clients


# Create your tests here.
class AuthTest(TestCase):
    def setUp(self):
        self.client = Clients()

    def test(self):
        url = '/auth/login'
        data = {
            "email": "alexandre.tresallet@gmail.com",
            "password": "1234"
        }
        response = self.client.get('/auth/login')
        self.assertEqual(response.status_code, 200)
        # response = self.client.post(url, data)
        # self.assertEqual(response.status_code, 400)