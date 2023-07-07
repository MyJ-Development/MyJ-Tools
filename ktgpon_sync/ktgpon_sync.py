import re
import mysql.connector
import logging
import time
import telnetlib
import re

olt_list = ["172.16.50.121","172.16.50.126","172.16.50.127","172.16.50.130","172.16.152.150"]

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
        
def getKTGPON(address):
    HOST = address
    user = b'admin'
    password = b'admin'
    try:
        tn = telnetlib.Telnet(HOST)
        tn.set_debuglevel(0)
        
        tn_read = tn.read_until(b'login:',10)
        tn.write(b'\n')
        tn_read = tn.read_until(b'username:',10)
        tn.write(user+b'\n')
        tn_read = tn.read_until(b'Password:',10)
        tn.write(password+b'\n')
        tn_read = tn.read_until(b'>',10)
        data = []
        logging.info("Conectado a OLT: "+address)
        tn.write(b"show gpon-onu optical-info all\na")
        time.sleep(90)
        respuesta_telnet = tn.read_until(b'>',10).decode('utf-8', errors='ignore')
        position_data = respuesta_telnet.split('-------------------------------------------')
        values = {}
        onu_data = []
        for i in position_data:
            match = re.search(r'ONU ID\s+:\s+(.*?)\n', i)
            error = ""
            values = {}
            if match:
                onu_id= match.group(1)
                values['pon'] = onu_id.replace('g2/', '').replace("\r","").split(":")[0]
                values['slot'] = onu_id.replace('g2/', '').replace("\r","").split(":")[1]
            else:
                error = 1
            match = re.search(r'tx power\s+:\s+([0-9.-]+)\s+\(dbm\)', i)
            if match:
                values['tx'] = match.group(1)
            else:
                error = 1

            match = re.search(r'rx power\s+:\s+(.*?)\s+\(dbm\)', i)
            if match:
                values['rx'] = match.group(1)
            else:
                error = 1
            if error == "":
                onu_data.append(values)
        tn.write(b"show gpon-onu register-info all\na")
        time.sleep(45)
        respuesta_telnet = tn.read_until(b'>',10).decode('utf-8', errors='ignore')
        position_data = respuesta_telnet.split('\n')
        re_onuid = r"\w+/\w+:\w+"
        re_mac = r"([A-Za-z0-9]{12})"
        mac_data = []
        #print(position_data)
        for i in position_data:
            resultado = re.search(re_onuid, i)
            if resultado:
                onu_id = resultado.group(0)
                pon = onu_id.replace('g2/', '').replace("\r","").split(":")[0]
                slot = onu_id.replace('g2/', '').replace("\r","").split(":")[1]

            resultado = re.search(re_mac, i)
            if resultado:
                mac = resultado.group(0)
                #find index in onu_data when pon and slot match with onu_data[pon] and onu_data[slot], then add mac to onu_data[index]
                mac_data.append({'mac':mac,'pon':pon,'slot':slot})

        #iterate onu_data and add mac  at same time
        output = []
        for i in onu_data:
            for j in mac_data:
                if i['pon'] == j['pon'] and i['slot'] == j['slot']:
                    i['mac'] = j['mac']
                    i["ip"] = address
                    output.append(i)
    except Exception as e:
        logging.error("Error when getting data: "+str(address)+", "+str(e))
        return -1
    return output

if __name__ == '__main__':
    user_data = []
    results = []
    error = 0
    for ip in olt_list:
        response = getKTGPON(ip)
        if response == -1:
            logging.error("Error when getting data from OLT: "+str(ip))
            error = 1
        else:
            logging.info("Data from OLT: "+str(ip)+", "+str(len(response))+" ONUs")
            results.append(response)
            
    for result in results:
        for i in result:
            user_data.append(i)
    if error:
        insertOltData(user_data)
        exit(1)
    else:
        exit(insertOltData(user_data))  