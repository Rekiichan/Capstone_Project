from server.models import *
import torch
from typing import List, Dict, Tuple
from server.handle_function.client_on_server import ClientOnServer
import copy

class Server:
    def __init__(self):
        self.clients: List[ClientOnServer] = []
        self.server_model: Dict[str, torch.Tensor] = None
        self.loaded: bool = False
        self.client_num: int = 0
        self.client_weights_ratio: List[float] = []
        self.origin_model: Dict[str, torch.Tensor] = None

    def load_server_model(self, model_path: str):
      if not self.loaded:
        state_dict = torch.load(model_path)
        self.server_model.load_state_dict(state_dict)
        self.origin_model = copy.deepcopy(self.server_model)
        self.loaded = True


    def add_client(self, model_path: str, eval_list_path: str):
        client = ClientOnServer(model_path, eval_list_path)
        self.clients.append(client)
        self.client_num = len(self.clients)

    def __getitem__(self, index: int) -> ClientOnServer:
        return self.clients[index]

    def compute_client_samples_ratio(self) -> List[float]:
        total_samples = sum(client.get_samples() for client in self.clients)
        self.client_weights_ratio = [client.get_samples() / total_samples for client in self.clients]
        return self.client_weights_ratio

    def aggregate(self, models: List[Dict[str, torch.Tensor]]) -> Dict[str, torch.Tensor]:
        with torch.no_grad():
            mode = TrainInfo.objects.filter().first()
            mode = mode.mode
            if mode.lower() == 'fedbn':
                for key in self.server_model.state_dict().keys():
                    if 'bn' not in key:
                        temp = torch.zeros_like(self.server_model.state_dict()[key], dtype=torch.float32)
                        if len(self.client_weights_ratio) > 0:
                            for client_idx in range(self.client_num):    
                                temp += self.client_weights_ratio[client_idx] * models[client_idx][key]
                            self.server_model.state_dict()[key].data.copy_(temp)
            else:
                for key in self.server_model.state_dict().keys():
                    if 'num_batches_tracked' in key:
                        self.server_model.state_dict()[key].data.copy_(self.origin_model[key])
                    else:
                        temp = torch.zeros_like(self.server_model.state_dict()[key])
                        if len(self.client_weights_ratio) > 0:
                            for client_idx in range(self.client_num):
                                temp += self.client_weights_ratio[client_idx] * models[client_idx][key]
                            self.server_model.state_dict()[key].data.copy_(temp) 
        return self.server_model.state_dict()

    def metrics_avg(self) -> Tuple[float, float, float, float]:
        """Compute average metrics from multiple clients."""
        train_loss = 0
        train_accuracy = 0
        test_loss = 0
        test_accuracy = 0
        for client_idx in range(self.client_num):
            eval_list = self.clients[client_idx].get_eval_list()
            if len(self.client_weights_ratio) > 0:
                client_weight = self.client_weights_ratio[client_idx]
            else:
                client_weight = 0
            train_loss += eval_list[0]['train_loss'] * client_weight
            train_accuracy += eval_list[0]['train_accuracy'] * client_weight
            test_loss += eval_list[1]['test_loss'] * client_weight
            test_accuracy += eval_list[1]['test_accuracy'] * client_weight
        return train_loss, train_accuracy, test_loss, test_accuracy

