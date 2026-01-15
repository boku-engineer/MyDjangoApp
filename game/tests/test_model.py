"""
Model Tests
Tests for the database models in game/models.py
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

from game.models import GameSession, GameHistory

User = get_user_model()


class GameSessionModelTests(TestCase):
    """Tests for GameSession model."""

    def setUp(self):
        """Create a test user."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_create_game_session(self):
        """Should be able to create a game session."""
        game = GameSession.objects.create(
            user=self.user,
            player_cards=[10, 8],
            dealer_cards=[7, 5],
            player_score=18,
            dealer_score=12,
        )
        self.assertIsNotNone(game.id)
        self.assertEqual(game.user, self.user)

    def test_default_status_is_in_progress(self):
        """Default status should be 'in_progress'."""
        game = GameSession.objects.create(
            user=self.user,
            player_cards=[10, 8],
            dealer_cards=[7, 5],
        )
        self.assertEqual(game.status, 'in_progress')

    def test_default_is_player_turn_is_true(self):
        """Default is_player_turn should be True."""
        game = GameSession.objects.create(
            user=self.user,
            player_cards=[10, 8],
            dealer_cards=[7, 5],
        )
        self.assertTrue(game.is_player_turn)

    def test_json_fields_store_lists(self):
        """JSONFields should properly store card lists."""
        player_cards = [11, 10]
        dealer_cards = [7, 8, 6]
        game = GameSession.objects.create(
            user=self.user,
            player_cards=player_cards,
            dealer_cards=dealer_cards,
        )
        game.refresh_from_db()
        self.assertEqual(game.player_cards, player_cards)
        self.assertEqual(game.dealer_cards, dealer_cards)

    def test_status_choices(self):
        """Should accept valid status choices."""
        valid_statuses = [
            'in_progress', 'player_win', 'dealer_win',
            'push', 'blackjack', 'player_bust', 'dealer_bust'
        ]
        for status in valid_statuses:
            game = GameSession.objects.create(
                user=self.user,
                player_cards=[10, 8],
                dealer_cards=[7, 5],
                status=status,
            )
            self.assertEqual(game.status, status)

    def test_str_representation(self):
        """String representation should include game id, username, and status."""
        game = GameSession.objects.create(
            user=self.user,
            player_cards=[10, 8],
            dealer_cards=[7, 5],
        )
        str_repr = str(game)
        self.assertIn(str(game.id), str_repr)
        self.assertIn(self.user.username, str_repr)
        self.assertIn('in_progress', str_repr)

    def test_ordering_by_created_at_descending(self):
        """Games should be ordered by created_at descending."""
        game1 = GameSession.objects.create(
            user=self.user,
            player_cards=[10, 8],
            dealer_cards=[7, 5],
        )
        game2 = GameSession.objects.create(
            user=self.user,
            player_cards=[9, 9],
            dealer_cards=[6, 6],
        )
        games = GameSession.objects.all()
        self.assertEqual(games[0], game2)
        self.assertEqual(games[1], game1)


