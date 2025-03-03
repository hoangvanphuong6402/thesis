import os
import glob
import os.path as osp
import numpy as np
import json
from PIL import Image
from tqdm import tqdm
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import torch.optim as optim
import torch.utils.data as data
import torchvision
from torchvision import models, transforms
import timm
from ultralytics import YOLO
from zipfile import ZipFile 
import shutil
from werkzeug.utils import secure_filename
import uuid  
import yaml
import random
import pickle
from gridfs import GridFS
import cv2