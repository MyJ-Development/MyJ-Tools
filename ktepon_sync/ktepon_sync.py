import re
import mysql.connector
import logging
import logging
import time
import sys
import telnetlib
import re
from multiprocessing import Process, Manager

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

olt_list = {"172.16.50.100","172.16.50.104","172.16.50.105","172.16.50.106","172.16.50.107","172.16.50.125"}

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

def getKTEpon(ip,queue):
    tn = telnetlib.Telnet(ip)
    tn.set_debuglevel(0)
    tn_read = tn.read_until(b'login:',10)
    tn.write(b'\n')
    tn_read = tn.read_until(b'username:',10)
    tn.write(b'admin\n')
    tn_read = tn.read_until(b'Password:',10)
    tn.write(b'admin\n')
    tn_read = tn.read_until(b'>',10)
    logging.info("Conectado a OLT: "+ip)
    olt_data = []
    tn.write(b"show onu-list-info\na")
    time.sleep(90)
    respuesta_telnet = tn.read_until(b'>',10).decode('utf-8', errors='ignore')
    position_data = respuesta_telnet.split('\n')
    patron = r"\d+/\d+:\d+"
    for line in position_data:
        match = re.search(patron, line)
        if match:
            match = match.group()
            command = f"show onu dev-info p{match}\n"
            tn.write(command.encode('ascii'))
            tn.write(b"\n\n\n\n\n\n\n\n")
            respuesta_telnet = tn.read_until(b'>',10)
            try:
                respuesta_telnet_decoded = respuesta_telnet.decode('utf-8', errors='ignore')
                if "Invalid" in respuesta_telnet_decoded:
                    logging.error("Error en comando a OLT: "+ip)
                    break                
            except UnicodeDecodeError:
                respuesta_telnet_decoded = respuesta_telnet.decode('latin-1', errors='ignore')
                if "Invalid" in respuesta_telnet_decoded:
                    logging.error("Error en comando a OLT: "+ip)
                    break
            except Exception as e:
                logging.error(e)
                logging.error("Error en comando a OLT: "+ip)
            patron_mac_address = r"mac address:\s*([A-Fa-f0-9\.]+)"
            patron_transmitted_power = r"transmitted optical power:\s*[\d\.]+\s+mW\s*([\d\.]+)\s+dbm"
            patron_received_power = r"received optical power:\s*[\d\.]+\s+mW\s*([\d\.]+|-[\d\.]+)\s+dbm"
            mac_address = ""
            received_power = ""
            transmitted_power = ""
            try:
                mac_address = re.search(patron_mac_address, respuesta_telnet_decoded).group(1)
                transmitted_power = re.search(patron_transmitted_power, respuesta_telnet_decoded).group(1)
                received_power = re.search(patron_received_power, respuesta_telnet_decoded).group(1)
            except Exception as e:
                received_power = "0"
                transmitted_power = "0"

            if(mac_address):
                pon = match.split(":")[0].split("/")[1]
                slot = match.split(":")[1]
                olt_data.append({"ip":ip,"mac":mac_address.replace(".","").upper(),"pon":pon,"slot":slot,"rx":received_power,"tx":transmitted_power})

    onu_counter = olt_data.__len__()
    if(onu_counter>0):
        logging.info("OLT: "+ip+" ONUs: "+str(onu_counter))
        queue.put(olt_data)
        return 0
        
    else:
        logging.error("Error en OLT: "+ip+" ONUs: "+str(onu_counter))
        return -1
            
if __name__ == '__main__':
    logging.info("Iniciando proceso de sincronización de OLTs")
    processes = []
    manager = Manager()
    queue = manager.Queue()
    user_data = []
    for ip in olt_list:
        process = Process(target=getKTEpon, args=(ip, queue))
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