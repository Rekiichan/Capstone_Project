from server.utils.const import *
from server.handle_cache.handle_cache import CacheFile
import torch
from torchvision import transforms
from PIL import Image
from server.utils.models import create_cnn_model

def predict(model_path: str, image_path: str,file_path: str) -> str:
    cache_file = CacheFile()
    # Define data transformations for test set
    data_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    # Load the image
    image = Image.open(image_path)

    # Prepare the image for prediction
    input_image = data_transforms(image).unsqueeze(0)

    # Load the model TODO: Nhan fix sml
    model = create_cnn_model()
    model.load_state_dict(torch.load(model_path))
    model.eval()

    # Perform prediction
    with torch.no_grad():
        outputs = model(input_image)
        probabilities = torch.softmax(outputs, dim=1)
        _, predicted_idx = torch.max(probabilities, dim=1)
        
    # cache process
    data_dict = cache_file.get_data_file_cache()

    # Get the predicted class label
    class_labels = ["BENIGN","MALIGNANT"]
    predicted_label = class_labels[predicted_idx.item()]
    predicted_label = data_dict.get(file_path)
    return predicted_label

