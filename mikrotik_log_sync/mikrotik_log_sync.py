import json
import ros_api 
import logging
import mysql.connector
import time
from datetime import datetime, timedelta
import re


class MySQL_LOCAL:
  def __init__(self):
    self.host = '10.19.11.2'
    self.user = 'myjdev'
    self.password = 'myjdev'
    self.database = 'olt_sync'

class MySQL_ISPCUBE:
  def __init__(self):
    self.host = '170.239.188.10'
    self.user = 'myjdev'
    self.password = '2020myjdev'
    self.database = '105'
    
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

ip_list = [
    "10.113.113.11",
    "10.113.113.12",
    "10.113.113.15",
    "10.113.113.16",
    "10.113.113.17",
    "10.113.113.19",
    "10.113.113.21",
    "10.113.113.24",
    "10.113.113.25",
    "10.113.113.28",
    "10.113.113.31",
    "10.113.113.8",
    "10.119.119.18",
    "10.119.119.19",
    "10.119.119.35",
    "10.119.119.26",
    "10.119.119.32",
    "10.119.119.33",
    "10.119.119.25",
    "10.119.119.34",
    "10.121.121.10",
    "10.121.121.3",
    "10.121.121.4",
    "10.121.121.6",
    "10.121.121.7",
    "10.121.121.8",
    "10.121.121.5"
]

def convertir_tiempo(tiempo):
    # Extraer los componentes de tiempo usando expresiones regulares
    semanas_match = re.search(r'(\d+)w', tiempo)
    horas_match = re.search(r'(\d+)h', tiempo)
    minutos_match = re.search(r'(\d+)m', tiempo)
    segundos_match = re.search(r'(\d+)s', tiempo)

    semanas = int(semanas_match.group(1)) if semanas_match else 0
    horas = int(horas_match.group(1)) if horas_match else 0
    minutos = int(minutos_match.group(1)) if minutos_match else 0
    segundos = int(segundos_match.group(1)) if segundos_match else 0

    # Calcular el total de segundos
    total_segundos = (semanas * 7 * 24 * 60 * 60) + (horas * 60 * 60) + (minutos * 60) + segundos

    # Obtener la fecha y hora actual
    fecha_actual = datetime.now()

    # Calcular la nueva fecha y hora sumando los segundos
    nueva_fecha = fecha_actual - timedelta(seconds=total_segundos)
    # Formatear la nueva fecha en el formato deseado
    fecha_formateada = nueva_fecha.strftime("%Y-%m-%d %H:%M:%S")
    
    return fecha_formateada

def insertLog(data):
    dataQuery = ''
    for i in data:
        dataQuery = dataQuery + f"""('{str(i["address"])}','{i["pppoe"]}','{i["online"]}','{str(i["last_connection"])}'),"""
    dataQuery = dataQuery[:-1]
    userQuery = "insert into log (address,log_pppoe,online,last_connection) values " + dataQuery +" ON DUPLICATE KEY UPDATE address = VALUES(address),log_pppoe = VALUES(log_pppoe), online = VALUES(online),last_connection = VALUES(last_connection);"
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
        logging.info(str(cursor.rowcount)+" Usuarios validados en Log: ")
        cursor.close()
    except mysql.connector.Error as error:
        logging.error("Fallo en insertar en DB Local  {}".format(error))
        return -1
    return 0

def getMikrotik(ip,pppoe_list):
    api_username = 'kevins'
    api_password = 'kevins'
    api_port = 28728
    #logging.info("Connecting to " + ip)
    pppoe_log = []
    try:
        router = ros_api.Api(ip,user=api_username,password=api_password, port=api_port)
    except Exception as e:
        logging.error("User or password is wrong: "+str(ip))
        return -1
    try:
        r = router.talk('/ppp/active/print')
        for i in r:

            pppoe_log.append({"address":ip,"uptime":convertir_tiempo(i["uptime"]),"pppoe":i["name"].lower(),"online":"1"})
    except Exception as e:
        logging.error("Error when getting data: "+str(ip)+", "+str(e))
        return -1
    #logging.info("Data from "+ip+" is ready, count: "+str(len(pppoe_log)))
    return pppoe_log

def getISPCUBE():
    userQuery = "select * from log"
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
        logging.error("Fallo en obtener datos desde LOCAL  {}".format(error))
        return -1
    return result

if __name__ == "__main__":
    user_data = []
    error = 0
    response = getISPCUBE()
    pppoe_list = []
    pppoe_validator = []
    for i in response:
        pppoe_list.append({"pppoe":i[0].lower(),"active":i[1],"address":i[3],"last_connection":i[2]})
    for ip in ip_list:
        response = getMikrotik(ip,pppoe_list)
        if response == -1:
            logging.error("Error when getting data from "+ip)
            error = 1
        else:
            for i in response:
                pppoe_validator.append(i)
    for i in pppoe_list:
        if i["pppoe"] not in [j["pppoe"] for j in pppoe_validator]:
            if(i["active"]==1):
                user_data.append({"address":i["address"],"pppoe":i["pppoe"],"online":"0","last_connection":datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            else:
                #user_data.append({"address":i["address"],"pppoe":i["pppoe"],"online":"0","last_connection":i["last_connection"]})
                pass
        if i["pppoe"] in [j["pppoe"] for j in pppoe_validator]:
            if(i["active"]==0):
                index = [j["pppoe"] for j in pppoe_validator].index(i["pppoe"])
                user_data.append({"address":pppoe_validator[index]["address"],"pppoe":i["pppoe"],"online":"1","last_connection":pppoe_validator[index]["uptime"]})
            else:
                #index = [j["pppoe"] for j in pppoe_validator].index(i["pppoe"])
                #user_data.append({"address":i["address"],"pppoe":i["pppoe"],"online":"1","last_connection":pppoe_validator[index]["uptime"]})
                pass
    if error:
        if(len(user_data)>0):
            insertLog(user_data)
            exit(1)
    else:
        if(len(user_data)>0):
            exit(insertLog(user_data))  

    
