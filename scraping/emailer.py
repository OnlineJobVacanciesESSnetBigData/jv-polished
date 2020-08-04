"""
A stub of code that could be extended to send emails, e.g. with diagnostic info about the daily scrape results.
"""

import mailjet_rest as mj
import scraping.support.log_helper as log_helper
from scraping.support.common import *


def emailer():
    api_key = os.environ['MAILJET_KEY']
    api_secret = os.environ['MAILJET_SECRET']
    mailjet = mj.Client(auth=(api_key, api_secret))

    html = '...construct an email here... e.g. by querying the Database where you stored the results for latest values'

    data = {
        'FromEmail': 'email@domain.com',
        'FromName': 'From ....',
        'Subject': 'Latest scraping results',
        'Html-part': html,
        'Recipients': [
            {
                "Email": "email1@domain.com",
                "Name": "Person 1"
            },
            {
                "Email": "email2@domain.com",
                "Name": "Person 2"
            }
        ]
    }

    mailjet.send.create(data=data)
    log_helper.deflog.info('Email sent')