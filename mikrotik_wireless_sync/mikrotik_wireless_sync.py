import json
import ros_api 
import re
import logging
import mysql.connector
import time

class MySQL_LOCAL:
  def __init__(self):
    self.host = '10.19.11.2'
    self.user = 'myjdev'
    self.password = 'myjdev'
    self.database = 'olt_sync'

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

ip_list = {
    "10.113.113.12",
    "10.113.113.15",
    "10.113.113.16",
    "10.113.113.17",
    "10.113.113.19",
    "10.113.113.20",
    "10.113.113.21",
    "10.113.113.24",
}

def getMikrotik(ip):
    api_username = 'kevins'
    api_password = 'kevins'
    api_port = 28728
    logging.info("Connecting to " + ip)
    user_data = []
    try:
        router = ros_api.Api(ip,user=api_username,password=api_password, port=api_port)
    except Exception as e:
        logging.info("User or password is wrong: "+str(ip))
        return -1
    try:
        r = router.talk('/ppp/active/print')
        for i in r:
            user_data.append({"ip_mikrotik":ip,"ip_onu":i["address"],"pppoe":i["name"],"mac":i["caller-id"].replace(":","-"),"vlan":"ANTENA"})
            
    except Exception as e:
        logging.error("Error when getting data: "+str(ip)+", "+str(e))
        return -1
    logging.info("Data from "+ip+" is ready, count: "+str(len(user_data)))
    return user_data

def insertMikrotik(data):
    dataQuery = ''
    for i in data:
        if "ip_onu" not in i:
            i["ip_onu"] = "duplicado"
        dataQuery = dataQuery + f"""('{i["ip_mikrotik"]}','{i['pppoe']}','{i['mac']}','{i['vlan']}','{i['ip_onu']}'),"""
    dataQuery = dataQuery[:-1]
    userQuery = "insert ignore into mikrotik (ip,mikrotik_pppoe,mac_mikrotik,vlan,onu_ip) values " + dataQuery +" ON DUPLICATE KEY UPDATE mac_mikrotik = VALUES(mac_mikrotik),vlan = VALUES(vlan),ip = VALUES(ip);"
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
        logging.error("Fallo en insertar en DB Local  {}".format(error))
        return 1


if __name__ == "__main__":
    user_data = []
    error = 0
    for ip in ip_list:
        response = getMikrotik(ip)
        if response == -1:
            logging.error("Error when getting data from "+ip)
            error = 1
        else:
            for i in response:
                user_data.append(i)
    if error:
        insertMikrotik(user_data)
        exit(1)
    else:
        exit(insertMikrotik(user_data))  

    