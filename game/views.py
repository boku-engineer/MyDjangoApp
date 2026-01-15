from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import GameSession
from . import services


@login_required
def game_table(request):
    """Main game interface - shows current game or prompts to start new one."""
    game = services.get_current_game(request.user)
    return render(request, 'game/table.html', {'game': game})


@login_required
def new_game(request):
    """Start a new game - deal initial cards."""
    game, has_blackjack = services.create_new_game(request.user)

    if has_blackjack:
        services.end_game(game)

    return redirect('game_table')


@login_required
def hit(request):
    """Player draws another card."""
    game = get_object_or_404(GameSession, user=request.user, status='in_progress')

    player_busted = services.player_hit(game)

    if player_busted:
        services.end_game(game)

    return redirect('game_table')


@login_required
def stand(request):
    """Player stands - dealer plays out their hand."""
    game = get_object_or_404(GameSession, user=request.user, status='in_progress')

    services.player_stand(game)
    services.end_game(game)

    return redirect('game_table')


@login_required
def game_history(request):
    """View past games."""
    history = services.get_user_history(request.user)
    return render(request, 'game/history.html', {'history': history})

