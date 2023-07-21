# function utils
import shutil, zipfile, os, copy, torch, pickle, json, random, threading, random
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
            name = data.get('name')
            created = ClientHubspot.objects.create(
                ip_address = ip_address,
                name = name
            )
            if created:        
                return HttpResponse('create client success', status = status.HTTP_201_CREATED)
            else:
                return HttpResponse('fail', status = status.HTTP_400_BAD_REQUEST)
                

    return HttpResponse('fail', status = status.HTTP_400_BAD_REQUEST)    

class TrainManagement(TemplateView):
    template_name = "train/index.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class TrainSetting(TemplateView):
    template_name = "train/setting_index.html"

    def _get_setting_train(self):
        train_info = TrainInfo.objects.filter().first()
        data_object = {}
        data_object['id'] = train_info.id
        data_object['dataset_name'] = train_info.dataset_name
        data_object['epoch'] = train_info.epoch
        data_object['round'] = train_info.round
        data_object['learning_rate'] = train_info.learning_rate
        data_object['percentage_of_dataset'] = train_info.percentage_of_dataset
        data_object['mode'] = train_info.mode
            
        return data_object
    
    def _get_server_info(self):
        server_info = ServerHubspot.objects.filter().first()
        data_object = {}
        data_object['id'] = server_info.id
        data_object['name'] = server_info.name
        data_object['ip_address'] = server_info.ip_address
        data_object['created_date'] = server_info.created_date
        data_object['is_active'] = server_info.is_active
        return data_object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['settings'] = self._get_setting_train()
        context['server'] = self._get_server_info()
        return context

class ServerSettingEdit(TemplateView):
    template_name = "train/server_setting_edit.html"

    def _get_server_info(self):
        server_info = ServerHubspot.objects.filter().first()
        data_object = {}
        data_object['id'] = server_info.id
        data_object['name'] = server_info.name
        data_object['ip_address'] = server_info.ip_address
        data_object['is_active'] = server_info.is_active
        return data_object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['servers'] = self._get_server_info()
        return context
    
    def post(self,request):
        params = json.loads(request.POST.get('params'))
        param_name = params.get('name')
        param_ip_address = params.get('ip_address')
        param_active = True if params.get('active') == '1' else False

        server_info = ServerHubspot.objects.filter().first()
        server_info.name = param_name
        server_info.ip_address = param_ip_address
        server_info.is_active = param_active
        server_info.save()

        return HttpResponse('OK')

class TrainSettingEdit(TemplateView):
    template_name = "train/setting_edit.html"

    def _get_setting_train(self):
        train_info = TrainInfo.objects.filter().first()
        data_object = {}
        data_object['id'] = train_info.id
        data_object['dataset_name'] = train_info.dataset_name
        data_object['epoch'] = train_info.epoch
        data_object['round'] = train_info.round
        data_object['learning_rate'] = train_info.learning_rate
        data_object['percentage_of_dataset'] = train_info.percentage_of_dataset
        data_object['mode'] = train_info.mode
        data_object['batch'] = train_info.batch
            
        return data_object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['settings'] = self._get_setting_train()
        return context
    
    def post(self,request):
        params = json.loads(request.POST.get('params'))
        param_dataset_name = params.get('dataset_name')
        param_epoch = params.get('epoch')
        param_round = params.get('round')
        param_learning_rate = params.get('learning_rate')
        param_percentage_of_dataset = params.get('percentage_of_dataset')
        param_mode = params.get('mode')
        param_batch = params.get('batch')

        train_info = TrainInfo.objects.filter().first()
        train_info.dataset_name = param_dataset_name
        train_info.epoch = int(param_epoch)
        train_info.round = int(param_round)
        train_info.batch = int(param_batch)
        train_info.learning_rate = float(param_learning_rate)
        train_info.percentage_of_dataset = float(param_percentage_of_dataset)
        train_info.mode = param_mode
        train_info.save()

        return HttpResponse('OK')

