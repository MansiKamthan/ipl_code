from django.shortcuts import render, get_object_or_404, redirect
from .models import Team, Player, Match, IPLrole, PlayerStats
from .forms import TeamForm, PlayerFormEditAdd, MatchForm, PlayerStatsForm, MatchStatusForm, AssignRoleForm
from .forms import UserLoginForm, UserRegisterForm, PlayerForm, User, authenticate, login, logout
from django.utils import timezone
from django.db.models import Count, Sum
from django.db.models import Q, F
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect



# Create your views here.
###### Team Views ######

def team_list(request):
    teams = Team.objects.filter(active_status='active')
    return render(request, 'iplapp/team/team_list.html', {'teams': teams})


def team_detail(request, pk):
    cap = 'None';
    Won = 0;
    Lost = 0;
    Drawn = 0;
    try:
        team = get_object_or_404(Team, pk=pk)
        name = team.team_name
        run_list = PlayerStats.objects.filter(team=team).order_by('-created_date')[:10]
        matchesasguest = Match.objects.filter(guest_team=team.id)
        for match in matchesasguest:
            if match.guest_team_score > match.home_team_score:
                Won = Won + 1;
            if match.guest_team_score == match.home_team_score:
                Drawn = Drawn + 1
            if match.guest_team_score < match.home_team_score:
                Lost = Lost + 1

        matchesashome = Match.objects.filter(home_team=team.id)
        for match in matchesashome:
            if match.home_team_score > match.guest_team_score:
                Won = Won + 1;
            if match.guest_team_score == match.home_team_score:
                Drawn = Drawn + 1
            if match.home_team_score < match.guest_team_score:
                Lost = Lost + 1
        players = Player.objects.filter(team=team.id).filter(eligibility_status='eligible')
        for player in players:
            if player.team_role == 'captain':
                cap = player.first_name + " " + player.last_name
        totalrun = run_list.aggregate(TOTAL=Sum('run'))['TOTAL']
        return render(request, 'iplapp/team/team_detail.html', {'team': team,
                                                'run_list': run_list,
                                                'goals_count': totalrun,'players':players,
                                                'cap':cap,'Won':Won,'Lost':Lost,'Drawn':Drawn
                                                      })
    except Team.DoesNotExist:
        return render(request, 'iplapp/team/team_detail.html',
                      {'run_list': None,'cap':None,'players':None,'totalrun':0})

@login_required
def team_new(request):
    if request.method == "POST":
        #update
        form = TeamForm(request.POST)
        if form.is_valid():
            team = form.save(commit=False)
            team.created_date = timezone.now()
            team.save()
            teams = Team.objects.filter(created_date__lte=timezone.now())
            return render(request, 'iplapp/team/team_list.html', {'teams': teams})
    else:
        #edit
        form = TeamForm()
    return render(request, 'iplapp/team/team_edit.html', {'form': form})

@login_required
def team_edit(request, pk):
    team = get_object_or_404(Team, pk=pk)
    if request.method == "POST":
        form = TeamForm(request.POST, instance=team)
        if form.is_valid():
            team = form.save(commit=False)
            team.created_date = timezone.now()
            team.save()
            teams = Team.objects.filter(created_date__lte=timezone.now())
            return render(request, 'iplapp/team/team_list.html', {'teams': teams})
    else:
        #edit
        form = TeamForm(instance=team)
    return render(request, 'iplapp/team/team_edit.html', {'form': form})

@login_required
def team_delete(request, pk):
    team = get_object_or_404(Team, pk=pk)
    team.active_status = 'inactive'
    team.save()
    return redirect('iplapp:team_list')


## Player Views
def player_detail(request, pk):
    player = get_object_or_404(Player, pk=pk)
    team = player.team
    run_list = PlayerStats.objects.filter(player=player).order_by('-created_date')[:5]
    run_count = run_list.aggregate(TOTAL=Sum('run'))['TOTAL']
    return render(request, 'iplapp/player/player_detail.html', {'player': player,
                                                                'run_list': run_list,
                                                                'run_count': run_count,
                                                                'team': team})


def player_list(request):
    player_list = Player.objects.exclude(eligibility_status='ineligible')
    player_count = player_list.count()

    if(request.method == "GET"):
        qs = request.GET.get('playername')
        if qs:
            player_list = Player.objects.filter(Q(last_name__icontains=qs) |
                                                Q(first_name__icontains=qs)).exclude(eligibility_status='ineligible')
    return render(request, 'iplapp/player/player_list.html', {'player_list': player_list,
                                                              'player_count': player_count})

