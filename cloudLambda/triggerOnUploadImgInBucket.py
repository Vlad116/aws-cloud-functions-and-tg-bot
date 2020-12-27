import os
import boto3
import io
from io import BytesIO
from PIL import Image
import random
import string

dynamodb = boto3.client('dynamodb', region_name='eu-central-1')
s3 = boto3.client('s3')
rekognition = boto3.client('rekognition', region_name='eu-central-1')

TARGET_BUCKET = 'cloudphoto-target'
TABLE_NAME = 'photoToFaceTable'


# --------------- Helper Functions ------------------
def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


def dynamodb_put_item(tableName, photoKey, faceKey):
    response = dynamodb.put_item(
        TableName=tableName,
        Item={
            'FaceKey': {'S': faceKey},
            'PhotoKey': {'S': photoKey}
        }
    )
    print(response)


# --------------- Main handler ------------------
def lambda_handler(event, context):
    # Get the object from the event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    photo_key = event['Records'][0]['s3']['object']['key']

    try:
        file_byte_string = s3.get_object(Bucket=bucket_name, Key=photo_key)['Body'].read()
        image = Image.open(BytesIO(file_byte_string))

        response = rekognition.detect_faces(
            Image={
                'S3Object': {
                    'Bucket': bucket_name,
                    'Name': photo_key,
                }
            }
        )

        all_faces = response['FaceDetails']

        # Initialize list object
        boxes = []

        # Get image diameters
        image_width = image.size[0]
        image_height = image.size[1]

        # Crop face from image
        for face in all_faces:
            # достаем координаты рамки
            box = face['BoundingBox']

            x1 = int(box['Left'] * image_width) * 0.9
            y1 = int(box['Top'] * image_height) * 0.9
            x2 = int(box['Left'] * image_width + box['Width'] * image_width) * 1.10
            y2 = int(box['Top'] * image_height + box['Height'] * image_height) * 1.10

            # вырезанное лицо
            image_crop = image.crop((x1, y1, x2, y2))

            # загрузка лица в target bucket (cloudphoto-faces)
            stream = io.BytesIO()
            image_crop.save(stream, format="JPEG")
            image_crop_binary = stream.getvalue()

            # генерируем ключ для лица
            face_key = photo_key.split('.')[0] + "_" + "face" + "_" + get_random_string(6) + '.' + photo_key.split('.')[
                1]
            print("target key: " + face_key)

            # добавляем новый обьект с вырезанным лицом в target-bucket
            s3.put_object(Bucket=TARGET_BUCKET,
                          Key=face_key,
                          ACL='public-read',
                          Body=image_crop_binary)

            # Добавляем запись в базу данных
            dynamodb_put_item(TABLE_NAME, photo_key, face_key)

        print(response)
        return response
    except Exception as e:
        print(e)
        print("Error processing object {} from bucket {}. ".format(photo_key, bucket_name))
        raise e