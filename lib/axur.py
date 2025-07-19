# -*- coding: utf-8 -*-
import os
import requests
from dotenv import load_dotenv
from loguru import logger
#import json
from io import BytesIO
from PIL import Image
import base64

load_dotenv()

class AxurAPICommon:
    url = dict()
    token = ""

    def __init__(self):
        self.url['incidents'] = os.getenv("AXUR_URL", None)
        self.url['employee_leaks'] = os.getenv("AXUR_URL_LEAKS", None)
        self.url['client_leaks'] = os.getenv("AXUR_URL_CLIENT_LEAKS", None)
        self.token = os.getenv("AXUR_TOKEN", None)
    
    def request(self, method:str, url:str):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        try: 
            if method == "GET":
                 response = requests.get(url, headers=headers)
            if method == "POST":
                 response = requests.post(url, headers=headers)
        except Exception as err:
            logger.critical(err)
        else:
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(response.json())
                return None

    def get_new_incidents(self) ->list:
        inicidents = []
        incident = dict()
        data = self.request("GET", self.url['incidents'])
        try:
            axur_tickets = data['collectionData']['tickets']
        except Exception as err:
            logger.critical(err)
        for t in axur_tickets:
            try:
                jpg = next((item['url'] for item in t['attachments'] if item['name'].lower().endswith('.jpg')),None)
                txt = next((item['url'] for item in t['attachments'] if item['name'].lower().endswith('.txt')),None)
                incident = {
                    "id": str(t.get('ticket').get('ticketKey')) or "",
                    "ticketKey": str(t.get('ticket').get('ticketKey')) or "",
                    "tipo": str(t.get('detection').get('type')) or "",
                    "titulo": str(t.get('reference')) or "",
                    "url": str(t.get('snapshots').get('digitalLocation').get('url')) or "",
                    "risco": int(float(t.get('detection').get('prediction.risk',0)) * 100) or 0,
                    "coletor": str(t.get('detection').get('creation.collector')) or "",
                    "isp": str(t.get('detection').get('isp')) or "",
                    "host": str(t.get('snapshots').get('digitalLocation').get('host').get('name')) or "",
                    "ip": str(t.get('snapshots').get('digitalLocation').get('host').get('ip').get('address')) or "",
                    "jpg": jpg,
                    "txt": txt
                }
            except Exception as err:
                logger.critical(err)
            else:
                inicidents.append(incident)
        return inicidents
    
    @staticmethod
    def get_incident_image(self, url:str) -> str:
        try:
            response = self.request("GET", url)
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

    def get_new_employee_leaks(self):
        detections = []
        detection = dict()
        response = self.request("GET", self.url['employee_leaks'] )
        axur_detections = response['collectionData']['detections']
        for d in axur_detections:
            detection = {
                "id": str(d.get('id')) or "",
                "source": str(d.get('source.name')) or "",
                "user": str(d.get('user')) or "",
                "password": str(d.get('password')) or "",
                "status": str(d.get('status')) or "",
                "types": str(d.get('source.name')) or "",
                "user": str(d.get('user')) or "",
                "password":str(d.get('password')) or "",
                "status": str(d.get('status')) or "",
                "types": str(d.get('credential.types')) or "",
                "domain": str(d.get('user.emailDomain')) or "",
            }
            detections.append(detection)
        return detections
    
    def get_new_client_leaks(self):
        detections = []
        detection = dict()
        response = self.request("GET", self.url['client_leaks'] )
        try:
            axur_detections = response['collectionData']['detections']
        except Exception as err:
            logger.critical(err)
        
        for d in axur_detections:
            try:
                detection = {
                    "id": d['id'],
                    "source": str(d.get('source.name')) or "",
                    "user": str(d.get('user')) or "",
                    "password": str(d.get('password')) or "",
                    "status": str(d.get('status')) or "",
                    "type": str(d.get('credential.types')) or "",
                    "access.domain": str(d.get('access.domain')) or "",
                    "access.host": str(d.get('access.host')) or "",
                }
            except Exception as err:
                logger.critical(f'Falha ao ler detecao {d['id']} - {d['user']} - {err}')
            else:
                detections.append(detection)
        return detections


#axur = AxurAPICommon()
#print (json.dumps(axur.get_new_client_leaks(), indent=2))