@login_required
def myteamplayer_list(request, pk):
    try:
        team = Team.objects.get(coach_id=pk)
        if team != None:
            myPlayer = Player.objects.filter(team=team.id)
            player_count = myPlayer.count()
        return render(request, 'iplapp/player//myteamplayer_list.html',
                      {'myplayer': myPlayer,
                       'player_count': player_count,
                       'coachid': pk})
    except Team.DoesNotExist:
        return render(request, 'iplapp/player/myteamplayer_list.html',
                      {'myplayer': None,
                       'player_count': 0,
                       'coachid': pk
                       })

@login_required
def player_new(request, coachid):
    if request.method == 'POST':
        form = PlayerFormEditAdd(request.POST)
        if form.is_valid():
            try:
                team = Team.objects.get(coach_id=coachid)
                if team != None:
                    player = form.save(commit=False)
                    player.created_date = timezone.now()
                    player.team = team
                    player.save()

                    players = Player.objects.filter(team=team.id)
                    player_count = players.count()
                return render(request, 'iplapp/player/myteamplayer_list.html',
                              {'myplayer': players,
                               'player_count': player_count,
                               'coachid': coachid})
            except Team.DoesNotExist:
                return render(request, 'iplapp/player/myteamplayer_list.html',
                              {'myplayer': None,
                               'player_count': 0,
                               'coachid': coachid
                               })
    else:
        #edit player
        form = PlayerFormEditAdd()
    return render(request, 'iplapp/player/player_edit.html', {'form': form})

@login_required
def player_edit(request, pk, coachid):
    player = get_object_or_404(Player, pk=pk)
    if request.method == "POST":
        #update
        form = PlayerFormEditAdd(request.POST, instance=player)
        if form.is_valid():
            team = Team.objects.get(coach_id=coachid)
            if team != None:
                player = form.save(commit=False)
                player.updated_date = timezone.now()
                player.team = team
                player.save()

                players = Player.objects.filter(team=team.id)
                player_count = players.count()
            #players = Player.objects.filter(created_date__lte=timezone.now())
            return render(request, 'iplapp/player/myteamplayer_list.html',
                          {'myplayer': players,
                           'player_count': player_count,
                           'coachid': coachid})
    else:
        # edit
        form = PlayerFormEditAdd(instance = player)
    return render(request, 'iplapp/player/player_edit.html', {'form': form})

@login_required
def player_delete(request, pk, coachid):
    player = get_object_or_404(Player, pk=pk)
    player.eligibility_status = 'ineligible'
    player.save()
    team = Team.objects.get(coach_id=coachid)
    if team != None:
        players = Player.objects.filter(team=team.id)
        player_count = players.count()
    return render(request, 'iplapp/player/myteamplayer_list.html',
                            {'myplayer': players,
                            'player_count': player_count,
                             'coachid': coachid})

##### Homepage Views
##############################
def home(request):
    matches_sch = Match.objects.filter(match_status='scheduled').order_by('match_day', 'match_start_time')[:3]
    matches_full = Match.objects.filter(match_status='full_time').order_by('-match_day', '-match_start_time')[:3]
    matches_live = Match.objects.filter(match_status='in_progress')
    team_live = Team.objects.filter(id=1)
    player_run_scorer = PlayerStats.objects.values('player__first_name', 'player__last_name',
                                                  'player__team__team_short_name', 'player__team__team_logo_url')\
                                                .annotate(total_run=Sum('run'))\
                                                .order_by('-total_run')[:5]
    teams = Team.objects.filter(created_date__lte=timezone.now()).order_by('-team_point')
    return render(request, 'home.html', {'matches_sch': matches_sch,
                                              'matches_full': matches_full,
                                              'matches_live': matches_live,
                                              'team_logo_live': team_live,
                                              'player_run_scorer': player_run_scorer,
                                              'teams': teams})

def refresh_point_table(request):
    team_list = Team.objects.filter(created_date__lte=timezone.now())
    for team in team_list:
        home_won = Match.objects.filter(home_team=team, match_status='full_time').filter(
            home_team_score__gt=F('guest_team_score')).count()
        home_tie = Match.objects.filter(home_team=team, match_status='full_time').filter(
            home_team_score=F('guest_team_score')).count()
        guest_won = Match.objects.filter(guest_team=team, match_status='full_time').filter(
            home_team_score__lt=F('guest_team_score')).count()
        guest_tie = Match.objects.filter(guest_team=team, match_status='full_time').filter(
            home_team_score=F('guest_team_score')).count()
        team.team_point = home_won * 3 + home_tie + guest_won * 3 + guest_tie
        team.save()
    return redirect('iplapp:home')

