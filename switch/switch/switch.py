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

def getStatus(index,ip):
    community='public'
    if(index==1):
        value=(1,3,6,1,4,1,33826,1,1,5,1,2,1)
    else:
        value=(1,3,6,1,4,1,33826,1,1,5,1,2,2)

    generator = cmdgen.CommandGenerator()
    comm_data = cmdgen.CommunityData('server', community, 1) # 1 means version SNMP v2c
    transport = cmdgen.UdpTransportTarget((ip, 161))

    real_fun = getattr(generator, 'getCmd')
    res = (errorIndication, errorStatus, errorIndex, varBinds)\
        = real_fun(comm_data, transport, value)

    if not errorIndication is None  or errorStatus is True:
        print("Error: %s %s %s %s" % res)
    else:
        #print("%s" % varBinds)
            for line in res[3]:
                line = str(line).split("=")
                line = str(line[1]).replace(" ","")
                return line

async def run():
    
    ip_list  = {"172.16.50.201","192.168.200.22","192.168.200.23"}
    bot = telegram.Bot("5753479653:AAFpNG9ip59sgl2UVDPxDRzmNaL9DJTmO_A")
    while(True):
        for ip in ip_list:
            response = 0
            try:
                response = int(getStatus(1,ip))
                print(response)
            except:
                response = int(0)
            if(response<-70):
                response = str(response)
                response = response[:-1] + '.' + response[-1:]
                #print("IP: 172.16.50.201 Index 1: "+ str(response)+" dBm")
                try:
                    async with bot:
                        message = "Problema en Fibra TV IP: "+str(ip)+" Fibra 1: "+ str(response)+" dBm"
                        await bot.send_message(text=message, chat_id=-1001547382511)
                except:
                    print("Error Telegram Fibra 1: "+str(ip)+" : "+str(e))
            try:
                response = int(getStatus(2,ip))
            except:
                response = int(0)
            if(response<-70):
                response = str(response)
                response = response[:-1] + '.' + response[-1:]
                try:
                    async with bot:
                        message = "Problema en Fibra TV IP: "+str(ip)+" Fibra 2: "+ str(response)+" dBm"
                        await bot.send_message(text=message, chat_id=-1001547382511)
     
                except Exception as e:
                    print("Error Telegram Fibra 2: "+str(ip)+" : "+str(e))
            time.sleep(5)
        time.sleep(3600)

if __name__ == '__main__':
    asyncio.run(run())
