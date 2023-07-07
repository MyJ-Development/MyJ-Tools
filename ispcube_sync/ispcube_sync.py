import mysql.connector
import logging

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


class MySQL_ISPCUBE:
  def __init__(self):
    self.host = '170.239.188.10'
    self.user = 'myjdev'
    self.password = '2020myjdev'
    self.database = '105'

class MySQL_LOCAL:
  def __init__(self):
    self.host = '10.19.11.2'
    self.user = 'myjdev'
    self.password = 'myjdev'
    self.database = 'olt_sync'

def insertISPCUBE(data):
    dataQuery = ''
    for i in data:
        mac = "NOMAC"
        pppoe = "NOPPPOE"
        domicilio = "NODOMICILIO"
        if(i[3]):
            mac=i[3].replace(":","").replace(".","")
        if(i[4]):
            pppoe=i[4]
        if(i[2]):
            domicilio=i[2]
        dataQuery = dataQuery + "('"+str(i[1])+ "','" +str(pppoe)+ "','"+ str(i[0])+ "','" + str(mac) + "','"+str(domicilio)+"'),"
    dataQuery = dataQuery[:-1]
    userQuery = "insert ignore into mac_validation (nombre_cliente,pppoe,folio,mac_ispcube,domicilio) values " + dataQuery +";"
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
        logging.info(str(cursor.rowcount)+" Cantidad de clientes insertados correctamente en DB local: ")
        cursor.close()
    except mysql.connector.Error as error:
        logging.error("Fallo en insertar en DB Local  {}".format(error))
        return -1
    return 0

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
    response = insertISPCUBE(result)
    if response == 0:
        return(insertLogISPCUBE(result,"NOADDRESS"))
    else:
        return -1
    
def insertLogISPCUBE(data,address):
    dataQuery = ''
    for i in data:
        if(i[4]):
            pppoe=i[4]
        dataQuery = dataQuery + "('"+str(address)+ "','"+str(pppoe).lower()+ "'),"
    dataQuery = dataQuery[:-1]
    userQuery = "insert ignore into log (address,log_pppoe) values " + dataQuery +";"
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
        logging.info(str(cursor.rowcount)+" Cantidad de pppoe insertados correctamente en LOG DB local: ")
        cursor.close()
    except mysql.connector.Error as error:
        logging.error("Fallo en insertar en DB Local  {}".format(error))
        return -1
    return 0

def deleteISPCUBE():
    userQuery = "delete from mac_validation;"
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
        logging.info(str(cursor.rowcount)+" Cantidad de usuarios borrados correctamente en DB local: ")
        cursor.close()
    except mysql.connector.Error as error:
        logging.error("Fallo en borrar mac_validation en DB Local  {}".format(error))
        return -1
    return 0

if __name__ == '__main__':
    response = deleteISPCUBE()
    if response == 0:
        getISPCUBE()
    else:
        exit(1)