from django import forms
from .models import Team, Player, Match, PlayerStats, IPLrole
from django.forms.utils import ValidationError
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.core.exceptions import ObjectDoesNotExist
import re

User = get_user_model()

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ('team_name', 'team_logo_url', 'team_short_name', 'active_status', 'team_state', 'coach')

        def __init__(self, *args, **kwargs):
            super(TeamForm, self).__init__(*args, **kwargs)
            # Now set the queryset...
            self.fields['coach'].queryset = User.objects.filter(groups__name='Coach')

class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ('first_name', 'last_name', 'email', 'phone', 'team', 'eligibility_status', 'team_role',
                  'squad_position', 'city', 'state')


class PlayerFormEditAdd(forms.ModelForm):
    class Meta:
        model = Player
        fields = ('first_name', 'last_name', 'email', 'phone', 'eligibility_status', 'team_role',
                  'squad_position', 'city', 'state')


class PlayerStatsForm(forms.ModelForm):
    class Meta:
        model = PlayerStats
        fields = ('player', 'run')

    def __init__(self, *args, **kwargs):
        team_id = kwargs.pop('team_id')
        super(PlayerStatsForm, self).__init__(*args, **kwargs)
        self.fields['player'].queryset = Player.objects.filter(team__id=team_id)


class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ('home_team', 'guest_team', 'match_day', 'match_start_time', 'match_end_time',
                  'ground', 'match_referee', 'match_status', 'referee_comments')

    def __init__(self, *args, **kwargs):
        super(MatchForm, self).__init__(*args, **kwargs)
        # Now set the queryset...
        self.fields['match_referee'].queryset = User.objects.filter(groups__name='Scorer')


class MatchStatusForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ('match_status', 'referee_comments')


class AssignRoleForm(forms.ModelForm):
    class Meta:
        model = IPLrole
        fields = ['role', 'receiver_name', 'receiver_email']

    def clean(self):
        receiver_email = self.cleaned_data['receiver_email']
        try:
            iplrole = IPLrole.objects.filter(receiver_email=receiver_email).order_by('receiver_name').first()
        except ObjectDoesNotExist:
            return receiver_email
        if iplrole:
            raise forms.ValidationError('Email is already taken and assigned to '+iplrole.role+'')


class PasswordResetRequestForm(forms.Form):
    email_or_username = forms.CharField(label=("Email Or Username"), max_length=254)


class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("This user does not exist")
            if not user.check_password(password):
                raise forms.ValidationError("Incorrect Password")
            if not user.is_active:
                raise forms.ValidationError("This user is no longer active")
        return super(UserLoginForm, self).clean(*args, **kwargs)


class UserRegisterForm(forms.ModelForm):
    username = forms.CharField(label='Username', max_length=30)
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Password', widget=forms.PasswordInput())
    password1 = forms.CharField(label='Password (Again)', widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    # password validation
    def clean_password2(self):
        if 'password' in self.cleaned_data:
            password1 = self.cleaned_data['password']
            password2 = self.cleaned_data['password1']
            if password1 == password2:
                return password2
        raise forms.ValidationError('Passwords do not match.')

    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.search(r'^\w+$', username):
            raise forms.ValidationError('Username can only contain alphanumeric characters and the underscore.')
        try:
            User.objects.get(username=username)
        except ObjectDoesNotExist:
            return username
        raise forms.ValidationError('Username is already taken.')

    def clean(self, *args, **kwargs):
        email = self.cleaned_data.get('email')

        try:
            iplrole = IPLrole.objects.get(receiver_email=email)
        except ObjectDoesNotExist:
            iplrole = None

        if iplrole is not None:
            try:
                email_qs = User.objects.get(email=email)
            except ObjectDoesNotExist:
                email_qs = None

            if email_qs is not None:
                usergroup = email_qs.groups.all()
                groupname = ''
                if usergroup:
                    for name in usergroup:
                        groupname = name

                raise forms.ValidationError("This email has already been registered as '"+ str(groupname) +"'")
        else:
            raise forms.ValidationError("You are not authorized to register, please contact IPL administration'")
        return super(UserRegisterForm, self).clean(*args, **kwargs)
