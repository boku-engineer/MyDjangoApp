from django.contrib import admin
from .models import GameSession, GameHistory


@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'player_score', 'dealer_score', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(GameHistory)
class GameHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'result', 'player_final_score', 'dealer_final_score', 'played_at')
    list_filter = ('result', 'played_at')
    search_fields = ('user__username',)
    readonly_fields = ('played_at',)
