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
logger.add("f_axur.log", rotation="10 MB")

soar_host = os.getenv("SOAR_HOST")
soar_port = os.getenv("SOAR_PORT")
soar_org =  os.getenv("SOAR_ORG")
soar_key_id = os.getenv("SOAR_KEY_ID")
soar_key_secret = os.getenv("SOAR_KEY_SECRET")
soar_ca_cert = os.getenv("SOAR_CA_CERT")

#axur_url = os.getenv("AXUR_URL")
#axur_token = os.getenv("AXUR_TOKEN")

def pooler_new_incidents():
    logger.info("Iniciado monitoramento de novos incidentes na AXUR.")
    while True:
        logger.info("Consultando novos incidentes...")
        new_incidents = axur_get_new_incidents()
        if new_incidents:
            logger.info("Novos incidentes localizados.")
            for incident in new_incidents:
                soar_new_incident(incident)
        else:
            logger.warning("Nenhum novo incidente localizado.")
        
        time.sleep(300)

def pooler_new_employee_credentials():
    logger.info("Iniciado monitoramento de credenciais de colaboradores")
    while True:
        logger.info("Consultando novas credenciais de colaboradores...")
        new_credentials = axur_get_new_employee_credentials()
        if new_credentials:
            logger.info(f'Identificada {len(new_credentials)} novas credenciais vazadas.')
        #    for incident in new_incidents:
        #        soar_new_incident(incident)
        else:
            logger.warning("Nenhuma nova credencial vazada foi identificada")
        time.sleep(300)


#threading.Thread(target=pooler_new_incidents).start()
#threading.Thread(target=pooler_new_employee_credentials).start()
