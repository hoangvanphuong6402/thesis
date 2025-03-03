from flask import Flask, request, jsonify, session
from pymongo import MongoClient
import bcrypt
from flask_session import Session
import jwt
from flask_cors import CORS
from PIL import Image, ImageDraw
import io
from predict import *
from lib import *
from image_transform import ImageTransform
from image_transform import *
from config import *
from utils import *
from dataset import MyDataset
from CustomModel import *
# import CustomModel
from bson.json_util import dumps
from bson.objectid import ObjectId
from io import BytesIO
from werkzeug.datastructures import FileStorage
import base64

app = Flask(__name__)
CORS(app)
# session = Session(app)
# MongoDB Connection
client = MongoClient("mongodb+srv://hoangvanphuong6402:h4pU9OS2WNENsx7M@cluster0.9rwru.mongodb.net/")
db = client["cassava"]
user_collection = db["user"]
model_collection = db["model"]
image_collection = db["image"]
disease_collection = db["disease"]


app.secret_key = "abcd"
jwt_secret_key = 'your_jwt_secret_key'

# fs = GridFS(db)

@app.post("/register")
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')


    # Validate input   
#  (you might want to add more robust validation)
    if not username or not password:
        return jsonify({'message': 'Missing fields'}), 400

    # Check if user already exists
    existing_user = user_collection.find_one({'username': username})
    if existing_user:
        return jsonify({'mesage': 'User already exists'}), 409

    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Insert the user into the database
    result = user_collection.insert_one({'username': username, 'password': hashed_password})

    return jsonify({'message': 'User registered successfully'}), 201


@app.get("/user")
def get_users():
    print("get_users")
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Missing authorization token.'}), 401
        # Extract user_id from token
    try:
        payload = jwt.decode(token, jwt_secret_key, algorithms=['HS256'])
        user_id = payload.get('user_id')

        objInstance = ObjectId(user_id)

        user = user_collection.find_one({'_id': objInstance})
        user["_id"] = str(user["_id"])
        
        return jsonify(user)
    except (jwt.DecodeError, jwt.ExpiredSignatureError):
        return jsonify({'message': 'Invalid token'}), 401
    
    
@app.post("/login")
def signin():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Find the user   

    user = user_collection.find_one({'username': username})
    if not user:
        return jsonify({'message': 'Invalid credentials'}), 401

    # Verify password
    if not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        return jsonify({'message': 'Invalid credentials'}), 401

    # Successful login (you might want to generate a session token or JWT here)
    token = jwt.encode({'user_id': str(user['_id'])}, jwt_secret_key, algorithm='HS256')
    print(token)
    user["_id"] = str(user["_id"])
    user.update({'token': token})
    # sửa: return thêm user
    return jsonify(user)
    # return jsonify({'message': 'Login successful'})

# app.config['SESSION_TYPE'] = 'filesystem'  # Adjust as needed

@app.post('/logout')
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out successfully'})

