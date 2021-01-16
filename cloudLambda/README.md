## Cоздание триггера в AWS Lambda на загрузку фото, который будет вырезать лица 

### AWS Configure:
```
aws configure [--profile profile-name]
```

### Создание двух bucket'ов (первый для загрузки фоторграфий, второй для хранения вырезанных из фотографий лиц)
```
// source bucket (cloudphoto-source)
aws s3api create-bucket --bucket cloudphoto-source --region eu-central-1

// target bucket (cloudphoto-target)
aws s3api create-bucket --bucket cloudphoto-target --region eu-central-1
```

### Создание таблицы в Amazon DynamoDB
```
aws dynamodb create-table --table-name photoToFaceTable --attribute-definitions AttributeName=PhotoKey,AttributeType=S AttributeName=FaceKey,AttributeType=S --key-schema AttributeName=FaceKey,KeyType=HASH AttributeName=PhotoKey,KeyType=RANGE --provisioned-throughput ReadCapacityUnits=10,WriteCapacityUnits=5 --region eu-central-1
```

### Создание роли исполнения
```
$ aws iam create-role --role-name  uploadingTriggerRekognition  --assume-role-policy-document file://trust-policy.json
```
Пример trust-policy.json
```
{
  "Version": "2012-10-17",
  "Statement": {
      "Effect": "Allow",
      "Principal": {"Service": "lambda.amazonaws.com"},
      "Action": "sts:AssumeRole"
  }
}
```

Put-role-policy 
```
aws iam put-role-policy \
  --role-name uploadingTriggerRekognition \
  --policy-name rolePolicyForUplTriggerRekognition \
  --policy-document file://access-policy.json
```

Пример access-policy.json
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "BatchOperationsLambdaPolicy",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:GetObjectVersion",
                "s3:PutObject",
                "lambda:InvokeFunction"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:GetObjectAcl"
            ],
            "Resource": [
                "arn:aws:s3:::cloudphoto-source/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:PutObjectAcl",
                "s3:GetObject",
                "s3:GetObjectAcl",
                "s3:DeleteObject"
            ],
            "Resource": [
                "arn:aws:s3:::cloudphoto-target/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:Get*",
                "dynamodb:Query",
                "dynamodb:Scan",
                "dynamodb:Delete*",
                "dynamodb:Update*",
                "dynamodb:PutItem"
            ],
            "Resource": [
                "*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "rekognition:IndexFaces",
                "rekognition:DetectFaces",
                "rekognition:ListFaces",
                "rekognition:SearchFaces"
            ],
            "Resource": "*"
        }
    ]
}
```
или
```
$ aws iam create-role --role-name uploadingTriggerRekognition  --assume-role-policy-document '{"Version": "2012-10-17","Statement": [{ "Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"}]}'
$ aws iam attach-role-policy --role-name uploadingTriggerRekognition  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
$ aws iam attach-role-policy --role-name uploadingTriggerRekognition  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonRekognitionFullAccess
$ aws iam attach-role-policy --role-name uploadingTriggerRekognition  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonDynamoDBFullAccess
$ aws iam attach-role-policy --role-name uploadingTriggerRekognition  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonS3FullAccess
$ aws iam attach-role-policy --role-name uploadingTriggerRekognition  --policy-arn arn:aws:iam::aws:policy/service-role/IAMFullAccess
```

### Создание AWS cloud9 окружения:
```
aws cloud9 create-environment-ec2 --name cloudphoto-env --description "Environment for itiscloud course." --instance-type t2.micro --subnet-id subnet-1fab8aEX --automatic-stop-time-minutes 60 --owner-arn arn:aws:iam::123456789012:user/MyDemoUser
Output:
{
  "environmentId": "8a34f51ce1e04a08882f1e811bd706EX"
}
```
Далее подключаемся к созданному окружения и работаем в нем. 
(Решает проблему с добавлением библиотеки Pillow)

### Cоздание функции Python с помощью виртуальной среды
#### Создайте виртуальную среду.
```
~/my-function$ virtualenv myvenv
```
#### Активируйте среду.
```
~/my-function$ source myvenv/bin/activate
```
#### Установите библиотеки с помощью pip.
```
(myvenv) ~/my-function$ pip install Pillow
```
#### Деактивировать виртуальную среду.
```
(myvenv) ~/my-function$ deactivate
```
#### Создайте пакет развертывания с установленными библиотеками в корне.
```
~/my-function$ cd myvenv/lib/python3.7/site-packages
~/my-function/myvenv/lib/python3.7/site-packages$ zip -r trigger-deployment-package.zip .
```
#### Заметка
Библиотека может появиться в site-packages или dist-packages 
и в первой папке lib или lib64. 

Вы можете использовать pip show команду для поиска определенного пакета.
#### Добавьте файлы кода функции в корень вашего пакета развертывания.

```
~/my-function/myvenv/lib/python3.7/site-packages$ cd ../../../../
~/my-function$ zip -g trigger-deployment-package.zip triggerOnUploadImgInBucket.py
```

#### После выполнения этого шага у вас должна получиться следующая структура каталогов:
```
trigger-deployment-package.zip$
  │ triggerOnUploadImgInBucket.py
  │ __pycache__
  │ certifi/ 
  │ certifi-2020.6.20.dist-info/ 
  │ chardet/ 
  │ chardet-3.0.4.dist-info/ 
  ...
