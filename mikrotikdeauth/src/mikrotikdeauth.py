import mysql.connector
import datetime
from routeros_api import Api
import routeros_api
import json
from hurry.filesize import size, si
import re
import logging
from logging.config import dictConfig
import time
import threading
import sys
import telnetlib
import re
import multiprocessing


class MySQL_LOCAL:
  def __init__(self):
    self.host = '10.19.11.9'
    self.user = 'myjdev'
    self.password = 'myjdev'
    self.database = 'olt_sync'

class MySQL_ISPCUBE:
  def __init__(self):
    self.host = '170.239.188.10'
    self.user = 'myjdev'
    self.password = '2020myjdev'
    self.database = '105'

def getISPCUBE():
    userQuery = "select radiususer from customer join connections on connections.idcustomer=customer.idcustomer where status=1 and radiususer is not null"
    result = 0
    MySQLInfo = MySQL_ISPCUBE()
    try:
        connection = mysql.connector.connect(host=MySQLInfo.host,
                                         database=MySQLInfo.database,
                                         user=MySQLInfo.user,
                                         password=MySQLInfo.password)
        cursor = connection.cursor()
        cursor.execute(userQuery)
        result = cursor.fetchall()
        cursor.close()
        connection.close()
    except mysql.connector.Error as error:
        print("Fallo en obtener datos desde ISPCube  {}".format(error))
    
    return result

def getPPPoEData(pppoe):
    userQuery = "select ip from mikrotik where mikrotik_pppoe='"+pppoe+"';"
    result = 0
    MySQLInfo = MySQL_LOCAL()
    try:
        connection = mysql.connector.connect(host=MySQLInfo.host,
                                         database=MySQLInfo.database,
                                         user=MySQLInfo.user,
                                         password=MySQLInfo.password)
        cursor = connection.cursor()
        cursor.execute(userQuery)
        result = cursor.fetchall()
        cursor.close()
    except mysql.connector.Error as error:
        logging.error("Fallo en obtener datos desde ISPCube  {}".format(error))

    return result

def readIP(pppoeList):
    response = []
    p = []
    i=0
    ipList = open("ipList.txt","r")
    response = []
    for ip in ipList:
        p.append(multiprocessing.Process(target=sendDeAuth, args=(ip[:-1],pppoeList,)))
        p[i].start()
        i=i+1
    ipList.close

    for k in range(i):
        p[k].join()

def readIPWireless(pppoeList):
    response = []
    p = []
    i=0
    ipList = open("ipListWireless.txt","r")
    response = []
    for ip in ipList:
        p.append(multiprocessing.Process(target=sendDeAuth, args=(ip[:-1],pppoeList,)))
        p[i].start()
        i=i+1
    ipList.close

    for k in range(i):
        p[k].join()

def sendDeAuth(address,pppoeList):
    try:
        router = Api(address, user='kevins', password='123456', port=28728)
        #r = router.talk('/ppp/active/print')
        r = router.talk('/interface/pppoe-server/print')
    except Exception as error:
        print("Error en MK: "+str(address)+ " : "+ str(error))
    counter = 0
    for line in r:
        line=json.dumps(line,indent=4)
        data=json.loads(line)
        found = [x for x in pppoeList if str(x[0]) == str(data["user"])]
        if(found):
            #print(data[".id"]+" "+data["user"])
            try: 
                router.talk('/interface/pppoe-server/remove\n=.id='+data[".id"])
                counter = counter + 1
            except Exception as e:
                print("Error!: "+str(e))

    print(str(counter)+" Cantidad de Usuarios Desauntenticados "+" IP: "+address)

if __name__ == "__main__":
    deudores = getISPCUBE()
    readIP(deudores)
    readIPWireless(deudores)
