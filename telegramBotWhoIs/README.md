## Cоздание telegram бота с использованием WebHooks

### AWS Configure:
```
aws configure [--profile profile-name]
```

### Add iam role for lambda

```
aws iam create-role --role-name  uploadingBotTrigger  --assume-role-policy-document file://trust-policy.json
```

```
aws iam put-role-policy \
  --role-name uploadingBotTrigger \
  --policy-name rolePolicyForUploadingBotTrigger \
  --policy-document file://access-policy.json
```

### Создание тригера который отправляет сообщение и лицо

```
~/my-function$ virtualenv bot-env
```
#### Активируйте среду.
```
~/my-function$ source bot-env/bin/activate
```
#### Установить переменные окружения
```
export TELEG_BOT_TOKEN=1313098976:AAGsvcIzevo7A-bzE0XsjRIYH4bFOG1Lt0g
export CHAT_ID=331529984
```
#### Установите библиотеки с помощью pip.
```
(bot-env) ~/my-function$ pip install requests
pip install telepot
```
#### Деактивировать виртуальную среду.
```
(bot-env) ~/my-function$ deactivate
```
#### Создайте пакет развертывания с установленными библиотеками в корне.
```
~/my-function$ cd bot-env/lib/python3.7/site-packages
~/my-function/bot-env/lib/python3.7/site-packages$ zip -r telegram-bot-func-package.zip .
```

``` 
aws lambda create-function --function-name onUploadingBotTrigger \
--zip-file fileb://onUploadingBotTriggerPackage.zip \
--handler onUploadingBotTrigger.lambda_handler \
--runtime python3.7 \
--role arn:aws:iam::123456789012(свой id):role/uploadingBotTrigger
```

```

aws lambda add-permission --function-name onUploadingBotTrigger --statement-id botTriggerId --action "lambda:InvokeFunction" --principal s3.amazonaws.com --source-arn "arn:aws:s3:::cloudphoto-target" --source-account 707714338119 

aws s3api put-bucket-notification-configuration 
--bucket cloudphoto-target 
--notification-configuration file://notifications.json
```

### Creating an API Gateway
```
    aws apigateway create-rest-api --name 'cp_who_is_bot' --description 'api for cp_who_is_bot'  
```

### Creating a lambda function for bot

```
~/my-function$ virtualenv bot-env
```
#### Активируйте среду.
```
~/my-function$ source bot-env/bin/activate
```
#### Установить переменные окружения
```
export API_INVOKE_URL=https://ybv4b03io5.execute-api.eu-central-1.amazonaws.com/dev
export TELEG_BOT_TOKEN=1313098976:AAGsvcIzevo7A-bzE0XsjRIYH4bFOG1Lt0g
export CHAT_ID=331529984
```
#### Установите библиотеки с помощью pip.
```
(bot-env) ~/my-function$ pip install requests
pip install telepot
```
#### Деактивировать виртуальную среду.
```
(bot-env) ~/my-function$ deactivate
```
#### Создайте пакет развертывания с установленными библиотеками в корне.
```
~/my-function$ cd bot-env/lib/python3.7/site-packages
~/my-function/bot-env/lib/python3.7/site-packages$ zip -r telegram-bot-func-package.zip .
```


```
aws lambda create-function --function-name telegramBotFunction \
--zip-file fileb://telegram-bot-func-package.zip \
--handler telegramBotFunction.lambda_handler \
--runtime python3.7 \
--role arn:aws:iam::123456789012(свой id):role/uploadingBotTrigger
```

### Создание таблицы в Amazon DynamoDB (для связи человек - оригинальные фотографии на которых он есть)
```
aws dynamodb create-table --table-name nameToPhotoTable --attribute-definitions AttributeName=Name,AttributeType=S AttributeName=PhotoKey,AttributeType=S --key-schema AttributeName=Name,KeyType=HASH AttributeName=PhotoKey,KeyType=RANGE --provisioned-throughput ReadCapacityUnits=10,WriteCapacityUnits=5 --region eu-central-1
```

### Connecting Lambda function to API Gateway
Прежде чем мы добавим какой-либо код в нашу функцию, 
давайте сначала добавим к нему триггер. 
Мы хотим, чтобы каждый раз, когда кто-то отправляет сообщение нашему боту в Telegram, 
серверы Telegram должны отправлять его на наш URL-адрес, по которому размещен наш код. Другими словами, мы хотим, 
чтобы HTTP-запрос GET / POST запускал наш код, и мы будем делать это через наш API-шлюз.

```
aws apigateway get-resources --rest-api-id ybv4b03io5 --region eu-central-1    
{
    "items": [
        {
            "path": "/", 
            "id": "fl97e15g00"
        }
    ]
}

aws apigateway put-method --rest-api-id ybv4b03io5 --resource-id fl97e15g00 --http-method POST --authorization-type "NONE" --no-api-key-required --request-parameters "method.request.header.custom-header=false"
aws apigateway put-integration --rest-api-id ybv4b03io5 --resource-id fl97e15g00 --http-method POST --type AWS --integration-http-method POST --uri 'arn:aws:lambda:eu-central-1:707714338119:function:telegramBotFunction' --region eu-central-1
aws apigateway create-deployment --rest-api-id ybv4b03io5  --stage-name dev --stage-description 'Development Stage' --description 'First deployment to the dev stage'
```

(? и еще один метод на "где?")

###Setting Webhooks

```
    API-invoke-URL - https://ybv4b03io5.execute-api.eu-central-1.amazonaws.com/dev
    chat - "id": 331529984,
    
    "https://api.telegram.org/bot<your-bot-token>/setWebHook?url=<your-API-invoke-URL>"
    
    Вы получите подтверждающее сообщение от Telegram, и с этого момента все сообщения, отправленные вашему боту, будут отправляться на этот URL.
    {"ok":true,"result":true,"description":"Webhook was set"}
```