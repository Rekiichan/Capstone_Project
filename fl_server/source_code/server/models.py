from django.db import models

class ServerHubspot(models.Model):
    name = models.CharField(verbose_name='name', max_length=150)
    ip_address = models.CharField(verbose_name='ip_address', max_length=200)
    port = models.CharField(verbose_name='port', max_length=10)
    created_date = models.DateField(verbose_name='created_date', auto_now_add=True)
    is_deleted = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'server_center'
    
class TrainInfo(models.Model):
    epoch = models.IntegerField(verbose_name='epoch', max_length=50, default=0, blank=True,null=True)
    batch = models.IntegerField(verbose_name='batch', max_length=50, default=0, blank=True,null=True)
    round = models.IntegerField(verbose_name='round', max_length=50, default=0, blank=True,null=True)
    learning_rate = models.FloatField(verbose_name='learning_rate', max_length=50, default=0, blank=True,null=True)
    percentage_of_dataset = models.FloatField(verbose_name='percentage_of_dataset', max_length=50, default=0, blank=True,null=True)
    mode = models.CharField(verbose_name='mode', max_length=50, blank=True,null=True)
    dataset_name = models.CharField(verbose_name='dataset_name', max_length=50, blank=True,null=True)
    is_used = models.BooleanField(default=True)
    
    class Meta: 
        db_table = 'train_info'

class ClientHubspot(models.Model):
    name = models.CharField(verbose_name='name', max_length=150)
    ip_address = models.CharField(verbose_name='ip_address', max_length=200)
    port = models.CharField(verbose_name='port', max_length=10)
    created_date = models.DateField(verbose_name='created_date', auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'client_hubspot'
