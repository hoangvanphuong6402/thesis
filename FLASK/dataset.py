from lib import *
from config import *

class MyDataset(data.Dataset):
    def __init__(self, file_list, transform=None, phase='train', label_list=["chay_la", "dom_mat", "kham_la", "khoe_manh", "thoi_re"]):
        self.file_list = file_list
        self.transform = transform
        self.phase = phase
        self.label_list = label_list

    def __len__(self):
        return len(self.file_list)

    def __getitem__(self, index):
        img_path = self.file_list[index]
        img = Image.open(img_path)
        img_transformed = self.transform(img, self.phase)
        if self.phase == "train":
            splitted_path = img_path.split('\\')  
            label = splitted_path[splitted_path.index("train") + 1]
        elif self.phase == "val":
            splitted_path = img_path.split('\\')  
            label = splitted_path[splitted_path.index("val") + 1]
        label = self.label_list.index(str(label))
        return img_transformed, label