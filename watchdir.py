#!./venv/bin/python

"""
Script to monitor a folder, send an email if changes detected.
"""

import base64
import configparser
import logging
import os
import smtplib
import ssl
import subprocess
import time
from email.mime.text import MIMEText
from pathlib import Path

from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

from libs import mailer_calls

#Define config and logger.
CONFIG = configparser.ConfigParser()
CONFIG.read("conf/config.ini")
SECTION = "watchdir"
PATH = CONFIG['global']['data']

MAILER = CONFIG['mailer']

logger = logging.getLogger(SECTION)

def unrar():
    """
    Run command in directory where change is detected.
    """

    logger.info("Unraring.")

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
    """
    This function will be called on detection of changes to monitored folder with event data.
    """

    logger.info(event)
    logger.info(type(event))

    path = event.src_path

    subject = Path(path).name

    if os.path.isdir(path):
        body = "\n".join(os.listdir(path))
        body += "\n" + f"http://192.168.0.16:4201/directory/downloads/{subject}?sort=desc&column=modify_time&query="
        logger.info(f"{path} created")
        os.chdir(path)
        unrar()
        logger.info("done")
    else:
        body = ""

    mailer_calls.mailer(subject=subject, body=body)

def main():
    """
    Main function.
    """

    logging.basicConfig(filename=CONFIG[SECTION]['log'],\
                    level=CONFIG[SECTION]['level'],\
                    format='%(asctime)s::%(name)s::%(funcName)s::%(levelname)s::%(message)s',\
                    datefmt="%Y-%m-%dT%H:%M:%S%z")

    logger.info("############# Starting watcher ##############")

    patterns = "*"
    ignore_patterns = ""
    ignore_directories = False
    case_sensitive = True

    event_handler = PatternMatchingEventHandler(patterns,
                                                ignore_patterns,
                                                ignore_directories,
                                                case_sensitive
                                                )
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
