import os
from multiprocessing import Process
import telegram
import logging
from logging.config import dictConfig
import time
import datetime

LOGGING_CONFIG = {
    'version': 1,
    'loggers': {
        '': {  # root logger
            'level': 'NOTSET',
            'handlers': ['debug_console_handler', 'info_rotating_file_handler', 'error_file_handler', 'critical_mail_handler'],
        },
        'my.package': { 
            'level': 'WARNING',
            'propagate': False,
            'handlers': ['info_rotating_file_handler', 'error_file_handler' ],
        },
    },
    'handlers': {
        'debug_console_handler': {
            'level': 'DEBUG',
            'formatter': 'info',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
        'info_rotating_file_handler': {
            'level': 'INFO',
            'formatter': 'info',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'info.log',
            'mode': 'a',
            'maxBytes': 1048576,
            'backupCount': 10
        },
        'error_file_handler': {
            'level': 'WARNING',
            'formatter': 'error',
            'class': 'logging.FileHandler',
            'filename': 'error.log',
            'mode': 'a',
        },
        'critical_mail_handler': {
            'level': 'CRITICAL',
            'formatter': 'error',
            'class': 'logging.handlers.SMTPHandler',
            'mailhost' : 'localhost',
            'fromaddr': 'monitoring@domain.com',
            'toaddrs': ['dev@domain.com', 'qa@domain.com'],
            'subject': 'Critical error with application name'
        }
    },
    'formatters': {
        'info': {
            'format': '%(asctime)s-%(levelname)s-%(name)s::%(module)s|%(lineno)s:: %(message)s'
        },
        'error': {
            'format': '%(asctime)s-%(levelname)s-%(name)s-%(process)d::%(module)s|%(lineno)s:: %(message)s'
        },
    },}

bot = telegram.Bot(token='1294153119:AAHMZc8qNx2QhlLK5FSD9rMsp_mpkX-MSOs')

def main():
    status = []
    hostname = []
    hostcheck = []
    dictConfig(LOGGING_CONFIG)
    ip_file = open('ip.txt','r')
    for line in ip_file:
        hostname.append(str(line))
        hostcheck.append({"status":0,"counter":0,"date":""})

    while(True):
        i  = 0
        for line in hostname:
            line = line.split(",")
            ip = line[0]
            info = line[1]
            response = -1
            try: 
                response = os.system("ping -c 5 " + ip)
            except:
                response = -1

            if(response==0):
                #-423452442
                #-498052465
                if(hostcheck[i]['status'] == 1):
                    bot.sendMessage(-498052465,"Servicio: "+ info +" "+ip+" Se ha reconectado!")
                    hostcheck[i]['status'] = 0
                    hostcheck[i]['counter'] = 0

            if(response != 0 and hostcheck[i]['status']==0):
                bot.sendMessage(-498052465,"Servicio: "+ info +" "+ip+" Ha caido!")
                hostcheck[i]['status'] = 1

            if(hostcheck[i]['status'] == 1):
                if(hostcheck[i]['counter']==0):
                    logDate = datetime.datetime.utcnow() +datetime.timedelta(hours=-8)
                    logDate = datetime.datetime(logDate.year, logDate.month, logDate.day,logDate.hour,logDate.minute)
                    hostcheck[i]['date'] = logDate
                hostcheck[i]['counter'] = 1 + hostcheck[i]['counter']
                if(hostcheck[i]['counter']>30):
                    bot.sendMessage(-498052465,"Servicio: "+ info +" "+ip+" Caido desde: "+str(hostcheck[i]['date']))
                    hostcheck[i]['counter'] = 1
            i = i + 1

main()
