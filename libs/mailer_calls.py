#!./venv/bin/python

"""
Script containing mail functions/objects.
"""

import configparser
import logging
import smtplib
import ssl
from email.mime.text import MIMEText
import base64

#Define config and logger.
CONFIG = configparser.ConfigParser()
CONFIG.read("conf/config.ini")
SECTION = "mailer"
PATH = CONFIG['global']['data']

MAILER = CONFIG['mailer']

logger = logging.getLogger(SECTION)

def mailer(subject, body):
    """
    Accepts subject and body for sending an email.
    """

    message = f"Subject: {subject}\n\n{body}"
    msg = MIMEText(message)

    msg["From"] = MAILER['from']
    msg["To"] = MAILER['to']
    msg["Subject"] = subject

    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(MAILER['server'], MAILER['port'], context=context) as server:
        try:
            server.login(MAILER['from'], base64.b64decode(MAILER['passw']).decode("utf-8"))
            try:
                logger.info(f'Sending mail for {subject}')
                server.send_message(msg, MAILER['from'], MAILER['to'])
            except Exception as exp:
                logger.exception(exp)
        except Exception as exp:
            logger.exception(exp)

def main():
    """
    Main function.
    """

    logging.basicConfig(filename=CONFIG[SECTION]['log'],\
                    level=CONFIG[SECTION]['level'],\
                    format='%(asctime)s::%(name)s::%(funcName)s::%(levelname)s::%(message)s',\
                    datefmt="%Y-%m-%dT%H:%M:%S%z")

    logger.info("############# MAILER ##############")

    subject = "Karan Test."
    body = "content content content content content content content content"
    mailer(subject, body)

if __name__ == "__main__":
    main()