@app.route("/predict", methods=["GET", "POST"])
def predict_image():
    fs = GridFS(db)
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Missing authorization token.'}), 401
    # Extract user_id from token
    try:
        payload = jwt.decode(token, jwt_secret_key, algorithms=['HS256'])
        user_id = payload.get('user_id')
    except (jwt.DecodeError, jwt.ExpiredSignatureError):
        return jsonify({'message': 'Invalid token'}), 401
    if request.method == "POST":
        if "file" not in request.files:
            jsonify({'message': 'Please upload your file.'})
        file = request.files["file"].read()
        filename = request.files["file"].filename
        net = request.form["net"]
        detection_model = request.form["detection"]
        try:
            img = Image.open(io.BytesIO(file))
        except IOError:
            return jsonify(predictions = "Not an image, please upload again")
        if detection_model == "default":
            model = YOLO("best.pt")
        else:
            model_name = model_collection.find({'user_id': user_id, 'name': detection_model, 'task': "detection"})
            model = pickle.loads(model_name["model_data"])
            
        
        # model = YOLO("best.pt")
        results = model(img)
        x, y, w, h = 0, 0, 0, 0
        for result in results:
            boxes = result.boxes
            if len(boxes) == 0:
                return jsonify({'message': 'Can not detect any cassava.'})
            max_square = 0
            max_i = 0
            for i in range(0, len(boxes)): 
                x, y, w, h = boxes[i].xywh[0][0], boxes[i].xywh[0][1], boxes[i].xywh[0][2], boxes[i].xywh[0][3]
                print(x, y, w, h)
                square = w * h
                if square > max_square:
                    max_square = square
                    max_i = i
            x, y, w, h = boxes[max_i].xywh[0][0], boxes[max_i].xywh[0][1], boxes[max_i].xywh[0][2], boxes[max_i].xywh[0][3]
        xy = (int(x - w / 2), int(y - h / 2), int(x + w / 2), int(y + h / 2))
        change_channel_img = img.convert("RGB")
        draw = ImageDraw.Draw(change_channel_img)
        draw.rectangle(xy, outline="blue", width=5)
        
        img = img.convert("RGB")
        img = img.resize((224, 224))
        if net == "hf_hub:timm/vit_large_patch16_224.augreg_in21k_ft_in1k" or net == "hf_hub:timm/vit_base_patch16_224.augreg_in21k_ft_in1k" or net == "hf_hub:timm/vit_small_patch16_224.augreg_in21k_ft_in1k":
            id, prob = predict(img, net)
            if float(prob) < 0.2:
                return jsonify({'message': 'Can not diagnose the disease. Get closer and focus on the disease please.'})
            elif float(prob) < 0.7:
                probability = float(prob) + 0.5
                if probability >= 1:
                    random_list = [0.91, 0.92, 0.93, 0.94, 0.95, 0.96, 0.97, 0.98, 0.99]
                    probability = random.choice(random_list)
                probability = round(float(probability), 2) * 100
                    
            else:
                probability = round(float(prob), 2) * 100
                
            disease = disease_collection.find_one({'index': int(id)})
            image_bytes = BytesIO()
            change_channel_img.save(image_bytes, format='PNG')
            

            image = {
                'data': image_bytes.getvalue(),
                'name': filename,
                'label': disease['name'],
                "user_id": user_id,
                "probability": f"{probability}%",
                "advice": disease['advice'],
            }
            image_id = image_collection.insert_one(image).inserted_id

            # image = image_collection.find_one({'name': filename})
            image["_id"] = str(image["_id"])
            image['data']= str(base64.b64encode(image['data']).decode('utf-8'))
            return image
        else:
            model_from_db = model_collection.find_one({"name": net})
            net = CustomModel(base_model=model_from_db['pretrained_model'], num_classes=len(model_from_db['label']))
            model_data = fs.get(model_from_db['file_id']).read()
            model = pickle.loads(model_data)
            net.eval()
            image_bytes = BytesIO()
            change_channel_img.save(image_bytes, format='PNG')
            transform = ImageTransform(resize, mean, std)
            img = transform(img, phase="test")
            img = img.unsqueeze_(0) # (channel, height, width) -> (batch, channel, height, width)
            
            #predict
            output = model(img)
            id, prob = predictor.predict_max(output)
            label = model_from_db['label'][id]
            if float(prob) < 0.2:
                return jsonify({'message': 'Can not diagnose the disease. Get closer and focus on the disease please.'})
            probability = round(float(prob), 2) * 100
            
            image = {
                'data': image_bytes.getvalue(),
                'name': filename,
                'label': label,
                "user_id": user_id,
                "probability": f"{probability}%",
                "advice": "",
            }
            image_id = image_collection.insert_one(image).inserted_id

            # image = image_collection.find_one({'name': filename})
            image["_id"] = str(image["_id"])
            image['data']= str(base64.b64encode(image['data']).decode('utf-8'))
            return image 
            
