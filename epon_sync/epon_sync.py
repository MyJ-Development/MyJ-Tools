import re
import mysql.connector
import logging
import time
import telnetlib
import re
from multiprocessing import Process, Manager

olt_list = {"172.16.50.111"}

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

def insertOltData(data):
    dataQuery = ''

    for i in data:
        if not "tx" in i:
            i["tx"] = ""
        if not "rx" in i:
            i["rx"] = ""
        dataQuery = dataQuery + f"""('{str(i["ip"])}','{str(i['mac'])}','{str(i['pon'])}','{i['slot']}','{str(i["rx"])}','{str(i["tx"])}'),"""
    dataQuery = dataQuery[:-1]
    userQuery = "insert into olt (ip_olt,mac_olt,pon,slot,rx,tx) values " + dataQuery +" ON DUPLICATE KEY UPDATE ip_olt = VALUES(ip_olt), mac_olt = VALUES(mac_olt),pon = VALUES(pon),slot = VALUES(slot),rx=VALUES(rx),tx=VALUES(tx);"
    result = 0
    MySQLInfo = MySQL_LOCAL()
    try:
        connection = mysql.connector.connect(host=MySQLInfo.host,
                                         database=MySQLInfo.database,
                                         user=MySQLInfo.user,
                                         password=MySQLInfo.password)
        cursor = connection.cursor()
        cursor.execute(userQuery)
        connection.commit()
        logging.info(str(cursor.rowcount)+" Cantidad de pppoe insertados correctamente en DB local: ")
        cursor.close()
        return 0

    except Exception as error:
        logging.error("Error en inserción de datos en DB local: "+str(error))
        return 1
        
def getEPON(address,queue):
    HOST = address
    user = b'admin'
    password = b'admin'
    try:
        tn = telnetlib.Telnet(HOST)
        tn.set_debuglevel(0)
        tn_read = tn.read_until(b'Login: ',10)
        tn.write(user+b'\n')
        tn_read = tn.read_until(b'admin\r\nPassword: ',10)
        tn.write(password+b'\n')
        tn_read = tn.read_until(b'\r\n\r\nepon-olt> ',10)
        tn.write(b'enable\n')
        tn_read = tn.read_until(b'Password: ',10)
        tn.write(password+b'\n')
        tn_read = tn.read_until(b'#',10)
        tn.write(b'config terminal\n')
        tn_read = tn.read_until(b'config terminal\r\nepon-olt(config)# ',10)
        logging.info("Conectado a OLT: "+address)
        olt_data = []
        for i in range (1,9):
            command = 'interface epon p1/'+str(i)+'\n'
            tn.write(command.encode("ascii"))
            tn_read = tn.read_until(b'#',100)
            command = 'show onu receive power polarity low\n'
            tn.write(command.encode("ascii"))
            tn_read = tn.read_until(b'#',100)
            response = tn_read.decode()
            response = response.split('\n')
            for line in response:
                rx = ""
                tx = ""
                find = re.compile(r'-.[0-9]+.[0-9]+')
                dbm = re.findall(find,line)
                find = re.compile(r'(EPON.[0-9]*/[0-9]*:[0-9]*)')
                pon = re.findall(find,line)
                re_mac = r"([0-9A-Fa-f]{2}(?::[0-9A-Fa-f]{2})+)\s+(-?\d+\.\d+)"
                mac = re.search(re_mac, line)
                if mac:
                    mac = mac.group(1)
                if(dbm and pon and mac):
                    rx = dbm[0]
                    pon = pon[0]
                    pon = str(pon).split(":")
                    slot = pon[1]
                    pon = str(pon[0]).split("/")
                    pon = pon[1]
                    mac = mac.replace(":","")
                    olt_data.append({"mac":mac.upper(),"pon":pon,"slot":slot,"rx":rx,"ip":address})
        logging.info("OLT: "+address+" - "+str(len(olt_data))+" ONUs")
    except Exception as e:
        logging.info("Error en OLT: "+address+" : "+str(e))
        return -1
    queue.put(olt_data)
    return 0
    

if __name__ == '__main__':
    logging.info("Iniciando proceso de sincronización de OLTs")
    processes = []
    manager = Manager()
    queue = manager.Queue()
    user_data = []
    for ip in olt_list:
        process = Process(target=getEPON, args=(ip, queue))
        processes.append((ip, process))

    start_times = {}

    for ip, process in processes:
        start_times[ip] = time.time()
        logging.info("Iniciando proceso para la IP {}".format(ip))
        process.start()

    for ip, process in processes:
        process.join()
        time_counter = time.time() - start_times[ip]
        logging.info("Tiempo de ejecución para la IP {}: {}".format(ip, time_counter))
        
    # Obtener los valores de retorno de la cola y agregarlos a la lista de resultados
    results = []
    while not queue.empty():
        result = queue.get()
        results.append(result)
    for result in results:
        for i in result:
            user_data.append(i)
    exit(insertOltData(user_data))