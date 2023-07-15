from django.urls import path
from . import views

app_name = 'client'

urlpatterns = [
    path('train-request', views.TrainLocal.as_view(), name='index'),
    path('udpate-global-model', views.UpdateGlobalModel.as_view(), name='index'),
]
