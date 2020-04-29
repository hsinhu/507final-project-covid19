from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

app_name='finalcore'

urlpatterns = [
    path('wordcases', views.WorldCasesView.as_view(),name = 'word_case'),
    path('us-state', views.USStateView.as_view(),name = 'us_state'),
    path('us-county', views.USCountyView.as_view(),name = 'us_county'),
    # path('us-projection', views.USProjection.as_view(),name = 'us_projection'),
]