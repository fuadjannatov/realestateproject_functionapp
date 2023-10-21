import datetime
import logging
from pkg_resources import run_script

import sys
import os
import importlib.util

import azure.functions as func

#from . import Credentials, DB_connection, Scraper

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()
    runner_function('DB_connection')
    logging.info('Python timer trigger function ran at %s', utc_timestamp)


def runner_function(sn):
    sp = os.path.join(os.path.dirname(__file__), f'{sn}.py')

    s = importlib.util.spec_from_file_location(sn, sp)
    m = importlib.util.module_from_spec(s)
    sys.modules[s.name] = m
    s.loader.exec_module(m)