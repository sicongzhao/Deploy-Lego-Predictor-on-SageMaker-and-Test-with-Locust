import json
import boto3
import tempfile
import base64
import io
import numpy as np

# s3://sagemaker-lego/0003.png
def img_to_byte(img):
    with open(img, "rb") as img_file:
        img_byte = base64.b64encode(img_file.read())
    return img_byte
    
def _npy_dumps(data):
    """
    Serialized a numpy array into a stream of npy-formatted bytes.
    """
    buffer = io.BytesIO()
    np.save(buffer, data)
    return buffer.getvalue()

def lambda_handler(event, context):
    s3 = boto3.resource('s3', region_name='us-east-2')
    bucket = s3.Bucket('sagemaker-lego')
    object = bucket.Object('0003.png')
    tmp = tempfile.NamedTemporaryFile()
    
    with open(tmp.name, 'wb') as f:
        object.download_fileobj(f)
        payload = img_to_byte(tmp.name)
        send(_npy_dumps(payload))
    
    # s3 = boto3.client('s3')
    # s3_img = s3.get_object(Bucket='sagemaker-lego', Key='0003.png')
    # print(f's3_img: {s3_img}')
    # s3_img_decode = s3_img['Body'].read()#.decode('utf-8')
    # print(f's3_img_decode: {s3_img_decode}')
    # payload = json.dumps({'url':'https://cdn.britannica.com/30/136130-050-3370E37A/Leopard.jpg'})
    # send(payload)



def send(payload):
    print('start send')
    endpoint_name = "pytorch-inference-2020-04-30-04-19-50-410" # Modify this to your endpoint
    runtime = runtime= boto3.client('runtime.sagemaker')
    response = runtime.invoke_endpoint(EndpointName=endpoint_name, ContentType='application/x-npy', Body=payload)
    print(response['Body'].read())
    print('end send')