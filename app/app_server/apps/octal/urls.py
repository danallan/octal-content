from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView

from apps.octal import views

urlpatterns = patterns('',
                       url(r'^(?i)concepts/', views.get_octal_app, name="concepts"),
                       url(r'^exercise/([^/]*)$', views.handle_exercise_request, name='getexercise'),
                       url(r'^attempt/(?P<attempt>[^/]*)/(?P<correct>[01])$', views.handle_exercise_attempt, name='addattempt'),
                       url(r'^knowledge/([^/]*)$', views.handle_knowledge_request, name='getknowledge'),
                      )