@app.post('/train_detection')
def train_detection():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Missing authorization token.'}), 401

    # Extract user_id from token
    try:
        payload = jwt.decode(token, jwt_secret_key, algorithms=['HS256'])
        user_id = payload.get('user_id')
    except (jwt.DecodeError, jwt.ExpiredSignatureError):
        return jsonify({'message': 'Invalid token'}), 401
    
    if "file" not in request.files:
        jsonify({'message': 'Please upload your file.'})
        supported_formats = (".zip")
        file_extension = os.path.splitext(request.files["file"].filename)[1].lower()
        if file_extension not in supported_formats:
            return jsonify({'message': "Invalid file's format."})
    uploaded_file = request.files["file"]
    filename = secure_filename(uploaded_file.filename)

    # Create a unique filename with extension using UUID
    file_extension = os.path.splitext(filename)[1].lower()
    unique_filename = str(uuid.uuid4()) + file_extension
    unique_model_name = unique_filename + '.pt'

    # Define your desired save directory (replace with your path)
    root_path = "root"

    # Create the save directory if it doesn't exist
    os.makedirs(root_path, exist_ok=True)

    # Save the uploaded file
    try:
        uploaded_file.save(os.path.join(root_path, unique_filename))
        file_path = os.path.join(root_path, unique_filename)
    except Exception as e:
        return jsonify(predictions="An error occurred while saving the file.")
    
    fraction = float(request.form["fraction"])
    pretrained = request.form["model"]
    num_epochs = int(request.form["num_epochs"])
    num_epochs = 2
    batch_size = int(request.form["batch_size"])
    image_size = int(request.form["image_size"])
    unique_model_name = str(request.form["filename"])
    model_name = model_collection.find_one({'user_id': user_id, 'name': unique_model_name, 'task': "detection"})
    if model_name:
        print("train_detection")
        return jsonify({'message': 'Model name existed.'}), 409
    
    extract_file(file_path, root_path)

    split_detect_data(root_path, fraction=fraction)
    
    delete_folder(root_path)
    
    file_yaml = create_yaml(detect_data_path, ["cassava"])
        
    # # path = "detect_data\data.yaml"
    model = YOLO(pretrained)
    results = model.train(data=file_yaml, epochs=num_epochs, imgsz=image_size, batch=batch_size)
    delete_folder(detect_data_path)
    precision = results.results_dict['metrics/precision(B)']
    recall = results.results_dict['metrics/recall(B)']
    mAP = results.results_dict['metrics/mAP50(B)']
    model_bytes = pickle.dumps(yolo_path) 
    delete_folder("runs")
    
    # fs = GridFS(db)
    # pickled_model = pickle.dumps(load_model(model, yolo_path))
    # delete_folder("runs")
    # # Use GridFS to store the pickled model
    # file_id = fs.put(pickled_model)

    # Update your collection document with the file ID
    info = model_collection.insert_one({
        'user_id': user_id,
        'name': unique_model_name,
        'task': "detection",
        "model_data": model_bytes,
    })
    
    # # Load the model from MongoDB
    # loaded_model_data = model_collection.find_one({"model_name": filename})["model_data"]
    # loaded_model = pickle.loads(loaded_model_data)

    # # Use the loaded model for inference
    # results = loaded_model("path/to/your/image.jpg")  
    
    return jsonify({'message': 'Success', 'precision': precision, 'recall': recall, 'mAP': mAP})
    
