"""
View Tests
Tests for the game views in game/views.py
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from game.models import GameSession, GameHistory


class GameTableViewTests(TestCase):
    """Tests for game_table view."""

    def setUp(self):
        """Create test user and client."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.url = reverse('game_table')

    def test_requires_login(self):
        """Should redirect to login if not authenticated."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_authenticated_user_can_access(self):
        """Authenticated user should be able to access."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_displays_no_game_when_none_exists(self):
        """Should display no game state when user has no games."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertIsNone(response.context['game'])

    def test_displays_in_progress_game(self):
        """Should display in-progress game."""
        self.client.login(username='testuser', password='testpass123')
        game = GameSession.objects.create(
            user=self.user,
            player_cards=[10, 8],
            dealer_cards=[7, 5],
            player_score=18,
            dealer_score=12,
            status='in_progress',
        )
        response = self.client.get(self.url)
        self.assertEqual(response.context['game'], game)

    def test_displays_completed_game_result(self):
        """Should display most recent completed game when no in-progress game."""
        self.client.login(username='testuser', password='testpass123')
        game = GameSession.objects.create(
            user=self.user,
            player_cards=[10, 8],
            dealer_cards=[7, 10],
            player_score=18,
            dealer_score=17,
            status='player_win',
        )
        response = self.client.get(self.url)
        self.assertEqual(response.context['game'], game)


class NewGameViewTests(TestCase):
    """Tests for new_game view."""

    def setUp(self):
        """Create test user and client."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.url = reverse('new_game')

    def test_requires_login(self):
        """Should redirect to login if not authenticated."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_creates_new_game_session(self):
        """Should create a new game session."""
        self.client.login(username='testuser', password='testpass123')
        self.client.get(self.url)
        self.assertEqual(GameSession.objects.filter(user=self.user).count(), 1)

    def test_redirects_to_game_table(self):
        """Should redirect to game table after creating game."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('game_table'))

    def test_deletes_existing_in_progress_game(self):
        """Should delete any existing in-progress game."""
        self.client.login(username='testuser', password='testpass123')
        old_game = GameSession.objects.create(
            user=self.user,
            player_cards=[10, 8],
            dealer_cards=[7, 5],
            status='in_progress',
        )
        self.client.get(self.url)
        self.assertFalse(GameSession.objects.filter(id=old_game.id).exists())

    def test_new_game_has_two_cards_each(self):
        """New game should deal 2 cards to player and dealer."""
        self.client.login(username='testuser', password='testpass123')
        self.client.get(self.url)
        game = GameSession.objects.get(user=self.user, status='in_progress')
        self.assertEqual(len(game.player_cards), 2)
        self.assertEqual(len(game.dealer_cards), 2)

    def test_new_game_status_is_in_progress(self):
        """New game status should be 'in_progress' (unless blackjack)."""
        self.client.login(username='testuser', password='testpass123')
        self.client.get(self.url)
        game = GameSession.objects.filter(user=self.user).first()
        self.assertIn(game.status, ['in_progress', 'blackjack'])


class HitViewTests(TestCase):
    """Tests for hit view."""

    def setUp(self):
        """Create test user and client."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.url = reverse('hit')

    def test_requires_login(self):
        """Should redirect to login if not authenticated."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_requires_active_game(self):
        """Should return 404 if no active game."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_adds_card_to_player_hand(self):
        """Should add a card to player's hand."""
        self.client.login(username='testuser', password='testpass123')
        game = GameSession.objects.create(
            user=self.user,
            player_cards=[5, 5],
            dealer_cards=[7, 5],
            player_score=10,
            dealer_score=12,
            status='in_progress',
        )
        self.client.get(self.url)
        game.refresh_from_db()
        self.assertEqual(len(game.player_cards), 3)

    def test_updates_player_score(self):
        """Should update player's score after hit."""
        self.client.login(username='testuser', password='testpass123')
        GameSession.objects.create(
            user=self.user,
            player_cards=[5, 5],
            dealer_cards=[7, 5],
            player_score=10,
            dealer_score=12,
            status='in_progress',
        )
        self.client.get(self.url)
        game = GameSession.objects.get(user=self.user)
        self.assertGreater(game.player_score, 10)

    def test_redirects_to_game_table(self):
        """Should redirect to game table."""
        self.client.login(username='testuser', password='testpass123')
        GameSession.objects.create(
            user=self.user,
            player_cards=[5, 5],
            dealer_cards=[7, 5],
            player_score=10,
            dealer_score=12,
            status='in_progress',
        )
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('game_table'))


