from lib import *
from config import *
from utils import *
from image_transform import *
from CustomModel import *


class Predictor():
    def __init__(self, a=5):
        self.a = a
        
    def predict_max(self, output):
        output_ = output.detach().numpy()
        max_id = np.argmax(output.detach().numpy())
        for i in range(0, len(output_[0])):
            output_[0][i] = abs(output_[0][i])
        prob = output_[0][max_id]/sum(output_[0])
        return max_id, prob
    
predictor = Predictor()

def predict(img, net):
    model = CustomModel(base_model=net, num_classes=4)
    model.eval()
    
    # load weights
    if net == "hf_hub:timm/vit_large_patch16_224.augreg_in21k_ft_in1k":
        model_weights = load_model(model, save_path_large_model)
    elif net == "hf_hub:timm/vit_base_patch16_224.augreg_in21k_ft_in1k":
        model_weights = load_model(model, save_path_base_model)
    elif net == "hf_hub:timm/vit_small_patch16_224.augreg_in21k_ft_in1k":
        model_weights = load_model(model, save_path_small_model)
    elif net == "vgg16":
        model_weights = load_model(model, save_path_vgg16_model)
        
    transform = ImageTransform(resize, mean, std)
    img = transform(img, phase="test")
    img = img.unsqueeze_(0) # (channel, height, width) -> (batch, channel, height, width)
    
    #predict
    output = model_weights(img)
    id, prob = predictor.predict_max(output)
    return id, prob