class GameHistoryModelTests(TestCase):
    """Tests for GameHistory model."""

    def setUp(self):
        """Create a test user."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_create_game_history(self):
        """Should be able to create a game history record."""
        history = GameHistory.objects.create(
            user=self.user,
            player_final_cards=[10, 8, 3],
            dealer_final_cards=[7, 10],
            player_final_score=21,
            dealer_final_score=17,
            result='win',
        )
        self.assertIsNotNone(history.id)
        self.assertEqual(history.user, self.user)

    def test_result_choices(self):
        """Should accept valid result choices."""
        valid_results = ['win', 'loss', 'push', 'blackjack']
        for result in valid_results:
            history = GameHistory.objects.create(
                user=self.user,
                player_final_cards=[10, 8],
                dealer_final_cards=[7, 5],
                player_final_score=18,
                dealer_final_score=12,
                result=result,
            )
            self.assertEqual(history.result, result)

    def test_played_at_auto_set(self):
        """played_at should be automatically set on creation."""
        history = GameHistory.objects.create(
            user=self.user,
            player_final_cards=[10, 8],
            dealer_final_cards=[7, 5],
            player_final_score=18,
            dealer_final_score=12,
            result='win',
        )
        self.assertIsNotNone(history.played_at)

    def test_json_fields_store_lists(self):
        """JSONFields should properly store card lists."""
        player_cards = [11, 10]
        dealer_cards = [7, 8, 6]
        history = GameHistory.objects.create(
            user=self.user,
            player_final_cards=player_cards,
            dealer_final_cards=dealer_cards,
            player_final_score=21,
            dealer_final_score=21,
            result='push',
        )
        history.refresh_from_db()
        self.assertEqual(history.player_final_cards, player_cards)
        self.assertEqual(history.dealer_final_cards, dealer_cards)

    def test_str_representation(self):
        """String representation should include username and result."""
        history = GameHistory.objects.create(
            user=self.user,
            player_final_cards=[10, 8],
            dealer_final_cards=[7, 5],
            player_final_score=18,
            dealer_final_score=12,
            result='win',
        )
        str_repr = str(history)
        self.assertIn(self.user.username, str_repr)
        self.assertIn('win', str_repr)

    def test_ordering_by_played_at_descending(self):
        """History should be ordered by played_at descending."""
        history1 = GameHistory.objects.create(
            user=self.user,
            player_final_cards=[10, 8],
            dealer_final_cards=[7, 5],
            player_final_score=18,
            dealer_final_score=12,
            result='win',
        )
        history2 = GameHistory.objects.create(
            user=self.user,
            player_final_cards=[9, 9],
            dealer_final_cards=[6, 6],
            player_final_score=18,
            dealer_final_score=12,
            result='loss',
        )
        histories = GameHistory.objects.all()
        self.assertEqual(histories[0], history2)
        self.assertEqual(histories[1], history1)


class ModelRelationshipTests(TestCase):
    """Tests for model relationships."""

    def setUp(self):
        """Create test users."""
        self.user1 = User.objects.create_user(
            username='user1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='testpass123'
        )

    def test_user_can_have_multiple_sessions(self):
        """A user can have multiple game sessions."""
        GameSession.objects.create(
            user=self.user1,
            player_cards=[10, 8],
            dealer_cards=[7, 5],
        )
        GameSession.objects.create(
            user=self.user1,
            player_cards=[9, 9],
            dealer_cards=[6, 6],
        )
        self.assertEqual(self.user1.game_sessions.count(), 2)

    def test_user_can_have_multiple_history(self):
        """A user can have multiple game history records."""
        GameHistory.objects.create(
            user=self.user1,
            player_final_cards=[10, 8],
            dealer_final_cards=[7, 5],
            player_final_score=18,
            dealer_final_score=12,
            result='win',
        )
        GameHistory.objects.create(
            user=self.user1,
            player_final_cards=[9, 9],
            dealer_final_cards=[10, 10],
            player_final_score=18,
            dealer_final_score=20,
            result='loss',
        )
        self.assertEqual(self.user1.game_history.count(), 2)

    def test_cascade_delete_on_user_deletion(self):
        """Deleting user should delete their games and history."""
        GameSession.objects.create(
            user=self.user1,
            player_cards=[10, 8],
            dealer_cards=[7, 5],
        )
        GameHistory.objects.create(
            user=self.user1,
            player_final_cards=[10, 8],
            dealer_final_cards=[7, 5],
            player_final_score=18,
            dealer_final_score=12,
            result='win',
        )
        user1_id = self.user1.id
        self.user1.delete()
        self.assertEqual(GameSession.objects.filter(user_id=user1_id).count(), 0)
        self.assertEqual(GameHistory.objects.filter(user_id=user1_id).count(), 0)
