"""
Game Service Layer

Business logic for blackjack game operations, separated from views
for better testability and future API support.
"""
from .models import GameSession, GameHistory
from core.blackjack_engine import (
    deal_card,
    calculate_score,
    is_blackjack,
    determine_winner,
    deal_initial_hands,
    play_dealer_hand,
)


def create_new_game(user):
    """
    Create a new game session for the user.
    
    Deletes any existing in-progress games and deals initial hands.
    Returns the new game and whether the player has blackjack.
    """
    # End any existing in-progress game
    GameSession.objects.filter(user=user, status='in_progress').delete()

    # Deal initial hands
    player_cards, dealer_cards = deal_initial_hands()

    # Create new game session
    game = GameSession.objects.create(
        user=user,
        player_cards=player_cards,
        dealer_cards=dealer_cards,
        player_score=calculate_score(player_cards),
        dealer_score=calculate_score(dealer_cards),
    )

    # Check for player blackjack
    has_blackjack = is_blackjack(player_cards)
    
    return game, has_blackjack


def player_hit(game):
    """
    Player draws another card.
    
    Returns True if player busted, False otherwise.
    """
    game.player_cards.append(deal_card())
    game.player_score = calculate_score(game.player_cards)
    game.save()

    return game.player_score > 21


def player_stand(game):
    """
    Player stands - dealer plays out their hand.
    """
    game.dealer_cards = play_dealer_hand(game.dealer_cards)
    game.dealer_score = calculate_score(game.dealer_cards)
    game.is_player_turn = False
    game.save()


def end_game(game):
    """
    End the game - determine winner and save to history.
    """
    result = determine_winner(game.player_cards, game.dealer_cards)

    # Update game status
    game.status = result
    game.is_player_turn = False
    game.save()

    # Map result to history result
    result_map = {
        'blackjack': 'blackjack',
        'player_win': 'win',
        'dealer_bust': 'win',
        'dealer_win': 'loss',
        'player_bust': 'loss',
        'push': 'push',
    }

    # Save to history
    GameHistory.objects.create(
        user=game.user,
        player_final_cards=game.player_cards,
        dealer_final_cards=game.dealer_cards,
        player_final_score=game.player_score,
        dealer_final_score=game.dealer_score,
        result=result_map.get(result, 'loss'),
    )


def get_current_game(user):
    """
    Get the current game for display.
    
    Returns in-progress game if exists, otherwise most recent completed game.
    """
    game = GameSession.objects.filter(user=user, status='in_progress').first()
    if not game:
        game = GameSession.objects.filter(user=user).exclude(status='in_progress').first()
    return game


def get_user_history(user, limit=20):
    """
    Get the user's game history.
    """
    return GameHistory.objects.filter(user=user)[:limit]