# Match Views
#############
def match_list(request, pk):
    if(pk == 1):
        match_list = Match.objects.filter(created_date__lte=timezone.now()).order_by('match_day', 'match_start_time')
        list_type = 'all'
    elif(pk == 2):
        match_list = Match.objects.filter(match_status='in_progress').order_by('match_day', 'match_start_time')
        list_type = 'in_progress'
    elif(pk == 3):
        match_list = Match.objects.filter(match_status='full_time').order_by('match_day', 'match_start_time')
        list_type = 'finished'
    elif(pk == 4):
        match_list = Match.objects.filter(match_status='scheduled').order_by('match_day', 'match_start_time')
        list_type = 'scheduled'
    else:
        match_list = Match.objects.filter(created_date__lte=timezone.now()).order_by('match_day', 'match_start_time')
        list_type = 'all'
    return render(request, 'iplapp/match/match_list.html', {'match_list': match_list,
                                                          'list_type': list_type})

def match_referee(request, pk):
    match_list = Match.objects.filter(match_referee=pk).filter(Q(match_status='in_progress') | Q(match_status='scheduled')).order_by('match_day', 'match_start_time')
    return render(request, 'iplapp/match/referee_dashboard.html', {'match_list': match_list, })

def match_detail(request, pk):
    #Getting details
    match = get_object_or_404(Match, pk=pk)
    home_team = match.home_team
    guest_team = match.guest_team
    home_goals = PlayerStats.objects.filter(match=match, team=home_team)
    guest_goals = PlayerStats.objects.filter(match=match, team=guest_team)

    #Getting page forms
    home_goal_form = PlayerStatsForm(team_id=home_team.id)
    guest_goal_form = PlayerStatsForm(team_id=guest_team.id)

    match_status_form = MatchStatusForm()
    match_status_form.fields['match_status'].initial = match.match_status
    match_status_form.fields['referee_comments'].initial = match.referee_comments

    #Handling POST requests
    if request.method == "POST" and 'home_goal_submit' in request.POST:
        home_goal_form = PlayerStatsForm(request.POST, team_id=home_team.id)
        if home_goal_form.is_valid():
            goal = home_goal_form.save(commit=False)
            goal.created_date = timezone.now()
            goal.match = get_object_or_404(Match, pk=pk)
            goal.team = home_team
            goal.save()
            match.home_team_score = home_goals.count()
            match.save()
    elif request.method == "POST" and 'guest_goal_submit' in request.POST:
        guest_goal_form = PlayerStatsForm(request.POST, team_id=guest_team.id)
        if guest_goal_form.is_valid():
            goal = guest_goal_form.save(commit=False)
            goal.created_date = timezone.now()
            goal.match = get_object_or_404(Match, pk=pk)
            goal.team = guest_team
            goal.save()
            match.guest_team_score = guest_goals.count()
            match.save()

    elif request.method == "POST" and 'update_match_status' in request.POST:
        match_status_form = MatchStatusForm(request.POST, instance=match)
        if match_status_form.is_valid():
            print('>>>>Match Status Valid')
            match = match_status_form.save(commit=False)
            match.home_team_score = home_goals.count()
            match.guest_team_score = guest_goals.count()
            print('>>Home Goals - ', home_goals.count())
            print('>>Guest Goals - ', guest_goals.count())
            match.save()
            #Updating point table for both teams
            if(match.match_status=='full_time'):
                team = home_team
                home_won = Match.objects.filter(home_team=team, match_status='full_time').filter(home_team_score__gt=F('guest_team_score')).count()
                home_tie = Match.objects.filter(home_team=team, match_status='full_time').filter(home_team_score=F('guest_team_score')).count()
                guest_won = Match.objects.filter(guest_team=team, match_status='full_time').filter(home_team_score__lt=F('guest_team_score')).count()
                guest_tie = Match.objects.filter(guest_team=team, match_status='full_time').filter(home_team_score=F('guest_team_score')).count()
                team.team_point = home_won*3 + home_tie + guest_won*3 + guest_tie
                team.save()
                team = guest_team
                home_won = Match.objects.filter(home_team=team, match_status='full_time').filter(home_team_score__gt=F('guest_team_score')).count()
                home_tie = Match.objects.filter(home_team=team, match_status='full_time').filter(home_team_score=F('guest_team_score')).count()
                guest_won = Match.objects.filter(guest_team=team, match_status='full_time').filter(home_team_score__lt=F('guest_team_score')).count()
                guest_tie = Match.objects.filter(guest_team=team, match_status='full_time').filter(home_team_score=F('guest_team_score')).count()
                team.team_point = home_won * 3 + home_tie + guest_won * 3 + guest_tie
                team.save()

    return render(request, 'iplapp/match/match_detail.html', {'match': match,
                                                'home_team': home_team,
                                                'guest_team': guest_team,
                                                'home_goals': home_goals,
                                                'guest_goals': guest_goals,
                                                'match_status_form': match_status_form,
                                                'home_goal_form': home_goal_form,
                                                'guest_goal_form': guest_goal_form,
                                                'today': timezone.now()})


