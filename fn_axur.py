#from resilient_lib import build_resilient_url
from axur import *
from soar import *
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from loguru import logger

import threading
import os
import time

load_dotenv()

soar_host = os.getenv("SOAR_HOST")
soar_port = os.getenv("SOAR_PORT")
soar_org =  os.getenv("SOAR_ORG")
soar_key_id = os.getenv("SOAR_KEY_ID")
soar_key_secret = os.getenv("SOAR_KEY_SECRET")
soar_ca_cert = os.getenv("SOAR_CA_CERT")

#axur_url = os.getenv("AXUR_URL")
#axur_token = os.getenv("AXUR_TOKEN")

def pooler():
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


axur_incident_pooler_thread = threading.Thread(target=pooler)
axur_incident_pooler_thread.start()

#soar_new_incident_artifact("3728","URL","http://www.arezzo.com.br","teste")

#url = "https://api.axur.com/gateway/1.0/api/files/file/b25f462b8010cd0f9d142150a26e9af6e325d1a3e6485d8a50604c49a0dbe38f-7dd84a743fdb4ee69b7670b8d5a8a13b.jpg"
#soar_new_incident_comment(3731, axur_get_image(url))
