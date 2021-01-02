#!./venv/bin/python

"""
Script to monitor a folder, send an email if changes detected.
"""

import configparser
import json
import logging
import sys
import time
import os
import subprocess

from pathlib import Path
import smtplib, ssl
from email.mime.text import MIMEText

from watchdog.events import LoggingEventHandler, PatternMatchingEventHandler
from watchdog.observers import Observer

#Define config and logger.
CONFIG = configparser.ConfigParser()
CONFIG.read("conf/config.ini")
SECTION = "watchdir"
PATH = CONFIG['global']['data']

MAILER = CONFIG['mailer']

logger = logging.getLogger(SECTION)

def mailer(subject, body):

    Message = f"{subject}\n\n{body}"
    msg = MIMEText(Message)


    msg["From"] = MAILER['from']
    msg["To"] = MAILER['to']

    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(MAILER['server'], MAILER['port'], context=context) as server:
        server.login(MAILER['from'], MAILER['passw'])

        try:
            server.send_message(msg, MAILER['from'], MAILER['to'])
        except Exception as exp:
            logger.exception(exp)


def unrar():

    logger.info(f"Unraring.")

    ff_command = [
        "unrar",
        "-u",
        "e",
        "*.rar",
        "-idq"
    ]

    logger.debug(" ".join(ff_command))

    _, error = subprocess.Popen(
        ff_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    ).communicate()

    logger.error(error.decode().strip())

def on_created(event):

    path = event.src_path

    subject = Path(path).name
    body = os.listdir(path)

    mailer(subject=subject, body=body)

    if os.path.isdir(path):
        logger.info(f"{path} created")
        os.chdir(path)
        unrar()
        logger.info("done")

def main():
    """
    Main function.
    """

    logging.basicConfig(filename=CONFIG[SECTION]['log'],\
                    level=CONFIG[SECTION]['level'],\
                    format='%(asctime)s::%(name)s::%(funcName)s::%(levelname)s::%(message)s',\
                    datefmt="%Y-%m-%dT%H:%M:%S%z")

    logger.info("############# STARTING ##############")

    patterns = "*"
    ignore_patterns = ""
    ignore_directories = False
    case_sensitive = True

    event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)
    event_handler.on_created = on_created

    #event_handler = LoggingEventHandler()

    observer = Observer()
    observer.schedule(event_handler, PATH)
    observer.start()
    try:
        while True:
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()

if __name__ == "__main__":
    main()

