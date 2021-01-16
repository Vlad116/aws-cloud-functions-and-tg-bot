import boto3
import os
# import telepot
import requests

s3 = boto3.client('s3')

BOT_TOKEN = os.environ['TELEG_BOT_TOKEN']
URL = "https://api.telegram.org/bot{}/".format(BOT_TOKEN)
CHAT_ID = os.environ['CHAT_ID']


# Триггер на загрузку фото в target-bucket (вырезанное лицо)
# --------------- Main handler ------------------
def lambda_handler(event, context):
    # Get the object from the event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    photo_key = event['Records'][0]['s3']['object']['key']

    try:
        FACE_IMG_URL = "https://" + bucket_name + "s3.eu-central-1.amazonaws.com/" + photo_key

        url = URL + "sendMessage?text={}&chat_id={}".format("Кто это?", CHAT_ID)
        requests.get(url)

        send_photo_url = URL + "sendPhoto?photo={}&chat_id={}".format(FACE_IMG_URL, CHAT_ID)
        requests.get(send_photo_url)

        # response = bot.getUpdates()
        # pprint(response)
        # [
        # {'message': {
        # 'chat': {
        #   'first_name': 'Nick',
        #   'id': 999999999,
        #   'type': 'private'
        #  },
        # 'date': 1465283242,
        # 'from': {
        #   'first_name': 'Nick',
        #   'id': 999999999},
        #   'message_id': 10772,
        #   'text': 'Hello'
        #  },
        # 'update_id': 100000000
        # }
        # ]
        #
        # chat_id = response.message.chat.id

        # bot = telepot.Bot(BOT_TOKEN)
        # bot.sendMessage(CHAT_ID, "Кто это?")
        # bot.sendPhoto(CHAT_ID, FACE_IMG_URL)

        return
    except Exception as e:
        print(e)
        print("Error processing object {} from bucket {}. ".format(photo_key, bucket_name))
        raise e