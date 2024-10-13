import requests
import uuid
import json

import config

def get_token(authToken = config.GIGACHAT_API_KEY, scope = config.GIGACHAT_SCOPE):
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

    payload = {
        'scope': scope
    }
    rq_id = str(uuid.uuid4())
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': rq_id,
        'Authorization': f'Basic {authToken}'
    }
    try:
        response = requests.post(url, headers=headers, data=payload, verify=False)
        return response
    except requests.RequestException as _ex:
        print(f"Ошибка: {_ex}")
        return -1
def gigachat_models(giga_token):
    url = "https://gigachat.devices.sberbank.ru/api/v1/models"

    payload = {}
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {giga_token}'
    }
    try:
        response = requests.request("GET", url, headers=headers, data=payload, verify=False)
        return response
    except requests.RequestException as _ex:
        print(f"Ошибка: {_ex}")
        return -1
def get_chat_completion(auth_token, user_message, max_tokens:int = 512, model:str = "GigaChat"):
    """
    Отправляет POST-запрос к API чата для получения ответа от модели GigaChat.

    Параметры:
    - auth_token (str): Токен для авторизации в API.
    - user_message (str): Сообщение от пользователя, для которого нужно получить ответ.

    Возвращает:
    - str: Ответ от API в виде текстовой строки.
    """
    # URL API, к которому мы обращаемся
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

    # Подготовка данных запроса в формате JSON
    payload = json.dumps({
        "model": model,  # Используемая модель
        "messages": [
            {
                "role": "system",
                "content": "Ты можешь выделять текст html тегами вроде <i></i>, <b></b>. Ты не должен задавать вопросы пользователю"
            },
            {
                "role": "user",  # Роль отправителя (пользователь)
                "content": user_message  # Содержание сообщения
            }
        ],
        "temperature": 0.7,  # Температура генерации
        "top_p": 0.1,  # Параметр top_p для контроля разнообразия ответов
        "n": 1,  # Количество возвращаемых ответов
        "stream": False,  # Потоковая ли передача ответов
        "max_tokens": max_tokens,  # Максимальное количество токенов в ответе
        "repetition_penalty": 1,  # Штраф за повторения
        "update_interval": 0  # Интервал обновления (для потоковой передачи)
    })

    # Заголовки запроса
    headers = {
        'Content-Type': 'application/json',  # Тип содержимого - JSON
        'Accept': 'application/json',  # Принимаем ответ в формате JSON
        'Authorization': f'Bearer {auth_token}'  # Токен авторизации
    }

    try:
        response = requests.request("POST", url, headers=headers, data=payload, verify=False)
        return response
    except requests.RequestException as e:
        print(f"Произошла ошибка: {str(e)}")
        return -1

def ask_question(message, max_tokens = 250, model:str = "GigaChat"):
    response = get_token()
    if response != -1:
        # print(response.text)
        giga_token = response.json()['access_token']
        #expires_at = response.json()['expires_at']
        #response = gigachat_models(giga_token)
        #models = response.text
        #print(models)
        answer = get_chat_completion(giga_token, message, max_tokens, model)
        if answer.status_code == 200:
            #print(answer.json()['choices'][0]['message']['content'])
            print("Затрачено токинов: " + str(answer.json()['usage']['total_tokens']))
            return answer.json()['choices'][0]['message']['content']
        else:
            print("Что-то пошло не так")
            print(answer)
            print(answer.json())
            return -1