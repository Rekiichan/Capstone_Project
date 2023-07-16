import torch
import sys
import os
# add parent patt to sys.path
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from client.handle_view.client import Client
import pickle
from client.utils.models import create_cnn_model
import copy
from client.utils.const import *
from client.models import TrainInfo
""" 
Input of clients inclule:
1- file.pt from client\Model_from_Server
2- Custom Dict from argprase to config (batch_size,epochs,percentage_of_dataset, mode,dataset_name....)

Output of clients inclule:
1- file.pt from client\Model_Client_update
2- eval_list: Dict from  client\log
 """


""" Start Client """


def client_train():
  DICT_RETURN = {'success':True,'msg':"OK"}
  try:
    train_info_from_db = TrainInfo.objects.filter().first()
    
    data_dir = DATASET_PATH # path of dataset
    batch_size = train_info_from_db.batch
    epochs = train_info_from_db.epoch
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    percentage_of_dataset = train_info_from_db.percentage_of_dataset
    dataset_name = train_info_from_db.dataset_name
    mode = train_info_from_db.mode
    
    # path of model from server
    server_model_path = MODEL_FROM_SERVER 
    # path of model client will save and send to server
    client_model_path = MODEL_SEND_TO_SERVER 
    
    # Initalize client instance
    client = Client(
      data_dir=data_dir,
      batch_size=batch_size,
      epoch=epochs,
      device=device,
      model=None,  # Khởi tạo với None, sẽ được gán sau
      percentage_of_dataset=percentage_of_dataset,
      dataset_name=dataset_name,
      mode=mode,
      server_model_path=server_model_path,
      client_model_path=client_model_path
    )

    # Load data
    trainloader, validloader, num_examples = client.load_datasets()

    # # Model architecture from utils\model.py
    CNNModel = create_cnn_model()
    client.model = copy.deepcopy(CNNModel)

    # Fit model
    client.fit()

    # Evaluate model
    client.evaluate()

    # Save eval_list to a file
    eval_list = client.get_eval_list()
    with open(f'{PATH_SEND_TO_SERVER}/eval_list.pkl', 'wb') as f:
      pickle.dump(eval_list, f)
    return DICT_RETURN 
  except Exception as exc:
    print('triiger exceoption')
    DICT_RETURN['success'] = False
    DICT_RETURN['msg'] = str(exc)
    return DICT_RETURN

