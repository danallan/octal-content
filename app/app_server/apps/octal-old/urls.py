from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView

from views import get_octal_app

urlpatterns = patterns('',
                       url(r'^(?i)concepts/', get_octal_app, name="concepts"),
)
