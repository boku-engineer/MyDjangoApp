"""
Core Engine Tests
Tests for the blackjack game logic in core/blackjack_engine.py
"""
from django.test import TestCase

from core.blackjack_engine import (
    CARDS,
    deal_card,
    calculate_score,
    is_blackjack,
    determine_winner,
    deal_initial_hands,
    play_dealer_hand,
)


class DealCardTests(TestCase):
    """Tests for deal_card function."""

    def test_deal_card_returns_valid_value(self):
        """deal_card should return a value from the CARDS list."""
        for _ in range(100):
            card = deal_card()
            self.assertIn(card, CARDS)

    def test_deal_card_returns_integer(self):
        """deal_card should return an integer."""
        card = deal_card()
        self.assertIsInstance(card, int)


class CalculateScoreTests(TestCase):
    """Tests for calculate_score function."""

    def test_simple_score(self):
        """Calculate score for simple hand without aces."""
        self.assertEqual(calculate_score([5, 7]), 12)
        self.assertEqual(calculate_score([10, 10]), 20)
        self.assertEqual(calculate_score([2, 3, 4]), 9)

    def test_ace_as_eleven(self):
        """Ace should count as 11 when it doesn't cause bust."""
        self.assertEqual(calculate_score([11, 9]), 20)
        self.assertEqual(calculate_score([11, 5]), 16)

    def test_ace_converts_to_one(self):
        """Ace should convert from 11 to 1 when hand would bust."""
        self.assertEqual(calculate_score([11, 10, 5]), 16)  # 11+10+5=26, ace becomes 1
        self.assertEqual(calculate_score([11, 11, 9]), 21)  # Two aces, one becomes 1

    def test_multiple_aces(self):
        """Multiple aces should convert as needed."""
        self.assertEqual(calculate_score([11, 11]), 12)  # One ace becomes 1
        self.assertEqual(calculate_score([11, 11, 11]), 13)  # Two aces become 1

    def test_blackjack_score(self):
        """Blackjack hand should score 21."""
        self.assertEqual(calculate_score([11, 10]), 21)
        self.assertEqual(calculate_score([10, 11]), 21)

    def test_bust_score(self):
        """Bust hand should return score over 21."""
        self.assertEqual(calculate_score([10, 10, 5]), 25)


class IsBlackjackTests(TestCase):
    """Tests for is_blackjack function."""

    def test_blackjack_with_ace_and_ten(self):
        """Ace + 10-value card is blackjack."""
        self.assertTrue(is_blackjack([11, 10]))
        self.assertTrue(is_blackjack([10, 11]))

    def test_not_blackjack_with_three_cards(self):
        """21 with more than 2 cards is not blackjack."""
        self.assertFalse(is_blackjack([7, 7, 7]))
        self.assertFalse(is_blackjack([5, 5, 11]))

    def test_not_blackjack_with_lower_score(self):
        """Two cards not totaling 21 is not blackjack."""
        self.assertFalse(is_blackjack([10, 9]))
        self.assertFalse(is_blackjack([5, 5]))


class DetermineWinnerTests(TestCase):
    """Tests for determine_winner function."""

    def test_player_blackjack_wins(self):
        """Player blackjack beats dealer non-blackjack."""
        result = determine_winner([11, 10], [10, 9])
        self.assertEqual(result, 'blackjack')

    def test_dealer_blackjack_wins(self):
        """Dealer blackjack beats player non-blackjack."""
        result = determine_winner([10, 9], [11, 10])
        self.assertEqual(result, 'dealer_win')

    def test_both_blackjack_is_push(self):
        """Both having blackjack is a push."""
        result = determine_winner([11, 10], [10, 11])
        self.assertEqual(result, 'push')

    def test_player_bust(self):
        """Player busting loses."""
        result = determine_winner([10, 10, 5], [10, 7])
        self.assertEqual(result, 'player_bust')

    def test_dealer_bust(self):
        """Dealer busting means player wins."""
        result = determine_winner([10, 7], [10, 10, 5])
        self.assertEqual(result, 'dealer_bust')

    def test_player_higher_score_wins(self):
        """Player with higher score wins."""
        result = determine_winner([10, 9], [10, 8])
        self.assertEqual(result, 'player_win')

    def test_dealer_higher_score_wins(self):
        """Dealer with higher score wins."""
        result = determine_winner([10, 8], [10, 9])
        self.assertEqual(result, 'dealer_win')

    def test_equal_scores_is_push(self):
        """Equal scores is a push."""
        result = determine_winner([10, 8], [9, 9])
        self.assertEqual(result, 'push')


class DealInitialHandsTests(TestCase):
    """Tests for deal_initial_hands function."""

    def test_returns_two_hands(self):
        """Should return player and dealer hands."""
        player, dealer = deal_initial_hands()
        self.assertIsInstance(player, list)
        self.assertIsInstance(dealer, list)

    def test_each_hand_has_two_cards(self):
        """Each hand should have exactly 2 cards."""
        player, dealer = deal_initial_hands()
        self.assertEqual(len(player), 2)
        self.assertEqual(len(dealer), 2)

    def test_cards_are_valid(self):
        """All cards should be valid values."""
        player, dealer = deal_initial_hands()
        for card in player + dealer:
            self.assertIn(card, CARDS)


class PlayDealerHandTests(TestCase):
    """Tests for play_dealer_hand function."""

    def test_dealer_stands_on_17(self):
        """Dealer should stand on 17."""
        result = play_dealer_hand([10, 7])
        self.assertEqual(result, [10, 7])

    def test_dealer_stands_on_higher(self):
        """Dealer should stand on 18+."""
        result = play_dealer_hand([10, 9])
        self.assertEqual(result, [10, 9])

    def test_dealer_hits_on_16(self):
        """Dealer should hit on 16 or less."""
        result = play_dealer_hand([10, 6])
        self.assertGreater(len(result), 2)

    def test_dealer_does_not_modify_original(self):
        """Should not modify the original hand."""
        original = [10, 6]
        play_dealer_hand(original)
        self.assertEqual(original, [10, 6])

    def test_dealer_final_score_17_or_bust(self):
        """Dealer final score should be 17+ or bust."""
        for _ in range(50):
            result = play_dealer_hand([5, 5])
            score = calculate_score(result)
            self.assertTrue(score >= 17 or score > 21)
