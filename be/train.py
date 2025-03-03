from lib import *
from image_transform import ImageTransform
from config import *
from utils import *
from dataset import MyDataset

def main():
    train_list = make_datapath_list(phase="train")
    val_list = make_datapath_list(phase="val")
        
    train_dataset = MyDataset(train_list, transform=ImageTransform(resize=224, mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)), phase='train')
    val_dataset = MyDataset(val_list, transform=ImageTransform(resize=224, mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)), phase='val')

    train_dataloader = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_dataloader = torch.utils.data.DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    dataloader_dict = {
        "train": train_dataloader, 
        "val": val_dataloader
        }

    net = timm.create_model("hf_hub:timm/vit_large_patch14_clip_224.openai_ft_in12k_in1k", pretrained=True)
    # in_features = net.classifier.in_features
    net.classifier = nn.Linear(in_features=1000, out_features=5)
            
    criterior = nn.CrossEntropyLoss()
    optimizer = optim.SGD(params=param_to_update(net), lr=0.001, momentum=0.9)

    train_model(net, dataloader_dict, criterior, optimizer, num_epochs=num_epochs)
    
if __name__ == "__main__":
    main()    