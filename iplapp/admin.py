from django.contrib import admin
from .models import Team, Player, Match, Ground, PlayerStats, IPLrole
# Register your models here.


@admin.register(Team)
class TeamList(admin.ModelAdmin):
    list_display = ('team_name', 'coach')
    search_fields = ('team_name',)
    ordering = ['team_name']


@admin.register(Player)
class PlayerList(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'team')
    list_filter = ('team', 'eligibility_status')
    search_fields = ('first_name', 'last_name')
    ordering = ['first_name']


@admin.register(Ground)
class GroundList(admin.ModelAdmin):
    list_display = ('ground_name', 'city', 'state')
    list_filter = ('city', 'state')
    search_fields = ('ground_name',)
    ordering = ['ground_name']


@admin.register(Match)
class MatchList(admin.ModelAdmin):
    list_display = ('match_day', 'home_team', 'guest_team')
    list_filter = ('home_team', 'guest_team', 'match_status')
    search_fields = ('home_team',)
    ordering = ['-match_day']


@admin.register(PlayerStats)
class GoalList(admin.ModelAdmin):
    list_display = ('player', 'team', 'match')
    list_filter = ('team', 'player')
    search_fields = ('team', 'player')
    ordering = ['-created_date']


@admin.register(IPLrole)
class IPLroleList(admin.ModelAdmin):
    list_display = ('role', 'receiver_name', 'receiver_email')
    list_filter = ('role', 'receiver_name')
    search_fields = ('role', 'receiver_name')
    ordering = ['-role']
