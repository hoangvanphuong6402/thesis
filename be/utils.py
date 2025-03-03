from lib import *
from config import *

def make_datapath_list(phase="train"):
    rootpath = classify_data_path
    target_path = osp.join(rootpath + '\\' + phase + '/**/*.jpg')
    path_list = []
    for path in glob.glob(target_path):
        path_list.append(path)
    return path_list

def train_model(net, dataloader_dict, criterior, optimizer, num_epochs, save_location):
    min_val_loss = 1000
    max_val_acc = 0
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    net.to(device)
    torch.backends.cudnn.benchmark = True
    for epoch in range(num_epochs):
        print("Epoch {}/{}".format(epoch+1, num_epochs))

        for phase in ["train", "val"]:
            if phase == "train":
                net.train()

            else:
                net.eval()

            epoch_loss = 0.0
            epoch_corrects = 0

            if (epoch == 0) and (phase == "train"):
                continue
            for inputs, labels in tqdm(dataloader_dict[phase]):
                inputs = inputs.to(device)
                labels = labels.to(device)
                optimizer.zero_grad()
                with torch.set_grad_enabled(phase == "train"):
                    outputs = net(inputs)
                    loss = criterior(outputs, labels)
                    _, preds = torch.max(outputs, 1)

                    if phase == "train":
                        loss.backward()
                        optimizer.step()
                    epoch_loss += loss.item() * inputs.size(0)
                    epoch_corrects += torch.sum(preds == labels.data)
            epoch_loss = epoch_loss / len(dataloader_dict[phase].dataset)
            epoch_acc = epoch_corrects.double() / len(dataloader_dict[phase].dataset)
            if phase == "val":
                if epoch_loss < min_val_loss:
                    min_val_loss = epoch_loss
                if epoch_acc > max_val_acc:
                    max_val_acc = epoch_acc
            print("{} Loss: {:.4f} Acc: {:.4f}".format(phase, epoch_loss, epoch_acc))
    torch.save(net.state_dict(), save_location)
    # return min_val_loss.numpy()[0], max_val_acc.numpy()[0]
    return float(min_val_loss), float(max_val_acc)
            
def param_to_update(model):
    param_to_update = []

    update_param = ["classifier.2.weight", "classifier.2.bias", "base_model.norm.weight", "base_model.norm.bias", "base_model.head.weight", "base_model.head.bias"]

    for name, param in model.named_parameters():
        if name in update_param:
            param.requires_grad = True
        else:
            param.requires_grad = False
    total_blocks = len(model.base_model.blocks)
            
    # unfreeze n_blocks last attention blocks
    n_blocks = 6
    for i in range(total_blocks - n_blocks, total_blocks):
        block = model.base_model.blocks[i]
        for p in block.parameters():
            p.requires_grad = True
            param_to_update.append(p)
        
        return param_to_update
            
def load_model(net, path):
    # load_weights = torch.load(path)
    load_weights = torch.load(path,  map_location={"cuda:0": "cpu"})   # load cpu
    net.load_state_dict(load_weights)
    return net

def delete_folder(folder_path):
    try:
        shutil.rmtree(folder_path)
        print(f"Folder '{folder_path}' deleted successfully.")
    except OSError as error:
        print(f"Error deleting folder: {error}")
        
def extract_file(file_path, root_path):
    with ZipFile(file_path, 'r') as zObject: 
        zObject.extractall(path=root_path) 
    os.remove(file_path)

def split_classify_data(root_path, fraction=0.8):
    label_list = os.listdir(root_path)
    for label in label_list:
        if not os.path.exists(os.path.join(f'{classify_data_path}\\train', label)):
            os.makedirs(os.path.join(f'{classify_data_path}\\train', label))
        if not os.path.exists(os.path.join(f'{classify_data_path}\\val', label)):
            os.makedirs(os.path.join(f'{classify_data_path}\\val', label))
        label_path = os.path.join(root_path, label)
        file_list = os.listdir(label_path)
        random.shuffle(file_list)
        train_file = file_list[:int(len(file_list)*fraction)]
        val_file = file_list[int(len(file_list)*fraction):]
        for file in train_file:
            src_file_path = os.path.join(label_path, file)
            des_file_path = os.path.join(os.path.join(f'{classify_data_path}\\train', label), file)
            shutil.move(src_file_path, des_file_path)
        for file in val_file:
            src_file_path = os.path.join(label_path, file)
            des_file_path = os.path.join(os.path.join(f'{classify_data_path}\\val', label), file)
            shutil.move(src_file_path, des_file_path)
    return label_list
            
