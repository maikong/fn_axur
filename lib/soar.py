# -*- coding: utf-8 -*-
import os
from requests.auth import HTTPBasicAuth
from loguru import logger
from lib.axur import *
import requests
import json
import time

soar_host = os.getenv("SOAR_HOST")
soar_port = os.getenv("SOAR_PORT")
soar_org =  os.getenv("SOAR_ORG")
soar_key_id = os.getenv("SOAR_KEY_ID")
soar_key_secret = os.getenv("SOAR_KEY_SECRET")
soar_ca_cert = os.getenv("SOAR_CA_CERT")

class SoarApiCommon():
    def __init__(self):
        self.soar_host = os.getenv("SOAR_HOST")
        self.soar_port = os.getenv("SOAR_PORT")
        self.soar_org =  os.getenv("SOAR_ORG")
        self.soar_key_id = os.getenv("SOAR_KEY_ID")
        self.soar_key_secret = os.getenv("SOAR_KEY_SECRET")
        self.soar_ca_cert = os.getenv("SOAR_CA_CERT")
    
    def request(self, method:str, url:str, payload=None):
        headers = {"Content-Type": "application/json"}
        auth = HTTPBasicAuth(self.soar_key_id, self.soar_key_secret)
        try:
            if method.upper == "GET":
                response = requests.get(url, headers=headers, auth=auth, verify=self.soar_ca_cert)
            if method.upper == "POST":
                response = requests.post(url, headers=headers, data=json.dumps(payload) ,auth=auth, verify=self.soar_ca_cert)
        except Exception as err:
            logger.critical(str(err))
        else:
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(response.json())
                return None
            
    def add_incident(self, description, type, payload):
        url = "https://{}:{}/rest/orgs/{}/incidents".format(soar_host,soar_port,soar_org)
        response = self.request("POST", url, description, type, payload)
        if response:
            return response
        else:
            return None

    def add_artifact(self, incident_id, type, value, description=""):
        url = "https://{}:{}/rest/orgs/{}/incidents/{}/artifacts".format(soar_host,soar_port,soar_org,incident_id)
        payload = {
            "type": type,
            "value": value,
            "description": description
        }
        response = self.request("POST", url, payload)
        if response:
            return response
        else:
            return None



def soar_get_incident(id):
    """
    Consulta um incidente específico no SOAR através de seu ID.

    Args:
        id (int): ID do incidente
    Returns:
        incidente (json): Incidente e seus atributos
    """

    url = "https://{}:{}/rest/orgs/{}/incidents/{}".format(soar_host,soar_port,soar_org, id)
    headers = {"Content-Type": "application/json"}
    auth = HTTPBasicAuth(soar_key_id, soar_key_secret)
    response = requests.get(url, headers=headers, auth=auth, verify=soar_ca_cert)

    if response.status_code == 200:
        return response.json()
    else:
        #print("ERROR:", response.status_code, response.text)
        return None

def soar_new_incident_comment(incident_id, comment):
    url = "https://{}:{}/rest/orgs/{}/incidents/{}/comments".format(soar_host,soar_port,soar_org,incident_id)
    headers = {"Content-Type": "application/json"}
    auth = HTTPBasicAuth(soar_key_id, soar_key_secret)
    payload = {
        "text": {
            "format": "html",
            "content": comment
        }
    }
    
    response = requests.post(url, headers=headers, auth=auth, data=json.dumps(payload), verify=soar_ca_cert)
    if response.status_code == 200:
        logger.info(f'Comentário adicionado no incidente {incident_id} do SOAR.')

def soar_new_incident_artifact(incident_id, type, value, desc):
    url = "https://{}:{}/rest/orgs/{}/incidents/{}/artifacts".format(soar_host,soar_port,soar_org,incident_id)
    headers = {"Content-Type": "application/json"}
    auth = HTTPBasicAuth(soar_key_id, soar_key_secret)
    payload = {
        "type": type,
        "value": value,
        "description": desc
    }
    
    try:
        response = requests.post(url, headers=headers, auth=auth, data=json.dumps(payload), verify=soar_ca_cert)
    except Exception as err:
        logger.critical(f'Erro de conexão com o SOAR - {err}')
    else: 
        if response.status_code == 200:
            logger.info(f'Artefato adicionado no incidente {incident_id} do SOAR. ({type} - {value})')
        else:
            logger.error(f'Erro ao tentar criar artefado - {response.text}')

def soar_new_incident_attachments(incident_id, attachment):
    url = "https://{}:{}/rest/orgs/{}/incidents/{}/attachments".format(soar_host,soar_port,soar_org,incident_id)
    headers = {"Content-Type": "multipart/form-data"}
    auth = HTTPBasicAuth(soar_key_id, soar_key_secret)
    try:
        response = requests.post(url, headers=headers, auth=auth, data=json.dumps(attachment), verify=soar_ca_cert)
    except Exception as err:
        logger.critical(f'Erro de conexão com o SOAR - {err}')
    else: 
        if response.status_code == 200:
            logger.info(f'Anexo adicionado no incidente {incident_id} do SOAR.')
        else:
            logger.error(f'Erro ao tentar adiconar anexo - {response.text}')

def soar_new_incident(axur_incident):
    url = "https://{}:{}/rest/orgs/{}/incidents".format(soar_host,soar_port,soar_org)
    headers = {"Content-Type": "application/json"}
    auth = HTTPBasicAuth(soar_key_id, soar_key_secret)

    description = f"""
    Um provável novo site falso foi identificado pela AXUR <a href="https://one.axur.com/digital-fraud/tickets/{axur_incident['id']}" target="_blank">Detalhes</a>
       - URL: <a href="{axur_incident['url']}" target="_blank">{axur_incident['url']}</a>
       - Título do site: {axur_incident['titulo']}
       - Grau de risco: {axur_incident['risco']}
       - TicketID: {axur_incident['id']}
       - Coletor: {axur_incident['coletor']}
       - Tipo: {axur_incident['tipo']}
       - ISP: {axur_incident['isp']}
       - Host: {axur_incident['host']} ({axur_incident['ip']})
    """

    payload = {
        "name": "[AXUR] Fraude digital",
        "description": description,
        "discovered_date": int(time.time() * 1000),
        "external_id": axur_incident['id'],
        "incident_type_ids": ['Fraude digital',],
        "confirmed": True,
        "data_compromised": False,
        "severity_code": 5,
        "properties": {
            "axur_id": axur_incident['id'],
        },
    }
 
    try:
        response = requests.post(url, headers=headers, auth=auth, data=json.dumps(payload), verify=soar_ca_cert)
    except Exception as err:
        logger.critical(f'Erro de conexão com o SOAR - {err}')
    else: 
        if response.status_code == 200:
            new_incident = response.json()
            logger.info("Incidente {} criado no SOAR.".format(new_incident['id']))

            incident_id = new_incident['id']
            soar_new_incident_comment(incident_id, description)
            soar_new_incident_artifact(incident_id,"IP Address", axur_incident['ip'],"IP do Host")
            soar_new_incident_artifact(incident_id,"URL",axur_incident['url'],"URL do site falso")

            #soar_new_incident_comment(incident_id, axur_get_image(axur_incident['jpg']))

        else:     
            logger.error(f'Falha ao criar incidente no SOAR - {response.status_code} - {response.text}')
            return None
    
