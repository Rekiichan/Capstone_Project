# function utils
import shutil, zipfile, os, copy, torch, pickle, json
from pathlib import Path

# django template lib
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView

# API lib
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# server function import
from server.models import *
from server.utils.const import *
from server.handle_function.server import Server
from server.handle_function.server_running import predict
from server.handle_function.handle_view import send_file_via_api
from server.utils.models import create_cnn_model

class Login(TemplateView):
    template_name = "auth/login.html"

class Home(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class ClientManagement(TemplateView):
    template_name = 'client/list.html'

    def _get_client_data(self):
        list_client = []
        list_client_objects = ClientHubspot.objects.filter(is_deleted=0)
        for client in list_client_objects:
            data_object = {}
            data_object['id'] = client.id
            data_object['name'] = client.name
            data_object['ip_address'] = client.ip_address
            data_object['port'] = client.port
            data_object['created_date'] = client.created_date
            data_object['is_active'] = client.is_active

            list_client.append(data_object)
            
        return list_client

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_client'] = self._get_client_data()
        return context


def AddClient(request):
    if request.method == 'GET':
        return render(request, "client/add.html")

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_new_client':
            data = json.loads(request.POST.get('params'))
            ip_address = data.get('ip_address')
            port = data.get('port')
            name = data.get('name')
            created = ClientHubspot.objects.create(
                ip_address = ip_address,
                port = port,
                name = name
            )
            if created:        
                return HttpResponse('create client success', status = status.HTTP_201_CREATED)
            else:
                return HttpResponse('fail', status = status.HTTP_400_BAD_REQUEST)
                

    return HttpResponse('fail', status = status.HTTP_400_BAD_REQUEST)    

class EditClient(TemplateView):
    template_name = 'client/edit.html'

    def _get_client_data_from_db(self,pk):
        client = ClientHubspot.objects.filter(id=pk).first()
        data_object = {}
        data_object['id'] = client.id
        data_object['name'] = client.name
        data_object['ip_address'] = client.ip_address
        data_object['port'] = client.port
        data_object['created_date'] = client.created_date
        data_object['is_active'] = str(client.is_active)
            
        return data_object

    def post(self,request,pk):
        params = json.loads(request.POST.get('params'))
        print(type(params))
        param_ip_address = params.get('ip_address')
        param_port = params.get('port')
        param_name = params.get('name')
        param_is_active = True if params.get('is_active') == '1' else False

        update_client = ClientHubspot.objects.filter(id=pk).first()
        update_client.ip_address = param_ip_address
        update_client.port = param_port
        update_client.name = param_name
        update_client.is_active = param_is_active
        
        update_client.save()
        return HttpResponse('OK')

    def get_context_data(self, pk,**kwargs):
        context = super().get_context_data(**kwargs)
        context['client'] = self._get_client_data_from_db(pk)
        return context

def RemoveClient(request,pk):
    ClientHubspot.objects.filter(id=pk).delete()
    return HttpResponse('OK')

class AggregatedModel(APIView):
    def post(self,request):
        server = Server()
        CNNModel = create_cnn_model()
        server.server_model = copy.deepcopy(CNNModel)
        server.load_server_model(GLOBAL_MODEL_PATH)

        # train with multi client
        list_client = ClientHubspot.objects.filter(is_active = 1)
        client_counter = 1

        # get round from db
        training_round = TrainInfo.objects.filter(is_used=0).first().round
        for round in range(1, training_round + 1):
            for client in list_client:
                api_url = 'http://' + client.ip_address + ":" + client.port + '/train-request'
                response = send_file_via_api(GLOBAL_MODEL_PATH, api_url)
 
                # save updated model send from client               
                if not os.path.exists(PATH_MODEL_FROM_CLIENT):
                    os.mkdir(PATH_MODEL_FROM_CLIENT)
                file_path = f'{PATH_MODEL_FROM_CLIENT}/result_{client_counter}.zip'
                    
                with open(file_path, 'wb') as file:
                    file.write(response.content)
                
                # extract
                with zipfile.ZipFile(f"{PATH_MODEL_FROM_CLIENT}/result_{client_counter}.zip", 'r') as zip_ref:
                    zip_ref.extractall(f"{PATH_MODEL_FROM_CLIENT}")
                
                # move file to model_from_client
                shutil.move(f"{PATH_MODEL_FROM_CLIENT}/client/model_send_to_server/eval_list.pkl",f"{PATH_MODEL_FROM_CLIENT}/eval_list_{client_counter}.pkl")
                shutil.move(f"{PATH_MODEL_FROM_CLIENT}/client/model_send_to_server/model.pt",f"{PATH_MODEL_FROM_CLIENT}/model_{client_counter}.pt")
                shutil.rmtree(f"{PATH_MODEL_FROM_CLIENT}/client")
                os.remove(f"{PATH_MODEL_FROM_CLIENT}/result_{client_counter}.zip")

                server.add_client(f'{PATH_MODEL_FROM_CLIENT}/model_{client_counter}.pt', f'{PATH_MODEL_FROM_CLIENT}/eval_list_{client_counter}.pkl')

                # update client counter
                client_counter += 1

            # deo thay dung`
            # eval_list = []
            # for i in range(0, client_counter):
            #     eval_list.append(server[i].get_eval_list())

            list_model_client=[]
            for i in range(0, client_counter-1):
                list_model_client.append(server[i].get_model())
                
            aggregated_model = server.aggregate(list_model_client)
            
            # Compute average metrics
            train_loss, train_accuracy, test_loss, test_accuracy = server.metrics_avg()

            log_dict = {
                'fl_round': training_round,
                'training_loss_per_epoch': train_loss,
                'validation_loss_per_epoch': train_accuracy,
                'training_accuracy_per_epoch': test_loss,
                'validation_accuracy_per_epoch': test_accuracy,
            }

            log_round_path = f'server/log/log_dict_round_{round}'
            if not os.path.exists(log_round_path):
                if not os.path.exists(LOG_PATH):
                    os.mkdir(LOG_PATH)
            else:
                shutil.rmtree(LOG_PATH)
                os.mkdir(LOG_PATH)
            os.mkdir(log_round_path)
                
            log_file_path = f"server/log/log_dict_round_{round}/log.pkl"
            with open(log_file_path, 'wb') as f:
                pickle.dump(log_dict, f)

            # Save global model
            torch.save(aggregated_model, GLOBAL_MODEL_PATH)
            print(f"Global model saved to global_model.pt at round {round}")

        # update global model for all client in system
        for client in list_client:
            api_url = 'http://' + client.ip_address + ":" + client.port + '/udpate-global-model'
            response = send_file_via_api(GLOBAL_MODEL_PATH, api_url)
        
        return Response(status=status.HTTP_200_OK)
        
class Predict(APIView):
    def post(self,request):
        if 'file' not in request.FILES:
            return Response(data='No file uploaded.',status=status.HTTP_400_BAD_REQUEST)
        
        file = request.FILES['file']
        if file:
            if not os.path.exists(PREDICT_PATH):
                os.mkdir(PREDICT_PATH)
            with open(f"{PREDICT_PATH}/file.png", 'wb') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
        path = os.path.join(Path(__file__).resolve().parent.parent,GLOBAL_MODEL_PATH)
        result = predict(path,f"{PREDICT_PATH}/file.png")
        return Response(data=result,status=status.HTTP_200_OK)


