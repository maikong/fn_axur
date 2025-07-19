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

def pooler_new_incidents():
    axur = AxurAPICommon()
    logger.info(f'Iniciado monitoramento de novos incidentes na AXUR a cada {POLLER_TIME} segundos.')
    while True:
        logger.info("Consultando novos incidentes...")
        new_incidents = axur.get_new_incidents()
        if new_incidents:
            logger.warning(f'Indentificado {len(new_incidents)} novos incidentes.')
            for incident in new_incidents:
                soar_new_incident(incident)
                
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
        client_leaks = axur.get_new_client_leaks()
        if client_leaks:
            logger.warning(f'Identificada {len(client_leaks)} novas credenciais vazadas de clientes.')
            soar = SoarApiCommon()
            for i in client_leaks[:1]:
                description = f"""
                Uma credencial de usuário vazada foi identificada.
                Origem: {i['source']}
                Usuário: {i['user']}
                Acesso: {i['access.host']}
                Axur ID: {i['id']}
                """
                payload = {
                    "inc_training": True,
                    "name": "[AXUR] Credencial de cliente",
                    "description": description,
                    "discovered_date": int(time.time() * 1000),
                    "external_id": i['id'],
                    "incident_type_ids": ['CTI - Credenciais de clientes',],
                    "confirmed": True,
                    "data_compromised": False,
                    "severity_code": 5,
                    "properties": {
                        "axur_id": i['id'],
                        "axur_credencial": i['user'],
                    },
                    "pii": {
                        "data_compromised": False,
                    }
                }
                soar_incident = soar.add_incident(payload)
                if soar_incident:
                    logger.info(f'Aberto o incidente {soar_incident.get('id')} no SOAR')
                else:
                    logger.error('Falha em abrir o incidente no SOAR!')
        else:
            logger.info("Nenhuma nova credencial vazada foi identificada")
        time.sleep(POLLER_TIME)


threading.Thread(target=pooler_new_incidents).start()
#threading.Thread(target=pooler_new_employee_credentials).start()
threading.Thread(target=pooler_new_clients_credentials).start()