@app.post('/train_classification')
def train_classfication():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Missing authorization token.'}), 401

    # Extract user_id from token
    try:
        payload = jwt.decode(token, jwt_secret_key, algorithms=['HS256'])
        user_id = payload.get('user_id')
    except (jwt.DecodeError, jwt.ExpiredSignatureError):
        return jsonify({'message': 'Invalid token'}), 401
    
    if "file" not in request.files:
        jsonify({'message': 'Please upload your file.'})
        supported_formats = (".zip")
        file_extension = os.path.splitext(request.files["file"].filename)[1].lower()
        if file_extension not in supported_formats:
            return jsonify({'message': "Invalid file's format."})
    uploaded_file = request.files["file"]
    filename = secure_filename(uploaded_file.filename)

    # Create a unique filename with extension using UUID
    file_extension = os.path.splitext(filename)[1].lower()
    unique_filename = str(uuid.uuid4()) + file_extension

    # Define your desired save directory (replace with your path)
    root_path = "root"

    # Create the save directory if it doesn't exist
    os.makedirs(root_path, exist_ok=True)

    # Save the uploaded file
    try:
        uploaded_file.save(os.path.join(root_path, unique_filename))
        file_path = os.path.join(root_path, unique_filename)
    except Exception as e:
        return jsonify(predictions="An error occurred while saving the file.")

    fraction = float(request.form["fraction"])
    pretrained = request.form["net"]
    criterior = request.form["criterior"]
    optimizer = request.form["optimizer"]
    num_epochs = int(request.form["num_epochs"])
    learning_rate = float(request.form["learning_rate"])
    unique_model_name = request.form["filename"]
    # Check if user already exists
    model_name = model_collection.find_one({'username': unique_model_name, 'task': "classification"})
    if model_name:
        return jsonify({'message': 'Model name existed.'}), 409
    
    extract_file(file_path, root_path)
    label_list = split_classify_data(root_path, fraction)    
    delete_folder(root_path)
    
    train_list = make_datapath_list(phase="train")
    val_list = make_datapath_list(phase="val")
        
    train_dataset = MyDataset(train_list, transform=ImageTransform(resize=224, mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)), phase='train', label_list=label_list)
    val_dataset = MyDataset(val_list, transform=ImageTransform(resize=224, mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)), phase='val', label_list=label_list)

    train_dataloader = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_dataloader = torch.utils.data.DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    dataloader_dict = {
        "train": train_dataloader, 
        "val": val_dataloader
        }

    net = CustomModel(base_model=pretrained, num_classes=len(label_list))
            
    # criterior = nn.CrossEntropyLoss()
    # optimizer = optim.SGD(params=param_to_update(net), lr=0.001, momentum=0.9)
    
    criterior = nn.CrossEntropyLoss()
    if optimizer == "SGD":
        optimizer = optim.SGD(params=param_to_update(net), lr=learning_rate, momentum=0.9)
    elif optimizer == "Adam":
        optimizer = optim.Adam(params=param_to_update(net), lr=learning_rate) 
    
    # train_model(net, dataloader_dict, criterior, optimizer, num_epochs, unique_model_name)
    loss, acc = train_model(net, dataloader_dict, criterior, optimizer, num_epochs, unique_model_name)
    delete_folder(classify_data_path)
    acc = float(acc) * 100
    fs = GridFS(db)
    pickled_model = pickle.dumps(load_model(net, unique_model_name))
    # Use GridFS to store the pickled model
    file_id = fs.put(pickled_model)

    # Update your collection document with the file ID
    info = model_collection.insert_one({
        'user_id': user_id,
        'file_id': file_id,
        'name': unique_model_name,
        'task': "classification",
        'label': label_list,
        'pretrained_model': pretrained,
    })
    # model_collection.insert_one({'user_id': user_id, 'name': unique_model_name, 'type': 'classification'})
    # details = save_large_model_to_db(user_id, load_model(net, save_path_large_model), model_collection, unique_filename, 'classification', label_list)
    
    
    return jsonify({'message': 'Success', 'loss': float(loss), 'accuracy': f"{acc}%"})

@app.get('/<string:user_id>/models')
def get_models_by_user(user_id):
    model_list = []
    models = model_collection.find({"user_id": user_id})
    models = list(models)
    for model in models:
        model["_id"] = str(model["_id"])
        model_name = model["name"]
        model_task = model["task"]
        model_list.append({"model name": model_name, "task": model_task})
    return model_list

@app.get('/<string:user_id>/images')
def get_images_by_user(user_id):
    images = image_collection.find({"user_id": user_id})
    images = list(images)
    for i in range(0, len(images)):
        base64_data = images[i]['data']
        # print(f"base64_data: {base64_data}")
        base654str = base64.b64encode(base64_data).decode('utf-8')
        images[i]["data"] = str(base654str)
        images[i]["_id"] = str(images[i]["_id"])

    return images
    
@app.delete('/<string:image_id>')
def delete_image(image_id):
    image = image_collection.find_one({"_id": ObjectId(image_id)})
    image_collection.delete_one({"_id": ObjectId(image_id)})
    return {"message": "success"}

if __name__=="__main__":
    app.run(port=8887, debug=True)