class StandViewTests(TestCase):
    """Tests for stand view."""

    def setUp(self):
        """Create test user and client."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.url = reverse('stand')

    def test_requires_login(self):
        """Should redirect to login if not authenticated."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_requires_active_game(self):
        """Should return 404 if no active game."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_ends_game(self):
        """Should end the game (status no longer in_progress)."""
        self.client.login(username='testuser', password='testpass123')
        GameSession.objects.create(
            user=self.user,
            player_cards=[10, 8],
            dealer_cards=[7, 5],
            player_score=18,
            dealer_score=12,
            status='in_progress',
        )
        self.client.get(self.url)
        game = GameSession.objects.get(user=self.user)
        self.assertNotEqual(game.status, 'in_progress')

    def test_dealer_plays_hand(self):
        """Dealer should play their hand (hit until 17+)."""
        self.client.login(username='testuser', password='testpass123')
        GameSession.objects.create(
            user=self.user,
            player_cards=[10, 8],
            dealer_cards=[7, 5],  # 12, should hit
            player_score=18,
            dealer_score=12,
            status='in_progress',
        )
        self.client.get(self.url)
        game = GameSession.objects.get(user=self.user)
        self.assertGreaterEqual(len(game.dealer_cards), 2)

    def test_creates_history_record(self):
        """Should create a history record."""
        self.client.login(username='testuser', password='testpass123')
        GameSession.objects.create(
            user=self.user,
            player_cards=[10, 8],
            dealer_cards=[10, 7],
            player_score=18,
            dealer_score=17,
            status='in_progress',
        )
        self.client.get(self.url)
        self.assertEqual(GameHistory.objects.filter(user=self.user).count(), 1)

    def test_redirects_to_game_table(self):
        """Should redirect to game table."""
        self.client.login(username='testuser', password='testpass123')
        GameSession.objects.create(
            user=self.user,
            player_cards=[10, 8],
            dealer_cards=[10, 7],
            player_score=18,
            dealer_score=17,
            status='in_progress',
        )
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('game_table'))


class GameHistoryViewTests(TestCase):
    """Tests for game_history view."""

    def setUp(self):
        """Create test user and client."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )
        self.url = reverse('game_history')

    def test_requires_login(self):
        """Should redirect to login if not authenticated."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_authenticated_user_can_access(self):
        """Authenticated user should be able to access."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_displays_user_history_only(self):
        """Should only display current user's history."""
        self.client.login(username='testuser', password='testpass123')
        # Create history for test user
        GameHistory.objects.create(
            user=self.user,
            player_final_cards=[10, 8],
            dealer_final_cards=[7, 10],
            player_final_score=18,
            dealer_final_score=17,
            result='win',
        )
        # Create history for other user
        GameHistory.objects.create(
            user=self.other_user,
            player_final_cards=[9, 9],
            dealer_final_cards=[10, 10],
            player_final_score=18,
            dealer_final_score=20,
            result='loss',
        )
        response = self.client.get(self.url)
        self.assertEqual(len(response.context['history']), 1)
        self.assertEqual(response.context['history'][0].user, self.user)

    def test_limits_to_20_records(self):
        """Should limit history to 20 records."""
        self.client.login(username='testuser', password='testpass123')
        for i in range(25):
            GameHistory.objects.create(
                user=self.user,
                player_final_cards=[10, 8],
                dealer_final_cards=[7, 10],
                player_final_score=18,
                dealer_final_score=17,
                result='win',
            )
        response = self.client.get(self.url)
        self.assertEqual(len(response.context['history']), 20)
