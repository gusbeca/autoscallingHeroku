#!/usr/bin/env python3
import os  # PARA LLAMAR VAIABLES DE ENTORNO
from apscheduler.schedulers.blocking import BlockingScheduler # PARA HACER TAREAS PROGRAMADAS
import requests
import base64
import json
import boto3
import datetime

#-----------------------INICIALIZACION DE VARAIBLES---------------------
APP = "workerh"
KEY = os.environ['H_API_KEY']
PROCESS = "worker"

data_string = ":" + KEY

data_bytes = data_string.encode("utf-8")

# Generate Base64 encoded API Key
BASEKEY = base64.b64encode(data_bytes)
# Create headers for API call
HEADERS = {
    "Accept": "application/vnd.heroku+json; version=3",
    "Authorization": "Bearer "+KEY,
    "Content-Type": "application/json"
}

#"Authorization": BASEKEY

#------------------------DEFINICION DE FUNCIONES-----------------------------------------

#----------FUNCION DE ESCALADO--------------------------------------
def scale(size):
    payload = {'quantity': size}
    json_payload = json.dumps(payload)
    url = "https://api.heroku.com/apps/" + APP + "/formation/" + PROCESS
    try:
        result = requests.patch(url, headers=HEADERS, data=json_payload)
        print(result)
    except:
        print("test!")
        return None
    if result.status_code == 200:
        return "Success!"
    else:
        return "Failure"


#print('Scaling ...')
#print(scale(0))


#-----------TAREA DE CRON------------------------------------------------------------

sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=2)
def job():

    region_name = 'us-east-1'
    aws_access_key_id = os.environ['AWSID']
    aws_secret_access_key = os.environ['AWSK']

    cloudwatch = boto3.resource('cloudwatch', region_name=region_name,
                                aws_access_key_id=aws_access_key_id,
                                aws_secret_access_key=aws_secret_access_key)
    metric = cloudwatch.Metric('AWS/SQS', 'ApproximateNumberOfMessagesVisible')
    # print(metric.dimensions)
    inicio = datetime.datetime.now() + datetime.timedelta(hours=0)-datetime.timedelta(seconds=300)
    inicio = inicio.isoformat()
    ahora = datetime.datetime.now() + datetime.timedelta(hours=0)
    ahora = ahora.isoformat()
    print(inicio,'   ',ahora)
    qmensajes = metric.get_statistics(Dimensions=[
        {
            'Name': 'QueueName',
            'Value': 'videoQ'
        },
    ],
        StartTime=inicio,
        EndTime=ahora,
        Period=60,
        Statistics=['Average']
    )
    q=qmensajes['Datapoints'][0]['Average']
    print(q)
    if q>20:
        print('Scaling to 2 dynos...')
        print(scale(3))
    elif q <20 and q>10:
        print('Scaling  to 3 dynos...')
        print(scale(2))
    elif q<11 and q > 8:
        print('Scaling to 1 dyno ...')
        print(scale(1))
    elif q < 1:
        print('Scaling to 0 dyno ...')
        print(scale(0))



sched.start()