import os, sys
import socket
import random
from struct import pack, unpack
from datetime import datetime as dt
import time
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.proto.rfc1902 import Integer, IpAddress, OctetString
import telegram
import telebot
import threading
import asyncio
import logging

log_file = "log.txt"
logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file)
        ]
    )

def getStatus(index,ip):
    community='public'
    if(index==1):
        value=(1,3,6,1,4,1,33826,1,1,5,1,2,1)
    else:
        value=(1,3,6,1,4,1,33826,1,1,5,1,2,2)

    generator = cmdgen.CommandGenerator()
    comm_data = cmdgen.CommunityData('server', community, 1) # 1 means version SNMP v2c
    transport = cmdgen.UdpTransportTarget((ip, 161))
    res = ''
    try:
        real_fun = getattr(generator, 'getCmd')
        res = (errorIndication, errorStatus, errorIndex, varBinds)\
            = real_fun(comm_data, transport, value)
    except Exception as e:
        logging.error("Excepcion: "+str(e))
        return -999
    logging.info(res)
    if not errorIndication is None  or errorStatus is True:
        logging.error("Error: %s %s %s %s" % res)
        return -999
    else:
        #logging.info("%s" % varBinds)
            for line in res[3]:
                line = str(line).split("=")
                line = str(line[1]).replace(" ","")
                return line
    return -999

async def run():

    ip_list  = {"172.16.50.201","192.168.200.22","192.168.200.23","192.168.11.22"}
    bot = telegram.Bot("5753479653:AAFpNG9ip59sgl2UVDPxDRzmNaL9DJTmO_A")
    while(True):
        for ip in ip_list:
            response = 0
            try:
                response = int(getStatus(1,ip))
                logging.info(response)
                if(response == -999):
                    response = 0
                    async with bot:
                        message = "Problema en SwitchTV IP: "+str(ip)+" No Responde SNMP!"
                        await bot.send_message(text=message, chat_id=-1001547382511)
            except:
                async with bot:
                        message = "Problema en SwitchTV IP: "+str(ip)+" error no controlado"
                        await bot.send_message(text=message, chat_id=-1001547382511)


            if(response<-80):
                response = str(response)
                response = response[:-1] + '.' + response[-1:]
                #logging.info("IP: 172.16.50.201 Index 1: "+ str(response)+" dBm")
                try:
                    async with bot:
                        message = "Problema en Fibra TV IP: "+str(ip)+" Fibra 1: "+ str(response)+" dBm"
                        await bot.send_message(text=message, chat_id=-1001547382511)
                except:
                    logging.error("Error Telegram Fibra 1: "+str(ip)+" : "+str(e))
            try:
                response = int(getStatus(2,ip))
                if(response == -999):
                    response = 0
                    async with bot:
                        message = "Problema en SwitchTV IP: "+str(ip)+" No Responde SNMP!"
                        await bot.send_message(text=message, chat_id=-1001547382511)
            except:
                async with bot:
                        message = "Problema en SwitchTV IP: "+str(ip)+" error no controlado"
                        await bot.send_message(text=message, chat_id=-1001547382511)
            if(response<-80):
                response = str(response)
                response = response[:-1] + '.' + response[-1:]
                try:
                    async with bot:
                        message = "Problema en Fibra TV IP: "+str(ip)+" Fibra 2: "+ str(response)+" dBm"
                        await bot.send_message(text=message, chat_id=-1001547382511)

                except Exception as e:
                    logging.error("Error Telegram Fibra 2: "+str(ip)+" : "+str(e))
            time.sleep(5)
        time.sleep(3600)

if __name__ == '__main__':
    asyncio.run(run())
