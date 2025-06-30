import os
import requests
from dotenv import load_dotenv
from loguru import logger
import json
from io import BytesIO
from PIL import Image
import base64

load_dotenv()
axur_url = os.getenv("AXUR_URL", None)
axur_token = os.getenv("AXUR_TOKEN", None)
axur_url_leaks = os.getenv("AXUR_URL_LEAKS", None)
#DEBUG = str(os.getenv("DEBUG").lower) == "true"

def axur_get_new_incidents():
    tickets = []
    ticket = dict()
    headers = {
        "Authorization": f"Bearer {axur_token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(axur_url, headers=headers)
    except Exception as erro:
        logger.critical(f'Falha em consultar incidente na AXUR - {erro}')
    else:
        if response.status_code == 200:
            data = response.json()
            axur_tickets = data['collectionData']['tickets']

            for t in axur_tickets:
                jpg = next((item['url'] for item in t['attachments'] if item['name'].lower().endswith('.jpg')),None)
                txt = next((item['url'] for item in t['attachments'] if item['name'].lower().endswith('.txt')),None)
                ticket = {
                    "id": str(t['ticket']['ticketKey']),
                    "tipo": t['detection']['type'],
                    "titulo": t['snapshots']['content']['title'],
                    "url": t['snapshots']['digitalLocation']['url'],
                    "risco": int(float(t['detection'].get('prediction.risk',0)) * 100),
                    "coletor": t['detection']['creation.collector'],
                    "isp": t['detection']['isp'],
                    "host": t['snapshots']['digitalLocation']['host']['name'],
                    "ip": t['snapshots']['digitalLocation']['host']['ip']['address'],
                    "jpg": jpg,
                    "txt": txt
                }
                tickets.append(ticket)
            return tickets
        else:
            logger.error(f'Falha ao consultar incidentes na AXUR - {response.status_code} - {response.text}')
            return None

def axur_get_image(url):
    headers = {
        "Authorization": f"Bearer {axur_token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
    except Exception as erro:
        logger.critical(f'Falha em consultar imagem AXUR - {erro}')
    else:
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))

            largura = 300
            propor = largura / img.width
            altura = int(img.height * propor)

            img_resize = img.resize((largura, altura))

            buffer = BytesIO()
            img_resize.save(buffer, format="JPEG")
            img_new = buffer.getvalue()

            img_b64 = base64.b64encode(img_new).decode('utf-8')
            img_html = f'<img src="data:image/jpeg;base64,{img_b64}" alt="Imagem JPG" />'
            return img_html
        else:
            logger.error(f'Falha ao consultar imagem na AXUR - {response.status_code} - {response.text}')
            return None

def axur_get_new_employee_credentials():
    detections = []
    detection = dict()
    headers = {
        "Authorization": f"Bearer {axur_token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(axur_url_leaks, headers=headers)
    except Exception as erro:
        logger.critical(f'Falha ao consultar credenciais de colaboradores - {erro}')
    else:
        if response.status_code == 200:
            data = response.json()
            axur_detections = data['collectionData']['detections']
            for d in axur_detections:
                detection = {
                    "id": d['id'],
                    "source": d['source.name'],
                    "user": d['user'],
                    "password": d['password'],
                    "status": d['status'],
                    "types": d['credential.types'],
                    "domain": d['user.emailDomain'],
                }
                detections.append(detection)
            return detections
        else:
            logger.error(f'Falha ao consultar credenciais de colaboradores- {response.status_code} - {response.text}')
            return None


def axur_get_ticket(ticket_key):
    headers = {
        "Authorization": f"Bearer {axur_token}",
        "Content-Type": "application/json"
    }

    url = f'https://api.axur.com/gateway/1.0/api/tickets-core/tickets/{ticket_key}'

    try:
        response = requests.get(url, headers=headers)
    except Exception as erro:
        logger.critical(f'Falha em consultar incidente na AXUR - {erro}')
    else:
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f'Falha ao consultar incidentes na AXUR - {response.status_code} - {response.text}')
            return None
        
def axur_comment_ticket(ticket_key, comment):
    headers = {
        "Authorization": f"Bearer {axur_token}",
        "Content-Type": "application/json"
    }

    url = f'https://api.axur.com/gateway/1.0/api/tickets-texts/texts/tickets/{ticket_key}'
    payload = {
        "content": comment,
        "internal": False,
        "type": "comment"
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
    except Exception as erro:
        logger.critical(f'Falha ao adicionar comentário - {erro}')
    else:
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f'Falha ao adicionar comentário - {response.status_code} - {response.text}')
            return None


#print (json.dumps(axur_get_new_incidents(), indent=2))
#data = axur_get_new_employee_credentials()
#print (json.dumps(data, indent=2))
#print (len(data))
#print (json.dumps(axur_get_ticket("s3zmr7"), indent=2))
#print (json.dumps(axur_comment_ticket("s3zmr7","Teste de comentário"), indent=2))


