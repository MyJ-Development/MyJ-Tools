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
hostname = []
def main():
    status = []
    dictConfig(LOGGING_CONFIG)
    ip_file = open('ip.txt','r')
    for line in ip_file:
        hostname.append(str(line))
        
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
            #bot.sendMessage(-498052465,"Servicio "+ip+" online!")
            logDate = datetime.datetime.today()
            logDate = datetime.datetime(logDate.year, logDate.month, logDate.day,logDate.hour,logDate.minute)
            logging.info("Servicio ("+info+") "+"online: "+ip+ " : "+str(logDate))
        else:
            bot.sendMessage(-498052465,"Servicio "+ info +" "+ip+" offline!")
            logDate = datetime.datetime.today()
            logDate = datetime.datetime(logDate.year, logDate.month, logDate.day,logDate.hour,logDate.minute)
            logging.error("Error en servicio: "+ip+ " : "+str(logDate))
    main()
main()
