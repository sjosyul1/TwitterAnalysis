from django.conf.urls import url
from . import views


urlpatterns=[
    #url(r'^s', views.index, name='index'),
    url(r'^$', views.HomeView.as_view(), name='home'),
]
