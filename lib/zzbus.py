# -*- coding: utf-8 -*-
import os
from loguru import logger
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def get_env_variable(var_name):
    value = os.getenv(var_name)
    if value is None:
        raise ValueError(f"Environment variable '{var_name}' not set.")
    return value

class ZZBusApiCommon():
    def __init__(self):
        try: 
          self.ZZBUS_HOST = get_env_variable("ZZBUS_HOST")
          self.ZZBUS_KEY = get_env_variable("ZZBUS_KEY")
        except Exception as err:
            logger.critical(err)
    
    def request(self, method:str, url:str, payload:dict):
      headers = {
          "Authorization": f'Basic {self.ZZBUS_KEY}',
          "Content-Type": "application/json"
      }
      try: 
          if method.upper() == "GET":
                response = requests.get(url, headers=headers)
          if method.upper() == "POST":
                print(headers)
                response = requests.post(url, headers=headers, data=json.dumps(payload))
      except Exception as err:
          logger.critical(err)
      else:
          if response.status_code == 200:
              return response.json()
          else:
              logger.error(response.json())
              return None

#zzbus = ZZBusApiCommon()
#response = zzbus.request("POST",get_env_variable("ZZBUS_HOST"),payload)
#print (json.dumps(response, indent=2))