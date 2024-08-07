import socket
import re
import mysql.connector
import datetime
import queue
import threading
import logging
import time

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

class MySQL_LOCAL:
  def __init__(self):
    self.host = '10.19.11.2'
    self.user = 'myjdev'
    self.password = 'myjdev'
    self.database = 'olt_sync'

def insertLogMikrotik(data,address,online):
    logDate = datetime.datetime.today()
    logDate = datetime.datetime(logDate.year, logDate.month, logDate.day,logDate.hour,logDate.minute)
    logDate = str(logDate)

    dataQuery = ''
    dataQuery = dataQuery + "('"+str(address)+ "','"+data.lower()+ "','"+str(online)+"','"+logDate+"'),"

    dataQuery = dataQuery[:-1]
    userQuery = "insert ignore into log (address,log_pppoe,online,last_connection) values " + dataQuery +" ON DUPLICATE KEY UPDATE address = VALUES(address),log_pppoe = VALUES(log_pppoe), online = VALUES(online), last_connection = VALUES(last_connection);"
    result = 0
    #logging.info(userQuery)
    MySQLInfo = MySQL_LOCAL()
    try:
        connection = mysql.connector.connect(host=MySQLInfo.host,
                                         database=MySQLInfo.database,
                                         user=MySQLInfo.user,
                                         password=MySQLInfo.password)
        cursor = connection.cursor()
        cursor.execute(userQuery)
        connection.commit()
        #logging.info(str(data))
        cursor.close()
    except mysql.connector.Error as error:
        #logging.error("Fallo en insertar en DB Local  {}".format(error))
        return -1
    except Exception as error:
        #logging.error("Fallo  en DB Local  {}".format(error))
        return -1
    return 0



localIP     = "10.19.11.2"
localPort   = 514
bufferSize  = 1024
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket.bind((localIP, localPort))
BUF_SIZE = 10000
q = queue.Queue(BUF_SIZE)
logging.info("UDP server up and listening")

log = {"pppoe":"","ip":"","online":""}
connected = re.compile(r' connected')
disconnected = re.compile(r' disconnected')
findpppoe = re.compile(r'[0-9A-Za-z]*>')
findip = re.compile(r'[0-9]+.[0-9]+.[0-9]+.[0-9]')

class ProducerThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        super(ProducerThread,self).__init__()
        self.target = target
        self.name = name

    def run(self):
        while True:
            bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
            clientMsg = str(bytesAddressPair[0])
            clientIP = str(bytesAddressPair[1])
            online = re.findall(connected,clientMsg)
            offline = re.findall(disconnected,clientMsg)
            pppoe = re.findall(findpppoe,clientMsg)
            if(online and pppoe):
                online = online[0]
                pppoe = pppoe[0]
                pppoe = pppoe[:-1]
                ip = re.findall(findip,clientIP)
                ip = ip[0]
                log["pppoe"] = pppoe
                log["ip"] = ip
                log["online"] = 1
                q.put(log)
                #logging.info("log added: "+str(log))
            if(offline and pppoe):
                offline = offline[0]
                pppoe = pppoe[0]
                pppoe = pppoe[:-1]
                ip = re.findall(findip,clientIP)
                ip = ip[0]
                log["pppoe"] = pppoe
                log["ip"] = ip
                log["online"] = 0
                q.put(log)
                #logging.info("log added: "+str(log))
                #logging.info("Disconnected: "+str(pppoe)+ " Address: "+str(ip))
                #insertLogMikrotik(pppoe,ip,"0")
        return

class ConsumerThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        super(ConsumerThread,self).__init__()
        self.target = target
        self.name = name
        return

    def run(self):
        while True:
            if not q.empty():
                item = q.get()
                #logging.info("q: "+str(item['pppoe']))
                #logging.info(item)
                while True:
                    response = insertLogMikrotik(item['pppoe'],item['ip'],item['online'])
                    if(response == 0):
                        break
                    else:
                        time.sleep(0.2)
        return

if __name__ == '__main__':

    p = ProducerThread(name='producer')
    c = ConsumerThread(name='consumer')

    p.start()
    c.start()