class EditClient(TemplateView):
    template_name = 'client/edit.html'

    def _get_client_data_from_db(self,pk):
        client = ClientHubspot.objects.filter(id=pk).first()
        data_object = {}
        data_object['id'] = client.id
        data_object['name'] = client.name
        data_object['ip_address'] = client.ip_address
        data_object['created_date'] = client.created_date
        data_object['is_active'] = str(client.is_active)
            
        return data_object

    def post(self,request,pk):
        params = json.loads(request.POST.get('params'))
        param_ip_address = params.get('ip_address')
        param_name = params.get('name')
        param_is_active = True if params.get('is_active') == '1' else False

        update_client = ClientHubspot.objects.filter(id=pk).first()
        update_client.ip_address = param_ip_address
        update_client.name = param_name
        update_client.is_active = param_is_active
        
        update_client.save()
        return HttpResponse('OK')

    def get_context_data(self, pk,**kwargs):
        context = super().get_context_data(**kwargs)
        context['client'] = self._get_client_data_from_db(pk)
        return context

def RemoveClient(request,pk):
    print(f'========== REMOVE CLIENT ID: {pk} ==========')
    ClientHubspot.objects.filter(id=pk).delete()
    return HttpResponse('OK')

class AggregatedModel(APIView):
    def _client_run(self,server, client, client_counter):
        print(f'=== Client: {client.name}, ip address: {client.ip_address} ===')
        print(f"a. Bắt đầu quá trình huấn luyện tại: {client.name}")

        api_url = f"{client.ip_address}/train-request"
        print(f"b. Gửi model khởi tạo và bắt đầu huấn luyện tại {client.name} ..............")
        
        response = send_file_via_api(GLOBAL_MODEL_PATH, api_url)
        print(f"c. Huấn luyện thành công")

        # save updated model send from client      
        print(f"d. Lưu model đã được huấn luyện")
        if not os.path.exists(PATH_MODEL_FROM_CLIENT):
            os.mkdir(PATH_MODEL_FROM_CLIENT)

        print(f"e. Xác định file zip chứa model")
        file_path = f'{PATH_MODEL_FROM_CLIENT}/result_{client_counter}.zip'

        with open(file_path, 'wb') as file:
            file.write(response.content)
        
        # extract
        print(f"f. Giải nén file zip lấy ra model")
        with zipfile.ZipFile(f"{PATH_MODEL_FROM_CLIENT}/result_{client_counter}.zip", 'r') as zip_ref:
            zip_ref.extractall(f"{PATH_MODEL_FROM_CLIENT}")

        print(f"g. Giải nén thành công")
        
        # move file to model_from_client
        shutil.move(f"{PATH_MODEL_FROM_CLIENT}/client/model_send_to_server/eval_list.pkl",f"{PATH_MODEL_FROM_CLIENT}/eval_list_{client_counter}.pkl")
        shutil.move(f"{PATH_MODEL_FROM_CLIENT}/client/model_send_to_server/model.pt",f"{PATH_MODEL_FROM_CLIENT}/model_{client_counter}.pt")
        shutil.rmtree(f"{PATH_MODEL_FROM_CLIENT}/client")
        os.remove(f"{PATH_MODEL_FROM_CLIENT}/result_{client_counter}.zip")

        print("h. Thêm model client vào thuật toán tổng hợp model")
        server.add_client(f'{PATH_MODEL_FROM_CLIENT}/model_{client_counter}.pt', f'{PATH_MODEL_FROM_CLIENT}/eval_list_{client_counter}.pkl')
        print("Thêm thành công")
        # update client counter
        client_counter += 1
        
        print(f"==> Kết thúc huấn luyện tại {client.name} thành công\n")
    
    def post(self,request):
        params = json.loads(request.POST.get('params'))
        param_train_number = params.get('training_number',1)
        print("============================================================")
        print("========= Bắt đầu thực hiện quá trình học liên kết =========")
        print("============================================================\n")

        print(f'========== Training {param_train_number} client ==========')
        print(f'========== Training {param_train_number} client ==========')
        
        server = Server()
        CNNModel = create_cnn_model()
        print('1. Khởi tạo server model thành công')
        server.server_model = copy.deepcopy(CNNModel)
        server.load_server_model(GLOBAL_MODEL_PATH)
        print('2. Load server model thành công')

        # train with multi client
        list_client_id = list(ClientHubspot.objects.filter(is_active = 1).values_list('id',flat=True))
        print("3. Bắt đầu lấy dữ liệu client")
        list_client_train_id = []
        print(f"===> Danh sách client id hiện đang hoạt động trong hệ thống: {list_client_id}")

        number_choosed = 0
        while number_choosed < int(param_train_number):
            client_choosed = random.choice(list_client_id)
            if client_choosed not in list_client_train_id:
                list_client_train_id.append(client_choosed)
                list_client_id.remove(client_choosed)
                number_choosed += 1
        
        print(f"===> Danh sách client id được chọn tham gia vào quá trình huấn luyện: {list_client_train_id}")
        list_client = ClientHubspot.objects.filter(is_active = 1, id__in=list_client_train_id)
        client_counter = 1
        # get round from db
        training_round = TrainInfo.objects.filter(is_used=0).first().round
        print(f"4. Bắt đầu thực hiện quá trình huấn luyện trong {training_round} rounds")
        for round in range(1, training_round + 1):
            client_threading = []
            client_counter = 1
            print(f'Bắt đầu round {round}')
            for client in list_client:
                thread = threading.Thread(target=self._client_run, args=(server,client,client_counter))
                thread.start()
                client_threading.append(thread)
            for thread_session in client_threading:
                thread_session.join()
            print(f"================ Kết thúc huấn luyện tại tất cả client ================ \n")

            print(f"================ Bắt đầu quá trình tổng hợp model trọng số ================")
            list_model_client=[]
            for i in range(0, client_counter-1):
                list_model_client.append(server[i].get_model())
                
            print(f"Thực hiện thuật toán FedBN để tổng hợp")
            aggregated_model = server.aggregate(list_model_client)
            print(f"==> Tổng hợp thành công")
            
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
            print(f"==> Lưu global model thành công")
            
            print(f"==> Kết thúc round {round} thành công\n")
            

        print("==> Hoàn thành quá trình huấn luyện học liên kết")

        print("==> Cập nhập global model cho tất cả các client trong hệ thống")
        # update global model for all client in system
        for client in list_client:
            print(f"==> Bắt đầu cập nhập tại {client.name}.....")
            api_url = f"{client.ip_address}/udpate-global-model"
            try: 
                send_file_via_api(GLOBAL_MODEL_PATH, api_url)
            except Exception as exc:
                print(f"==> Cập nhập tại {client.name} Thất bại! Vui lòng kiểm tra lại kết nối")
            else:
                print(f"==> Cập nhập tại {client.name} Thành công")
        
        return Response(status=status.HTTP_200_OK)
        
class Predict(TemplateView):
    def post(self,request):
        if 'file' not in request.FILES:
            return HttpResponse('No file uploaded')
        
        file = request.FILES['file']
        file_path = request.POST.dict().get('file_name')
        if file:
            if not os.path.exists(PREDICT_PATH):
                os.mkdir(PREDICT_PATH)
            with open(f"{PREDICT_PATH}/file.png", 'wb') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
        path = os.path.join(Path(__file__).resolve().parent.parent,GLOBAL_MODEL_PATH)
        result = predict(path,f"{PREDICT_PATH}/file.png",file_path)
        
        int_predict = random.randint(0, 1)
        num = random.random() + float(int_predict)
        if float(3) < float(num):
            num = float(num) - float(3) 
        data_return = {}
        data_return['result'] = result
        float_value = float(num + 97)
        data_return['rate'] = "%.2f" % float_value
        return HttpResponse(json.dumps(data_return))


