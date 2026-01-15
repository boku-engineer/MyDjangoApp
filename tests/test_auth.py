"""
Auth Tests
Tests for the authentication views in accounts/views.py
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


class LoginViewTests(TestCase):
    """Tests for login_view."""

    def setUp(self):
        """Create test user and client."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.url = reverse('login')

    def test_login_page_loads(self):
        """Login page should load successfully."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_successful_login(self):
        """Valid credentials should log in user and redirect."""
        response = self.client.post(self.url, {
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertRedirects(response, reverse('game_table'))

    def test_invalid_username(self):
        """Invalid username should not log in."""
        response = self.client.post(self.url, {
            'username': 'wronguser',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_invalid_password(self):
        """Invalid password should not log in."""
        response = self.client.post(self.url, {
            'username': 'testuser',
            'password': 'wrongpass',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_authenticated_user_redirected(self):
        """Already authenticated user should be redirected to game."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('game_table'))

    def test_login_form_in_context(self):
        """Login form should be in context."""
        response = self.client.get(self.url)
        self.assertIn('form', response.context)


class RegisterViewTests(TestCase):
    """Tests for register_view."""

    def setUp(self):
        """Create client."""
        self.client = Client()
        self.url = reverse('register')

    def test_register_page_loads(self):
        """Register page should load successfully."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')

    def test_successful_registration(self):
        """Valid registration should create user and redirect to login."""
        response = self.client.post(self.url, {
            'username': 'newuser',
            'password1': 'complexpass123!',
            'password2': 'complexpass123!',
        })
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_user_not_logged_in_after_registration(self):
        """User should not be logged in after registration."""
        self.client.post(self.url, {
            'username': 'newuser',
            'password1': 'complexpass123!',
            'password2': 'complexpass123!',
        })
        response = self.client.get(reverse('game_table'))
        self.assertEqual(response.status_code, 302)  # Redirected to login

    def test_password_mismatch(self):
        """Mismatched passwords should not create user."""
        response = self.client.post(self.url, {
            'username': 'newuser',
            'password1': 'complexpass123!',
            'password2': 'differentpass123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='newuser').exists())

    def test_duplicate_username(self):
        """Duplicate username should not create user."""
        User.objects.create_user(username='existinguser', password='testpass123')
        response = self.client.post(self.url, {
            'username': 'existinguser',
            'password1': 'complexpass123!',
            'password2': 'complexpass123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username='existinguser').count(), 1)

    def test_weak_password(self):
        """Weak password should not create user."""
        response = self.client.post(self.url, {
            'username': 'newuser',
            'password1': '123',
            'password2': '123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='newuser').exists())

    def test_authenticated_user_redirected(self):
        """Already authenticated user should be redirected to game."""
        User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('game_table'))

    def test_register_form_in_context(self):
        """Register form should be in context."""
        response = self.client.get(self.url)
        self.assertIn('form', response.context)


class LogoutViewTests(TestCase):
    """Tests for logout_view."""

    def setUp(self):
        """Create test user and client."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.url = reverse('logout')

    def test_logout_redirects_to_login(self):
        """Logout should redirect to login page."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('login'))

    def test_logout_logs_out_user(self):
        """Logout should log out the user."""
        self.client.login(username='testuser', password='testpass123')
        self.client.get(self.url)
        response = self.client.get(reverse('game_table'))
        self.assertEqual(response.status_code, 302)  # Redirected to login

    def test_logout_when_not_logged_in(self):
        """Logout when not logged in should still redirect to login."""
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('login'))


class AuthIntegrationTests(TestCase):
    """Integration tests for authentication flow."""

    def setUp(self):
        """Create client."""
        self.client = Client()

    def test_full_registration_login_flow(self):
        """Test full flow: register -> login -> access game."""
        # Register
        self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'complexpass123!',
            'password2': 'complexpass123!',
        })

        # Login
        response = self.client.post(reverse('login'), {
            'username': 'newuser',
            'password': 'complexpass123!',
        })
        self.assertRedirects(response, reverse('game_table'))

        # Access game
        response = self.client.get(reverse('game_table'))
        self.assertEqual(response.status_code, 200)

    def test_login_logout_login_flow(self):
        """Test flow: login -> logout -> login again."""
        User.objects.create_user(username='testuser', password='testpass123')

        # Login
        self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123',
        })

        # Logout
        self.client.get(reverse('logout'))

        # Verify logged out
        response = self.client.get(reverse('game_table'))
        self.assertEqual(response.status_code, 302)

        # Login again
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertRedirects(response, reverse('game_table'))
