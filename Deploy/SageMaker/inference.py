import argparse
import json
import os
import pickle
import sys
import sagemaker_containers
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.utils.data
from PIL import Image
import io
from torchvision import models
import logging
import base64
from base64 import decodestring
LOG = logging.getLogger()

def _npy_loads(data):
    """
    Deserializes npy-formatted bytes into a numpy array
    """
    stream = io.BytesIO(data)
    return np.load(stream, allow_pickle=True)

def _npy_dumps(data):
    """
    Serialized a numpy array into a stream of npy-formatted bytes.
    """
    buffer = io.BytesIO()
    np.save(buffer, data)
    return buffer.getvalue()

def model_fn(model_dir):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    LOG.info('Loading the model.')
    LOG.info(f'model_dir {model_dir}')
    with open(os.path.join(model_dir, 'lego_model.pth'), 'rb') as f:
        model = torch.load(f, map_location=device)
    LOG.info('Done loading model')
    return model

def input_fn(request_body, content_type = 'application/x-npy'):
    LOG.info('Deserializing the input data.')
    LOG.info(f"request body: {request_body}")
    LOG.info(f"content type: {content_type}")
    
    if content_type == 'application/x-npy':
        LOG.info(f"inside content type")
        data = _npy_loads(request_body)
        LOG.info(f"npy_loads: {data}")
        image64 = base64.b64decode(data)
        img2 = np.asarray(Image.open(io.BytesIO(image64)))
        imgdata = Image.fromarray(img2.astype('uint8'),'RGB')
        imgrbg = np.asarray(imgdata)
        img_input = torch.from_numpy(imgrbg)
        LOG.info(f'before retuen img_input {img_input.shape}')
        return img_input.type('torch.DoubleTensor')
    LOG.info('Exception')
    raise Exception('Requested unsupported ContentType in content_type: ' + content_type)
    
def predict_fn(input_data, model):
    LOG.info('Generating prediction based on input parameters.')
    if torch.cuda.is_available(): #input_data = input_data.view(1, 3, 224, 224).cuda()
        input_data = input_data.view(-1, 3, 200, 200).cuda()
    else :#input_data = input_data.view(1, 3, 224, 224)
        input_data = input_data.view(-1, 3, 200, 200)
    with torch.no_grad():
        model = model.double()
        model.eval()
        out = model(input_data.double())
        ps = torch.exp(out)
    return ps


    
def output_fn(prediction_output, accept = 'application/json'):
    LOG.info(f'Serializing the generated output. {prediction_output}')
    LOG.info(f'type of output {type(prediction_output)}')
    topk, topclass = prediction_output.topk(1, dim=1)
    classes = {
        0: '2357 Brick corner 1x2x2',
        1: '3003 Brick 2x2',
        2: '3004 Brick 1x2',
        3: '3005 Brick 1x1',
        4: '3022 Plate 2x2',
        5: '3023 Plate 1x2',
        6: '3024 Plate 1x1',
        7: '3040 Roof Tile 1x2x45deg',
        8: '3069 Flat Tile 1x2',
        9: '3673 Peg 2M',
        10: '3713 Bush for Cross Axle',
        11: '3713 Bush for Cross Axle',
        12: '6632 Technic Lever 3M',
        13: '11214 Bush 3M friction with Cross axle',
        14: '18651 Cross Axle 2M with Snap friction',
        15: '32123 half Bush'
    }
    pred = {'prediction': classes[topclass.numpy()[0][0]], 'score': topk.numpy()[0][0]}
    LOG.info(f'Adding pediction: {pred}')
    LOG.info(f'Output accept: {accept}')

    if accept == 'application/x-npy':
        LOG.info('inside accept')
        return _npy_dumps(pred), 'application/x-npy'
    elif accept == 'application/json':
        return json.dumps(pred)
    else:
        raise Exception(f'Requested unsupported ContentType in Accept:{accept}')