@login_required
def match_edit(request, pk):
    match = get_object_or_404(Match, pk=pk)
    if request.method == "POST":
        #update
        form = MatchForm(request.POST, instance=match)
        if form.is_valid():
            match = form.save(commit=False)
            match.updated_date = timezone.now()
            match.save()
            match_list = Match.objects.filter(created_date__lte=timezone.now())
            return render(request, 'iplapp/match/match_list.html', {'match_list': match_list,
                                                              'list_type': 'all'})
    else:
        # edit
        form = MatchForm(instance=match)
    return render(request, 'iplapp/match/match_edit.html', {'form': form})

@login_required
def match_new(request):
    if request.method == "POST":
        #update
        form = MatchForm(request.POST)
        if form.is_valid():
            match = form.save(commit=False)
            match.created_date = timezone.now()
            match.save()
            match_list = Match.objects.filter(created_date__lte=timezone.now())
            return render(request, 'iplapp/match/match_list.html', {'match_list': match_list,
                                                              'list_type': 'all'})
    else:
        # edit
        form = MatchForm()
    return render(request, 'iplapp/match/match_edit.html', {'form': form})

@login_required
def match_delete(request, pk):
    match = get_object_or_404(Match, pk=pk)
    match.delete()
    match_list = Match.objects.filter(created_date__lte=timezone.now())
    return render(request, 'iplapp/match/match_list.html', {'match_list': match_list,
                                                      'list_type': 'all'})

#Role Views
###########
@login_required
def role_list(request):
    user_list = User.objects.all()
    role_list = IPLrole.objects.filter(registered='No')
    return render(request, 'iplapp/role/roles.html', {'roles_list': role_list, 'user_list': user_list,
                                                 'sent': 'False', 'Emailid': 'None'})


@login_required
def assign_role(request):
    #form = AssignRoleForm(request.POST or None)
    user_list = User.objects.all()
    role_list = IPLrole.objects.filter(registered='No')
    if request.method == "POST":
        form = AssignRoleForm(request.POST)
        if form.is_valid():
            assignrole = form.save(commit=False)
            assignrole.save()
            cd = form.cleaned_data
            host_name = request.get_host()
            host_url = request.get_full_path()
            final_url = 'http://' + host_name + "/register"
           # post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = 'Activate your IPL account as ' + cd['role']
            message = "Hi!\n You are selected as '" + cd['role'] +"' from IPL administration." \
                    "\nPlease register at IPL using below link \n " +final_url + "\n Thanks ! IPL"

            send_mail(subject, message, 'indianpremierleague202208@gmail.com', [cd['receiver_email']])
            return render(request, 'iplapp/role/roles.html', {'roles_list': role_list, 'user_list': user_list,
                                                         'sent': 'True', 'emailid': cd['receiver_email']})

    else:
        form = AssignRoleForm()
    return render(request, 'iplapp/role/assign_roles.html', {'form': form})

@login_required
def delete_role(request, pk):
    iplrole = get_object_or_404(IPLrole, pk=pk)
    iplrole.delete()
    return redirect('iplapp:role_list')

#Session Views
##############
def login_view(request):
    title = "Login"
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(username=username, password=password)
        login(request, user)
        return redirect('iplapp:home')
    return render(request, 'registration/login.html', {'form': form, 'title': title})


def register_view(request):
    title = 'Register'
    form = UserRegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        password = form.cleaned_data.get('password')
        email = form.cleaned_data.get('email')
        user.set_password(password)
        user.is_staff = True
        user.save()

        iplrole = IPLrole.objects.get(receiver_email=email)
        group_name = iplrole.role
        print('group_name---', group_name)
        my_group = Group.objects.get(name=group_name)
        print('my_group--', my_group)
        my_group.user_set.add(user)

        iplrole.registered = 'Yes'
        iplrole.save()
        new_user = authenticate(username=user.username, password=password)
        login(request, new_user)
        return redirect('iplapp:home')


    context = {
        "form": form,
        "title": title
    }
    return render(request, "registration/login.html", context)


def register_success(request):
    return render(request, 'registration/success.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('iplapp:home')


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        print('form--', form)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            print('form-valid-', form)
            #return redirect('ipl_app:home')
            return HttpResponseRedirect('success/')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
        #print('form-new-', form)
    return render(request, 'registration/change_password.html', {'form': form})


@login_required
def password_success(request):
    return render(request, 'registration/change_password_success.html')

