import os
import json
import smtplib

from loader import load_env

load_env()

import requests
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


if __name__ == '__main__':
    try:
        config = ENTRY_PROXY.all({'content_type': 'config', 'fields.configId': os.environ['APP_ENV']})[0]

        try:
            response = requests.post(
                config.server_url,
                headers={'Content-Type': 'application/json'},
                data=json.dumps({'token': config.last_token})
            )

            if response.status_code != 200:
                send_mail(
                    config.from_email,
                    config.from_password,
                    config.to_emails,
                    'Error recibido del dispositivo',
                    'El dispositivo envio el siguiente error: {0}'.format(
                        response.text
                    )
                )
        except requests.ConnectionError:
            try:
                response = requests.get('https://google.com')

                if response:
                    send_mail(
                        config.from_email,
                        config.from_password,
                        config.to_emails,
                        '[IMPORTANTE] No es posible conectarse con el servidor',
                        'El dispositivo cuenta con internet, pero no puede conectarse al servidor.'
                    )
            except:
                pass
    except:
        print("Could not find config")
