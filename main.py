import os
import json
import time
import requests
import schedule
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime


def job():
    print("[%s] Iniciando verificação" % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    r = requests.get('https://oap.ind.nl/oap/api/desks/AM/slots/?productKey=DOC&persons=3')
    if r.status_code == 200:
        dados = r.text.split(",")
        dados.pop(0)
        datas = json.loads(','.join(dados))['data']
        if len(datas) > 0:
            output_dict = [x for x in datas if x['date'] > '2022-09-14' and x['date'] < '2022-10-27']
            if len(output_dict) > 0:
                send_datas(output_dict)
    else:
        send_error(r.status_code)
    r = requests.get('https://oap.ind.nl/oap/api/desks/AM/slots/?productKey=DOC&persons=1')
    if r.status_code == 200:
        dados = r.text.split(",")
        dados.pop(0)
        datas = json.loads(','.join(dados))['data']
        if len(datas) > 0:
            output_dict = [x for x in datas if x['date'] > '2022-09-01' and x['date'] < '2022-10-26']
            if len(output_dict) > 0:
                send_datas_well(output_dict)
    else:
        send_error(r.status_code)
    print("[%s] Verificação finalizada" % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("---------------------")


def send_error(error):
    print("[%s] E-mail erro enviado" % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    send_mail("Erro ao buscar informações IND", error)


def send_datas(datas):
    print("[%s] E-mail datas enviado pro Naidion" % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    dates = [x['date'] for x in datas]
    used = set()
    dates = [x for x in dates if x not in used and (used.add(x) or True)]
    body = "Encontrei datas disponíveis no IND:" + '\n'.join(dates)
    send_mail("Datas disponíveis no IND", body, 'brovedan@gmail.com')

def send_datas_well(datas):
    print("[%s] E-mail datas enviado pro Welligton" % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    dates = [x['date'] for x in datas]
    used = set()
    dates = [x for x in dates if x not in used and (used.add(x) or True)]
    body = "Encontrei datas disponíveis no IND:" + '\n'.join(dates)
    send_mail("Datas disponíveis no IND", body, 'well.soares.nunes@gmail.com')

def send_mail(sub, body, receive):
    user = 'noreply@brovetech.com.br'
    password = os.environ.get('PASSWORD', "")

    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = sub
        message["From"] = user
        message["To"] = receive
        text = body
        message.attach(MIMEText(text, "plain"))
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.hostinger.com', 465, context=context) as server:
            server.login(user, password)
            server.sendmail(
                user, receive, message.as_string()
            )
    except Exception as ex:
        print("Something went wrong….", ex)
job()
schedule.every(15).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
