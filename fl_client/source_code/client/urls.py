from django.urls import path
from . import views

app_name = 'client'

urlpatterns = [
    path('train-request', views.TrainLocal.as_view(), name='train_request'),
    path('udpate-global-model', views.UpdateGlobalModel.as_view(), name='update_global_model'),
    path('predict', views.Predict.as_view(), name='predict'),
]
