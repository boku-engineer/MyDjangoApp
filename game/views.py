from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import GameSession, GameHistory
from core.blackjack_engine import (
    deal_card,
    calculate_score,
    is_blackjack,
    determine_winner,
    deal_initial_hands,
    play_dealer_hand,
)


@login_required
def game_table(request):
    """Main game interface - shows current game or prompts to start new one."""
    # First check for in-progress game, then show most recent completed game
    game = GameSession.objects.filter(user=request.user, status='in_progress').first()
    if not game:
        # Show most recent completed game so user can see the result
        game = GameSession.objects.filter(user=request.user).exclude(status='in_progress').first()
    return render(request, 'game/table.html', {'game': game})


@login_required
def new_game(request):
    """Start a new game - deal initial cards."""
    # End any existing in-progress game
    GameSession.objects.filter(user=request.user, status='in_progress').delete()

    # Deal initial hands
    player_cards, dealer_cards = deal_initial_hands()

    # Create new game session
    game = GameSession.objects.create(
        user=request.user,
        player_cards=player_cards,
        dealer_cards=dealer_cards,
        player_score=calculate_score(player_cards),
        dealer_score=calculate_score(dealer_cards),
    )

    # Check for player blackjack
    if is_blackjack(player_cards):
        return _end_game(game)

    return redirect('game_table')


@login_required
def hit(request):
    """Player draws another card."""
    game = get_object_or_404(GameSession, user=request.user, status='in_progress')

    # Add a card to player's hand
    game.player_cards.append(deal_card())
    game.player_score = calculate_score(game.player_cards)
    game.save()

    # Check if player busted
    if game.player_score > 21:
        return _end_game(game)

    return redirect('game_table')


@login_required
def stand(request):
    """Player stands - dealer plays out their hand."""
    game = get_object_or_404(GameSession, user=request.user, status='in_progress')

    # Dealer plays
    game.dealer_cards = play_dealer_hand(game.dealer_cards)
    game.dealer_score = calculate_score(game.dealer_cards)
    game.is_player_turn = False
    game.save()

    return _end_game(game)


def _end_game(game):
    """End the game - determine winner and save to history."""
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

    return redirect('game_table')


@login_required
def game_history(request):
    """View past games."""
    history = GameHistory.objects.filter(user=request.user)[:20]
    return render(request, 'game/history.html', {'history': history})
