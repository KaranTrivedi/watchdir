#!./venv/bin/python

"""
Docstring should be written for each file.
run `pylint filename.py` to find recommendations on improving format.
"""
import configparser
import json
import logging

#Define config and logger.
CONFIG = configparser.ConfigParser()
CONFIG.read("conf/config.ini")
SECTION = "watchdir"

logger = logging.getLogger(SECTION)

class Watchdir:
    """
    Create sample class
    """

    def __init__(self, var):
        self.var = var

    def __str__(self):
        """
        stringify
        """
        return json.dumps(vars(self), indent=2)


def main():
    """
    Main function.
    """

    logging.basicConfig(filename=CONFIG[SECTION]["log"],
                    level=CONFIG[SECTION]["level"],
                    format="%(asctime)s::%(name)s::%(funcName)s::%(levelname)s::%(message)s",
                    datefmt="%Y-%m-%dT%H:%M:%S%z")

    logger.info("####################STARTING####################")

if __name__ == "__main__":
    main()
