from rest_framework.test import APITestCase


class RegisterViewTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.path = '/auth/registration/'

    def test_successful_registration(self):
        data = {
            'email': 'foo@example.com',
            'password1': 'testPassword!1',
            'password2': 'testPassword!1'
        }
        self.assertFalse(User.objects.exists())
        response = self.client.post(
            self.path, data=data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(email=data['email']).exists())

    def test_unique_email(self):
        existing_user = UserFactory(email='foo@example.com')
        data = {
            'email': existing_user.email,
            'password1': 'testPassword!1',
            'password2': 'testPassword!1'
        }
        response = self.client.post(
            self.path, data=data, format='json')
        self.assertEqual(response.status_code, 400)