import mysql.connector
import datetime
import logging

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

def getISPCUBE():
    userQuery = "select connections.idcustomer,name,connections.address,radiususer,duedebt,intdate,mac,customer.lat,customer.lng,connections.lat,connections.lng,contact,phone from customer join connections on connections.idcustomer=customer.idcustomer where status=1 and radiususer is not null"
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
        logging.error("Fallo en obtener datos desde ISPCube  {}".format(error))
        return -1
    return result

def getISPCUBEAntiguos():
    userQuery = "select connections.idcustomer,name,connections.address,radiususer,duedebt,intdate,mac,customer.lat,customer.lng,connections.lat,connections.lng,contact,phone from customer join connections on connections.idcustomer=customer.idcustomer where status=1 and radiususer is not null and intdate < DATE_SUB(now(), INTERVAL 3 month);"
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
        logging.error("Fallo en obtener datos desde ISPCube  {}".format(error))
        return -1
    return result

def getISPCUBENuevos():
    userQuery = "select connections.idcustomer,name,connections.address,radiususer,duedebt,intdate,mac,customer.lat,customer.lng,connections.lat,connections.lng,contact,phone from customer join connections on connections.idcustomer=customer.idcustomer where status=1 and radiususer is not null and intdate > DATE_SUB(now(), INTERVAL 3 month);"
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
        logging.error("Fallo en obtener datos desde ISPCube  {}".format(error))
        return -1
    return result

def insertDeudores(data):
    dataQuery = ''
    for i in data:
        #print(str(i[2]))
        deuda = str(int(i[4]))
        dataQuery = dataQuery + "('"+i[0]+ "','"+str(i[1]).lower()+"','"+ str(i[2])+"','"+str(i[3])+"',"+deuda+",'"+str(i[5])+"','"+str(i[6])+"','"+str(i[7])+"','"+str(i[8])+"','"+str(i[9])+"','"+str(i[10])+"','"+str(i[11])+"','"+str(i[12])+"'),"

    dataQuery = dataQuery[:-1]
    userQuery = "insert into deudores values " + dataQuery + ";"
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
    except mysql.connector.Error as error:
        logging.error("Fallo en insertar en DB Local  {}".format(error))
        return -1
    return 0

def insertLogDeudoresAntiguos(amount):
    dataQuery = ''
    logDate = datetime.datetime.today()
    logDate = datetime.datetime(logDate.year, logDate.month, logDate.day,logDate.hour,logDate.minute)
    userQuery = "insert into log_deudores(log_date,cantidad_antiguos) values ('" + str(logDate)+"',"+str(amount)+ ");"
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
        logging.info(str(cursor.rowcount)+" Log insertado correctamente en DB local: ")
        cursor.close()
    except mysql.connector.Error as error:
        logging.error("Fallo en insertar en DB Local  {}".format(error))
        return -1
    return 0

def insertLogDeudoresNuevos(amount):
    dataQuery = ''
    logDate = datetime.datetime.today()
    logDate = datetime.datetime(logDate.year, logDate.month, logDate.day,logDate.hour,logDate.minute)
    userQuery = "insert into log_deudores(log_date,cantidad_nuevos) values ('" + str(logDate)+"',"+str(amount)+ ");"
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
        logging.info(str(cursor.rowcount)+" Log insertado correctamente en DB local: ")
        cursor.close()
    except mysql.connector.Error as error:
        logging.error("Fallo en insertar en DB Local  {}".format(error))
        return -1
    return 0

def deleteISPCUBE():
    userQuery = "delete from deudores;"
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

if __name__ == "__main__":
    deleteISPCUBE()
    deudores=getISPCUBE()
    if deudores == -1:
        logging.error("No se pudo obtener datos desde ISPCube")
        exit(1)
    log_deudoresAntiguos = getISPCUBEAntiguos()
    if log_deudoresAntiguos == -1:
        logging.error("No se pudo obtener datos desde ISPCube Antiguos ")
        exit(1)
    log_deudoresNuevos = getISPCUBENuevos()
    if log_deudoresNuevos == -1:
        logging.error("No se pudo obtener datos desde ISPCube Nuevos ")
        exit(1)
    response = insertDeudores(deudores)
    if response == -1:
        logging.error("No se pudo insertar en DB Local")
        exit(1)
    response = insertLogDeudoresAntiguos(len(log_deudoresAntiguos))
    if response == -1:
        logging.error("No se pudo insertar en DB Local Antiguos ")
        exit(1)
    response = insertLogDeudoresNuevos(len(log_deudoresNuevos))
    if response == -1:
        logging.error("No se pudo insertar en DB Local Nuevos ")
        exit(1)
    exit(0)

