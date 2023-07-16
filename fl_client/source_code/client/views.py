import os
import zipfile
import requests
from pathlib import Path
from django.http import FileResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from client.handle_view.client_work import client_train
from client.utils.const import *
from client.models import *
from client.handle_view.predict import predict

def get_url_server_center_info():
  server_center = ServerHubspot.objects.filter().first()
  if server_center:
    url = 'http://' + server_center.ip_address +":" +server_center.port

def send_file_via_api(file_path, api_url):
  with open(file_path, 'rb') as file:
    files = {'file': file}
    response = requests.post(api_url, files=files)
    return response

class TrainLocal(APIView):
  def post(self, request):
    # nhan file trong so tu server center
    if 'file' not in request.FILES:
      return Response(data='No file uploaded.',status=status.HTTP_400_BAD_REQUEST)
    
    file = request.FILES['file']
    if file:
      if not os.path.exists(PATH_FROM_SERVER):
        os.mkdir(PATH_FROM_SERVER)
      with open(MODEL_FROM_SERVER, 'wb') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    
    try:
      client_train()
    except Exception as exc:
      return Response(data=str(exc),status=status.HTTP_400_BAD_REQUEST)
    else:
      if not os.path.exists(PATH_SEND_TO_SERVER):
        os.mkdir(PATH_SEND_TO_SERVER)
      with zipfile.ZipFile(ZIP_SEND_TO_SERVER,mode="a") as archive:
        archive.write(f"{PATH_SEND_TO_SERVER}/eval_list.pkl")
        archive.write(f"{PATH_SEND_TO_SERVER}/model.pt")

      response = FileResponse(open(ZIP_SEND_TO_SERVER, 'rb'), as_attachment=True)
      return response

class UpdateGlobalModel(APIView):
  def post(self,request):
    # nhan file trong so tu server center
    if 'file' not in request.FILES:
      return Response(data='No file uploaded.',status=status.HTTP_400_BAD_REQUEST)

    file = request.FILES['file']
    if file:
      if not os.path.exists('client/global_model'):
        os.mkdir('client/global_model')
      with open(GLOBAL_MODEL_PATH, 'wb') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
      return Response(status=status.HTTP_200_OK)
    else:
      return Response(status=status.HTTP_400_BAD_REQUEST)
      
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
    model_predict_global = os.path.join(Path(__file__).resolve().parent.parent,GLOBAL_MODEL_PATH)
    result = predict(model_predict_global,f"{PREDICT_PATH}/file.png")
    return Response(data=result,status=status.HTTP_200_OK)


    
 
