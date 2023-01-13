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

def linkCheck(linkList):
    try:
        router = Api('192.168.99.154', user='grafana', password='123456', port=28728)
        #r = router.talk('/ppp/active/print')
        r = router.talk('/interface/ethernet/print')
        for line in r:
            line=json.dumps(line,indent=4)
            data=json.loads(line)
            obj = []
            try:
                obj.append(str(data["comment"]))
                obj.append(str(data[".id"]))
                print(obj)
                if(data["running"] == "true" and obj in linkList):
                    print("LinkUp! " + " ID: "+data[".id"]+" Interface: "+data["name"] + " Comment: "+data["comment"])
                elif(data["running"] == "false" and obj in linkList):
                    print("LinkDown! " + " ID: "+data[".id"]+" Interface: "+data["name"] + " Comment: "+data["comment"])
            except Exception as e:
                print(e)
                pass
    except Exception as error:
        print("Error en MK: "+str('192.168.99.154')+ " : "+ str(error))

if __name__ == "__main__":
    linkList = [('Level3 - router CR1072',"*2"),('Level3 - router CR1072',"*3"),
               ("Troncal Switch Quilicura CRS","*8"),("Troncal Switch Quilicura CRS","*9")]
    linkCheck(linkList)