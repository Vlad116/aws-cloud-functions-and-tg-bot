import json
from botocore.vendored import requests
import boto3
import os

dynamodb = boto3.client('dynamodb', region_name='eu-central-1')
BUCKET_NAME = 'cloudphoto-target'
TABLE_NAME = 'photoToFaceTable'
NAMES_TABLE = 'nameToPhotoTable'

BOT_TOKEN= os.environ['TELEG_BOT_TOKEN']
URL = "https://api.telegram.org/bot{}/".format(BOT_TOKEN)
CHAT_ID = os.environ['CHAT_ID']

def send_message(text, chat_id):
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    requests.get(url)

def send_photo(photo_url, chat_id):
    url = URL + "sendPhoto?photo={}&chat_id={}".format(photo_url, chat_id)
    requests.get(url)

def dynamodb_put_item(tableName, photoKey, name):
    response = dynamodb.put_item(
        TableName=tableName,
        Item={
            'Name': {'S': name},
            'PhotoKey': {'S': photoKey}
        }
    )
    print(response)

def lambda_handler(event, context):
    message = json.loads(event['body'])
    chat_id = message['message']['chat']['id']
    name = message['message']['text']
    # photo_key =

    # Добавляем запись в базу данных
    # dynamodb_put_item(TABLE_NAME, photo_key, name)

    # send_message(reply, chat_id)
    return {
        'statusCode': 200
    }