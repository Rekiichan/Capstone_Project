from django.urls import path
from . import views

app_name = 'server'

urlpatterns = [
    path('', views.Home.as_view(), name='index'),

    path('login', views.Login.as_view(), name='login'),

    # client ClientManagement
    path('client', views.AddClient, name='client_index'),
    path('client/add', views.AddClient, name='add_client'),
    path('client/edit/<pk>', views.EditClient, name='edit_client'),
    path('client/detail/<pk>', views.DetailClient, name='detail_client'),
    path('client/remove/<pk>', views.RemoveClient, name='remove_client'),

    # train
    path('server-train',views.AggregatedModel.as_view(), name='server_train'),
    path('predict',views.Predict.as_view(),name='predict'),
]
