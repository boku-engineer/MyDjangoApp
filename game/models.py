from django.db import models
from django.contrib.auth.models import User


class GameSession(models.Model):
    """Active/in-progress blackjack games."""
    
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('player_win', 'Player Win'),
        ('dealer_win', 'Dealer Win'),
        ('push', 'Push'),
        ('blackjack', 'Blackjack'),
        ('player_bust', 'Player Bust'),
        ('dealer_bust', 'Dealer Bust'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game_sessions')
    player_cards = models.JSONField(default=list)
    dealer_cards = models.JSONField(default=list)
    player_score = models.IntegerField(default=0)
    dealer_score = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    is_player_turn = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Game {self.id} - {self.user.username} - {self.status}"


class GameHistory(models.Model):
    """Completed blackjack games."""
    
    RESULT_CHOICES = [
        ('win', 'Win'),
        ('loss', 'Loss'),
        ('push', 'Push'),
        ('blackjack', 'Blackjack'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game_history')
    player_final_cards = models.JSONField(default=list)
    dealer_final_cards = models.JSONField(default=list)
    player_final_score = models.IntegerField()
    dealer_final_score = models.IntegerField()
    result = models.CharField(max_length=20, choices=RESULT_CHOICES)
    played_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-played_at']
        verbose_name_plural = 'Game histories'
    
    def __str__(self):
        return f"{self.user.username} - {self.result} - {self.played_at.strftime('%Y-%m-%d %H:%M')}"
