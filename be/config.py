from lib import *

# set random seed to be constant
torch.manual_seed(1234)
np.random.seed(1234)
random.seed(1234)

# imagenet config
resize = 224
mean = (0.485, 0.456, 0.406)
std = (0.229, 0.224, 0.225)

batch_size = 128

num_epochs = 2

save_path_large_model = "large_model.pth"
save_path_base_model = "base_model.pth"
save_path_small_model = "small_model.pth"
save_path_vgg16_model = "vgg16_model.pth"
yolo_path = "runs/detect/train/weights/best.pt"

detect_data_path = "detect_data"
classify_data_path = "classify_data"

# torch.backends.cudnn.deterministic = True
# torch.backends.cudnn.benchmark = False