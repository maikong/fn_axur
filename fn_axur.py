# -*- coding: utf-8 -*-
#from resilient_lib import build_resilient_url
from lib.axur import *
from lib.soar import *
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from loguru import logger

import threading
import os
import time

load_dotenv()
logger.add("fn_axur.log", rotation="10 MB")

POLLER_TIME = int(os.getenv("POLLER_TIME"))
#soar_host = os.getenv("SOAR_HOST")
#soar_port = os.getenv("SOAR_PORT")
#soar_org =  os.getenv("SOAR_ORG")
#soar_key_id = os.getenv("SOAR_KEY_ID")
#soar_key_secret = os.getenv("SOAR_KEY_SECRET")
#soar_ca_cert = os.getenv("SOAR_CA_CERT")

#axur_url = os.getenv("AXUR_URL")
#axur_token = os.getenv("AXUR_TOKEN")

def pooler_new_incidents():
    axur = AxurAPICommon()
    logger.info(f'Iniciado monitoramento de novos incidentes na AXUR a cada {POLLER_TIME} segundos.')
    while True:
        logger.info("Consultando novos incidentes...")
        new_incidents = axur.get_new_incidents()
        if new_incidents:
            logger.warning(f'Indentificado {len(new_incidents)} novos incidentes.')
            #for incident in new_incidents:
            #    soar_new_incident(incident)
        else:
            logger.info("Nenhum novo incidente localizado.")
        
        time.sleep(POLLER_TIME)

def pooler_new_employee_credentials():
    axur = AxurAPICommon()
    logger.info("Iniciado monitoramento de credenciais de colaboradores")
    while True:
        logger.info("Consultando novas credenciais de colaboradores...")
        incidents = axur.get_new_employee_leaks()
        if incidents:
            logger.warning(f'Identificada {len(incidents)} novas credenciais vazadas de colaboradores.')
            soar = SoarApiCommon()
            for i in incidents[0]:
                description = u"""
                    Uma credencial de cliente disponível na Deep/Dark WEB.
                """
                payload = {
                    "name": "[AXUR] Fraude digital",
                    "description": description,
                    "discovered_date": int(time.time() * 1000),
                    "external_id": i['id'],
                    "incident_type_ids": ['CTI - Credenciais de clientes',],
                    "confirmed": True,
                    "data_compromised": False,
                    "severity_code": 5,
                    "properties": {
                        "axur_id": i['id'],
                        "axur_credencial" : i['user'],
                        "axur_credencial_type" : i['type']
                    }
                }
                #soar.add_incident(description, "CTI - Credenciais de clientes", payload)
                    
        else:
            logger.info("Nenhuma nova credencial vazada foi identificada")
        time.sleep(POLLER_TIME)

def pooler_new_clients_credentials():
    axur = AxurAPICommon()
    logger.info("Iniciado monitoramento de credenciais de clientes")
    while True:
        logger.info("Consultando novas credenciais de clientes...")
        new_credentials = axur.get_new_client_leaks()
        if new_credentials:
            logger.warning(f'Identificada {len(new_credentials)} novas credenciais vazadas de clientes.')
        #    for incident in new_incidents:
        #        soar_new_incident(incident)
        else:
            logger.info("Nenhuma nova credencial vazada foi identificada")
        time.sleep(POLLER_TIME)


threading.Thread(target=pooler_new_incidents).start()
#threading.Thread(target=pooler_new_employee_credentials).start()
#threading.Thread(target=pooler_new_clients_credentials).start()

