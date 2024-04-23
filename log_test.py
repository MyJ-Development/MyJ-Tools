import json
import ros_api 
import re
import logging
import mysql.connector

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

ip_list = {
    "10.113.113.11",
    "10.113.113.12",
    "10.113.113.15",
    "10.113.113.16",
    "10.113.113.17",
    "10.113.113.19",
    "10.113.113.24",
    "10.113.113.28",
    "10.113.113.31",
    "10.113.113.8",
    "10.119.119.18",
    "10.119.119.25",
    "10.119.119.32",
    "10.119.119.35",
    "10.121.121.10",
    "10.121.121.3",
    "10.121.121.4",
    "10.121.121.6",
    "10.121.121.7",
    "10.121.121.8"
}

def insertLog(data):
    dataQuery = ''
    for i in data:
        dataQuery = dataQuery + "('"+str(i["address"])+ "','"+i["pppoe"]+ "','0'),"
    dataQuery = dataQuery[:-1]
    userQuery = "insert into log (address,log_pppoe,online) values " + dataQuery +" ON DUPLICATE KEY UPDATE address = VALUES(address),log_pppoe = VALUES(log_pppoe), online = VALUES(online);"
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

def getMikrotik(ip):
    api_username = 'kevins'
    api_password = 'kevins'
    api_port = 28728
    logging.info("Connecting to " + ip)
    try:
        router = ros_api.Api(ip,user=api_username,password=api_password, port=api_port)
    except Exception as e:
        logging.info("User or password is wrong: "+str(ip))
        return -1
    try:
        vlan_data = []
        r = router.talk('/interface/vlan/print')
        for i in r:
            i = json.dumps(i)
            i = json.loads(i)
            vlan_data.append(i)

        ethernet_data = []
        r = router.talk('/interface/ethernet/print')
        for i in r:
            i = json.dumps(i)
            i = json.loads(i)
            ethernet_data.append(i)

        ppppoe_server_data = []
        r = router.talk('/interface/pppoe-server/print')
        for i in r:
            i = json.dumps(i)
            i = json.loads(i)
            ppppoe_server_data.append(i)

        user_data = []
        for i in ppppoe_server_data:
            pppoe_vlan = i['service'].replace('vlan','').replace("VLAN","").replace("PPPoE","").replace("pppoe","").replace("PPPOE","").replace(" ","")
            for j in vlan_data:
                if j['vlan-id'] == pppoe_vlan:
                    for k in ethernet_data:
                        if "comment" in k:

                            if k["name"] == j["interface"] or k["comment"] == j["interface"]:
                                user_data.append({"vlan": j["name"],"olt":k["comment"][-3:],"pppoe":i["user"],"ip_mikrotik":ip,"mac":i["remote-address"].replace(":","")})

        #remove duplicated
        user_data = [i for n, i in enumerate(user_data) if i not in user_data[n + 1:]]
        
        r = router.talk('/ppp/active/print')
        for i in r:
            for j in user_data:
                if i["name"] == j["pppoe"]:
                    j["ip_onu"] = i["address"]
                    break
        
    except Exception as e:
        logging.error("Error when getting data: "+str(ip)+", "+str(e))
        return -1
    logging.info("Data from "+ip+" is ready, count: "+str(len(user_data)))
    patron = r'^\d{3}$'
    error = 0
    for i in user_data:
        coincidencia = re.match(patron, i["olt"])
        if(not coincidencia):
            logging.error("Comentario erroneo en: "+str(ip)+", "+i["olt"])
            error = 1
            
    if(error):
        return -1
    else:
        return user_data

def getISPCUBE():
    userQuery = "select connections.idcustomer,name,connections.address,mac,radiususer from customer join connections on connections.idcustomer=customer.idcustomer where status=0 and radiususer is not null;"
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
    except mysql.connector.Error as error:
        logging.error("Fallo en obtener datos desde ISPCube  {}".format(error))
        return -1
    return result

if __name__ == "__main__":
    user_data = []
    error = 0
    response = getISPCUBE()
    for i in response:
    	print(i[4])
    exit(0)
    for ip in ip_list:
        response = getMikrotik(ip)
        if response == -1:
            logging.error("Error when getting data from "+ip)
            error = 1
        else:
            for i in response:
                user_data.append(i)
    if error:
        insertLog(user_data)
        exit(1)
    else:
        exit(insertLog(user_data))  

    