def delete_folder(folder_path):
    try:
        shutil.rmtree(folder_path)
        print(f"Folder '{folder_path}' deleted successfully.")
    except OSError as error:
        print(f"Error deleting folder: {error}")
        
def split_detect_data(root_path, fraction):
    os.makedirs(f"{detect_data_path}\\train\\images")
    os.makedirs(f"{detect_data_path}\\valid\\images")
    os.makedirs(f"{detect_data_path}\\test\\images")
    os.makedirs(f"{detect_data_path}\\train\\labels")
    os.makedirs(f"{detect_data_path}\\valid\\labels")
    os.makedirs(f"{detect_data_path}\\test\\labels")
    folder_list = os.listdir(root_path)
    for folder in folder_list:
        if folder == "images":
            folder_path = os.path.join(root_path, folder)
            file_list = os.listdir(folder_path)
            random.shuffle(file_list)
            train_files = file_list[:int(len(file_list)*0.7)]
            val_files = file_list[int(len(file_list)*0.7):int(len(file_list)*0.9)]
            test_files = file_list[int(len(file_list)*0.9):]
            for file in train_files:
                src_file_path = os.path.join(folder_path, file)
                des_file_path = os.path.join(f"{detect_data_path}\\train\\images", file)
                shutil.move(src_file_path, des_file_path)
            for file in val_files:
                src_file_path = os.path.join(folder_path, file)
                des_file_path = os.path.join(f"{detect_data_path}\\valid\\images", file)
                shutil.move(src_file_path, des_file_path)
            for file in test_files:
                src_file_path = os.path.join(folder_path, file)
                des_file_path = os.path.join(f"{detect_data_path}\\test\\images", file)
                shutil.move(src_file_path, des_file_path)
        
        if folder == "labels":
            folder_path = os.path.join(root_path, folder)
            file_list = os.listdir(folder_path)
            for file in file_list:
                file_name = os.path.basename(file)
                splitted_name = os.path.splitext(file_name)

                if (f"{splitted_name[0]}.png" in train_files) or (f"{splitted_name[0]}.jpg" in train_files) or (f"{splitted_name[0]}.jpeg" in train_files):
                    src_file_path = os.path.join(folder_path, file)
                    des_file_path = os.path.join(f"{detect_data_path}\\train\\labels", file)
                    shutil.move(src_file_path, des_file_path)
                if (f"{splitted_name[0]}.png" in val_files) or (f"{splitted_name[0]}.jpg" in val_files) or (f"{splitted_name[0]}.jpeg" in val_files):
                    src_file_path = os.path.join(folder_path, file)
                    des_file_path = os.path.join(f"{detect_data_path}\\valid\\labels", file)
                    shutil.move(src_file_path, des_file_path)
                if (f"{splitted_name[0]}.png" in test_files) or (f"{splitted_name[0]}.jpg" in test_files) or (f"{splitted_name[0]}.jpeg" in test_files):
                    src_file_path = os.path.join(folder_path, file)
                    des_file_path = os.path.join(f"{detect_data_path}\\test\\labels", file)
                    shutil.move(src_file_path, des_file_path)
    
def create_yaml(file_path, class_name):    
    ab_path = os.path.abspath(file_path)
    data = {
        "names": class_name,
        "nc": len(class_name),
        "test": f"{ab_path}\\test\\images",
        "train": f"{ab_path}\\train\\images",
        "val": f"{ab_path}\\valid\\images"
    }

    with open(f"{file_path}\\data.yaml", "w") as file:
        yaml.dump(data, file, default_flow_style=False)
    return f"{file_path}\\data.yaml"

# def save_model_to_db(user_id, model, collection, model_name, task):
#     #pickling the model
#     pickled_model = pickle.dumps(model)
    
#     #saving model to mongoDB
#     info = collection.insert_one({'user_id': user_id, 'file': pickled_model, 'name': model_name, 'task': task})
#     # print(info.inserted_id, ' saved with this id successfully!')
    
#     details = {
#         'inserted_id':info.inserted_id,
#         'model_name':model_name,
#     }
    
#     return details

def save_model_to_db(db, user_id, model, collection, model_name, task, label):
    fs = GridFS(db)
    #pickling the model
    pickled_model = pickle.dumps(model)
    
    # Use GridFS to store the pickled model
    file_id = fs.put(pickled_model)
    
    #saving model to mongoDB
    info = collection.insert_one({'user_id': user_id, 'file': pickled_model, 'name': model_name, 'task': task, 'label': label})
    # print(info.inserted_id, ' saved with this id successfully!')
    
    details = {
        'inserted_id':info.inserted_id,
        'model_name':model_name,
        'label': label,
    }
    
    return details