```

Используйте префикс fileb: // для загрузки пакета развертывания двоичного файла .zip в Lambda и обновления кода функции.
```
aws lambda create-function --function-name triggerOnUpload \
--zip-file fileb://trigger-deployment-package.zip \
--handler triggerOnUploadImgInBucket.lambda_handler \
--runtime python3.7 \
--role arn:aws:iam::123456789012(свой id):role/uploadingTriggerRekognition
```

###  Добавить разрешения в политику функции
```
$ aws lambda add-permission --function-name triggerOnUpload 
--statement-id triggerOnUploadInv3245 
--action "lambda:InvokeFunction" 
--principal s3.amazonaws.com 
--source-arn "arn:aws:s3:::cloudphoto-source" 
--source-account (aws account id)
```

Проверьте политику доступа к функции, выполнив команду AWS CLI get-policy.
```
aws lambda get-policy --function-name CreateThumbnail
```
### Включить уведомления, о нужном типе дейтвий в bucket'е (в нашем случае триггер на добавление обьектов в корзину)
```
aws s3api put-bucket-notification-configuration 
--bucket cloudphoto-source 
--notification-configuration file://notifications.json
```

notifications.json

```
{
"LambdaFunctionConfigurations": [
    {
      "Id": "png",
      "LambdaFunctionArn": "arn:aws:lambda:eu-central-1:707714338119:function:triggerOnUpload",
      "Events": [ "s3:ObjectCreated:Put","s3:ObjectCreated:Post","s3:ObjectCreated:CompleteMultipartUpload" ],
      "Filter": {
        "Key": {
          "FilterRules": [
            {
              "Name": "suffix",
              "Value": ".png"
            }
          ]
        }
      }
    },
    {
      "Id": "jpg",
      "LambdaFunctionArn": "arn:aws:lambda:eu-central-1:707714338119:function:triggerOnUpload",
      "Events": [ "s3:ObjectCreated:Put","s3:ObjectCreated:Post","s3:ObjectCreated:CompleteMultipartUpload" ],
      "Filter": {
        "Key": {
          "FilterRules": [
            {
              "Name": "suffix",
              "Value": ".jpg"
            }
          ]
        }
      }
    }
  ]
}
```

### Usage
При загрузке s3 обьекта в source-bucket срабатывает триггер, вырезает лица на фотографии и сохроняет их в target-bucket, 
а так же добавляет запись в DynamoDB c ключом FaceKey (ключ обьекта лица) и значением ключа оригинала фотографии PhotoKey