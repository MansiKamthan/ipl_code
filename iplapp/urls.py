from django.conf.urls import url
from django.urls import path, re_path
from . import views
from django.conf import settings
from django.views.static import serve
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

app_name = 'iplapp'

urlpatterns = [

    path('', views.home, name="home"),
    re_path(r'^home/$', views.home, name='home'),

    path('register/success/', views.register_success, name='success'),
    path('password/', views.change_password, name='change_password'),
    path('password/success/', views.password_success, name='password_success'),
    # team views
    path('team_list', views.team_list, name='team_list'),
    path('team/<int:pk>/', views.team_detail, name='team_detail'),
    path('team/new/', views.team_new, name='team_new'),
    path('team/<int:pk>/edit/', views.team_edit, name='team_edit'),
    path('team/<int:pk>/delete/', views.team_delete, name='team_delete'),

    #### Matches

    path('point_table_refresh', views.refresh_point_table, name='refresh_point_table'),

    # path('match_list', views.match_list, name='match_list'),
    path('match_list/<int:pk>', views.match_list, name='match_list'),
    path('referee/<int:pk>', views.match_referee, name='match_referee'),
    path('match/<int:pk>/', views.match_detail, name='match_detail'),
    path('match/<int:pk>/edit', views.match_edit, name='match_edit'),
    path('match/new', views.match_new, name='match_new'),
    path('match/<int:pk>/delete/', views.match_delete, name='match_delete'),

    #Player views
    path('player/<int:pk>/', views.player_detail, name='player_detail'),
    path('player_list', views.player_list, name='player_list'),
    path('player_list/<int:pk>', views.myteamplayer_list, name='myteamplayer_list'),
    path('player/<int:coachid>/new/', views.player_new, name='player_new'),
    path('player/<int:pk>/<int:coachid>/edit/', views.player_edit, name='player_edit'),
    path('player/<int:pk>/<int:coachid>/delete/', views.player_delete, name='player_delete'),

    #Roles views
    path('assign_role', views.assign_role, name='assign_role'),
    path('roles', views.role_list, name='role_list'),
    path('roles/delete/<int:pk>/', views.delete_role, name='delete_role'),
]

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    urlpatterns += [
        url(r'^media/(?P<path>.*)$',
            serve, {'document_root': settings.MEDIA_ROOT,})
    ]