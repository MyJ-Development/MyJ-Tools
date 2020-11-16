import mysql.connector
import datetime

class MySQL_LOCAL:
  def __init__(self):
    self.host = '10.19.11.9'
    self.user = 'myjdev'
    self.password = 'myjdev'
    self.database = 'olt_sync'

class MySQL_ISPCUBE:
  def __init__(self):
    self.host = '170.239.188.10'
    self.user = 'myjdev'
    self.password = '2020myjdev'
    self.database = '105'

def getISPCUBE():
    userQuery = "select connections.idcustomer,name,connections.address,radiususer,duedebt,intdate,mac from customer join connections on connections.idcustomer=customer.idcustomer where status=1 and radiususer is not null"
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
        print("Fallo en obtener datos desde ISPCube  {}".format(error))
    
    return result

def getISPCUBEAntiguos():
    userQuery = "select connections.idcustomer,name,connections.address,radiususer,duedebt,intdate,mac from customer join connections on connections.idcustomer=customer.idcustomer where status=1 and radiususer is not null and intdate < DATE_SUB(now(), INTERVAL 3 month);"
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
        print("Fallo en obtener datos desde ISPCube  {}".format(error))
    
    return result

def getISPCUBENuevos():
    userQuery = "select connections.idcustomer,name,connections.address,radiususer,duedebt,intdate,mac from customer join connections on connections.idcustomer=customer.idcustomer where status=1 and radiususer is not null and intdate > DATE_SUB(now(), INTERVAL 3 month);"
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
        print("Fallo en obtener datos desde ISPCube  {}".format(error))
    
    return result

def insertDeudores(data):
    dataQuery = ''
    for i in data:
        deuda = str(int(i[4]))
        dataQuery = dataQuery + "('"+i[0]+ "','"+str(i[1]).lower()+"','"+ str(i[2])+"','"+str(i[3])+"',"+deuda+",'"+str(i[5])+"','"+str(i[6])+"'),"

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
        print(str(cursor.rowcount)+" Cantidad de pppoe insertados correctamente en DB local: ")
        cursor.close()
    except mysql.connector.Error as error:
        print("Fallo en insertar en DB Local  {}".format(error))

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
        print(str(cursor.rowcount)+" Log insertado correctamente en DB local: ")
        cursor.close()
    except mysql.connector.Error as error:
        print("Fallo en insertar en DB Local  {}".format(error))

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
        print(str(cursor.rowcount)+" Log insertado correctamente en DB local: ")
        cursor.close()
    except mysql.connector.Error as error:
        print("Fallo en insertar en DB Local  {}".format(error))

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
        print(str(cursor.rowcount)+" Cantidad de usuarios borrados correctamente en DB local: ")
        cursor.close()
    except mysql.connector.Error as error:
        print("Fallo en borrar mac_validation en DB Local  {}".format(error))

def main():
    deleteISPCUBE()
    deudores=getISPCUBE()
    log_deudoresAntiguos=getISPCUBEAntiguos()
    log_deudoresNuevos=getISPCUBENuevos()
    insertDeudores(deudores)
    insertLogDeudoresAntiguos(len(log_deudoresAntiguos))
    insertLogDeudoresNuevos(len(log_deudoresNuevos))
main()