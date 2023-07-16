from django.urls import path
from . import views

app_name = 'server'

urlpatterns = [
    path('', views.Home.as_view(), name='index'),

    path('login', views.Login.as_view(), name='login'),

    # client ClientManagement
    path('client', views.ClientManagement.as_view(), name='client_index'),
    path('client/add', views.AddClient, name='add_client'),
    path('client/edit/<pk>', views.EditClient.as_view(), name='edit_client'),
    path('client/remove/<pk>', views.RemoveClient, name='remove_client'),

    # train
    path('train',views.TrainManagement.as_view(), name='train_index'),
    path('train-setting',views.TrainSetting.as_view(), name='train_setting_index'),
    path('train-setting-edit',views.TrainSettingEdit.as_view(), name='train_setting_edit'),
    path('server-train',views.AggregatedModel.as_view(), name='server_train'),
    path('predict',views.Predict.as_view(),name='predict'),
]
