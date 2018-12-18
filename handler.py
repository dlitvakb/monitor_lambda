import os
import json
import random
import string
import smtplib
import dateutil.parser
from datetime import datetime, timedelta, timezone

from loader import load_env

load_env()

from contentful_management import Client as CMA

CMA_CLIENT = CMA(os.environ['CF_CMA_TOKEN'])
ENTRY_PROXY = CMA_CLIENT.entries(os.environ['CF_SPACE_ID'], 'master')


def send_mail(user, password, to_mails, subject, body):
    message = 'From: {0}\nTo: {1}\nSubject: {2}\n\n{3}'.format(
        user,
        ", ".join(to_mails),
        subject,
        body
    )
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(user, password)
        server.sendmail(user, to_mails, message)
        server.close()
        print('Email sent: {0}'.format(subject))
    except Exception as e:
        print('Failed to send Email')
        print(e)


def generate_token():
    return ''.join(
        random.SystemRandom().choice(
            string.ascii_uppercase + string.ascii_lowercase + string.digits
        ) for _ in range(32)
    )


def response(status_code, body=None):
    if body is None:
        body = {}

    return {
        "statusCode": status_code,
        "headers": {'Content-Type': 'application/json'},
        "body": json.dumps(body)
    }


def monitor(event, context):
    print(event)
    data = json.loads(event['body'])
    if 'token' not in data:
        print("token not sent")
        return response(403, {"message": "Token not sent"})

    config = None
    try:
        config = ENTRY_PROXY.all({'content_type': 'config', 'fields.configId': os.environ['APP_ENV']})[0]
    except:
        print("config not found")
        return response(400, {"message": "Could not find config"})

    if config.last_token != data['token']:
        print("token does not match")
        return response(403, {"message": "Token does not match"})

    new_token = generate_token()
    print("generated token")

    config.last_token = new_token

    last_called_at = datetime.now(timezone.utc).isoformat()
    config.last_called_at = last_called_at[:15] + last_called_at[25:] # Trim seconds and microseconds
    try:
        config.save()
    except Exception as e:
        print(e)
        return response(500, {"message": "Error saving"})

    print("success")
    return response(200, {"next_token": new_token})


def health(event, context):
    config = None
    try:
        config = ENTRY_PROXY.all({'content_type': 'config', 'fields.configId': os.environ['APP_ENV']})[0]
        print("config found")
    except:
        print("config not found")
        return response(400, {"message": "Could not find config"})

    last_called_at = dateutil.parser.parse(config.last_called_at)

    if datetime.now(timezone.utc) - last_called_at > timedelta(minutes=10):
        print("no contact")
        send_mail(
            config.from_email,
            config.from_password,
            config.to_emails,
            '[IMPORTANTE] Dispositivo sin contacto',
            'No se ha recibido contacto del dispositivo hace mas de 10 minutos.'
        )
        return response(400, {"message": "No contact in over 10 minutes"})

    print("ok")
    return response(200)
