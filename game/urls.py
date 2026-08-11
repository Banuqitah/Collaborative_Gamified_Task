from django.urls import path, re_path

from . import views, settings

urlpatterns = [
    path('', views.index, name='index'),
    re_path(r'room/(?P<room_id>\w+)/$', views.room_state),
    re_path(r'login/(?P<worker_id>\w+)$', views.set_login),
    re_path(r'survey/(?P<worker_id>\w+)$', views.set_survey),
    re_path(r'action/(?P<worker_id>\w+)$', views.send_action),
    re_path(r'avatars$', views.list_avatars),
    re_path(r'pending$', views.get_pending),
]
