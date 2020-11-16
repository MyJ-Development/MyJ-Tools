import os, sys
import socket
import random
from struct import pack, unpack
from datetime import datetime as dt
import time
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.proto.rfc1902 import Integer, IpAddress, OctetString
import telegram

bot = telegram.Bot(token='1294153119:AAHMZc8qNx2QhlLK5FSD9rMsp_mpkX-MSOs')


def getStatus(index):
    ip='172.16.50.201'
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

def main():
    while(True):
        response = 0
        try:
            response = int(getStatus(1))
        except:
            response = int(0)
        if(response<30):
            response = str(response)
            response = response[:-1] + '.' + response[-1:]
            #print("IP: 172.16.50.201 Index 1: "+ str(response)+" dBm")
            try:
                bot.sendMessage(-498052465,"Problema en Fibra Maipu IP: 172.16.50.201 Fibra 1: "+ str(response)+" dBm")
            except:
                print("Error Telegram")
        try:
            response = int(getStatus(2))
        except:
            response = int(0)
        if(response<30):
            response = str(response)
            response = response[:-1] + '.' + response[-1:]
            try:
                bot.sendMessage(-498052465,"Problema en Fibra Fibra Maipu IP: 172.16.50.201 Fibra 2: "+ str(response)+" dBm")
            except:
                print("Error Telegram")
        time.sleep(3600)

main()