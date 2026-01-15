"""
Blackjack game engine adapted from learning_blackjack.py
Provides core game logic for the Django web application.
"""
import random

CARDS = [11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]


def deal_card():
    """Returns a random card value."""
    return random.choice(CARDS)


def calculate_score(hand):
    """Calculate score, adjusting aces from 11 to 1 if needed."""
    score = sum(hand)
    aces = hand.count(11)
    while score > 21 and aces > 0:
        score -= 10
        aces -= 1
    return score


def is_blackjack(hand):
    """Check for natural blackjack (21 with 2 cards)."""
    return len(hand) == 2 and calculate_score(hand) == 21


def determine_winner(player_cards, dealer_cards):
    """
    Determine the winner of the game.

    Returns:
        str: One of 'blackjack', 'player_win', 'dealer_win', 'push', 'player_bust', 'dealer_bust'
    """
    player_score = calculate_score(player_cards)
    dealer_score = calculate_score(dealer_cards)

    if is_blackjack(player_cards) and not is_blackjack(dealer_cards):
        return 'blackjack'
    if is_blackjack(dealer_cards) and not is_blackjack(player_cards):
        return 'dealer_win'
    if is_blackjack(player_cards) and is_blackjack(dealer_cards):
        return 'push'
    if player_score > 21:
        return 'player_bust'
    if dealer_score > 21:
        return 'dealer_bust'
    if player_score > dealer_score:
        return 'player_win'
    if player_score < dealer_score:
        return 'dealer_win'
    return 'push'


def deal_initial_hands():
    """Deal initial two cards each to player and dealer."""
    player_cards = [deal_card(), deal_card()]
    dealer_cards = [deal_card(), deal_card()]
    return player_cards, dealer_cards


def play_dealer_hand(dealer_cards):
    """
    Play out the dealer's hand according to standard rules.
    Dealer must hit on 16 or less, stand on 17+.

    Returns:
        list: The final dealer hand
    """
    cards = dealer_cards.copy()
    while calculate_score(cards) < 17:
        cards.append(deal_card())
    return cards
