import mysql.connector
import datetime
from routeros_api import Api
import routeros_api
import json
from hurry.filesize import size, si
import re
import logging
from logging.config import dictConfig
import time
import threading
import sys
import telnetlib
import re
import multiprocessing

class MySQL_ISPCUBE:
  def __init__(self):
    self.host = '170.239.188.10'
    self.user = 'myjdev'
    self.password = '2020myjdev'
    self.database = '105'

class MySQL_LOCAL:
  def __init__(self):
    self.host = '10.19.11.7'
    self.user = 'radius'
    self.password = 'myjdev'
    self.database = 'radius'

class MySQL_GRAFANA:
  def __init__(self):
    self.host = '10.19.11.2'
    self.user = 'myjdev'
    self.password = 'myjdev'
    self.database = 'olt_sync'

def insertPPPoeEData(data):
    dataQuery = ''
    for i in data:
        rx = "null"
        tx = "null"
        dataQuery = dataQuery + "('"+str(i[0])+"','Cleartext-Password',':=','123456'),"
    dataQuery = dataQuery[:-1]
    userQuery = "insert into radcheck (username,attribute,op,value) values " + dataQuery +" ON DUPLICATE KEY UPDATE attribute = VALUES(attribute),op = VALUES(op),value = VALUES(value);"
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
        result = 1
    except mysql.connector.Error as error:
        print("Fallo en insertar en OLT DB Local INSERT PPPoE Data  {}".format(error))

    except Exception as error:
        print(error)
    return result




def insertPPPoeEPlan(data):
    dataQuery = ''
    for i in data:
        plan = str(i[1]) + "/" + str(i[2])
        dataQuery = dataQuery + "('"+str(i[0])+"','"+plan+"','8'),"
    dataQuery = dataQuery[:-1]
    userQuery = "insert into radusergroup (username,groupname,priority) values " + dataQuery +" ON DUPLICATE KEY UPDATE groupname = VALUES(groupname),priority = VALUES(priority);"
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
        print(str(cursor.rowcount)+" Cantidad de planes insertados correctamente : ")
        cursor.close()
        result = 1
    except mysql.connector.Error as error:
        print("Fallo en Planes  {}".format(error))

    except Exception as error:
        print(error)
    return result

def insertPPPoeEBandwith(data):
    dataQuery = ''
    for i in data:
        rx = "null"
        tx = "null"
        bandwith = i[1]+'/'+i[2]
        dataQuery = dataQuery + "('"+str(i[0])+"','Mikrotik-Rate-Limit','=','"+bandwith+"'),"
    dataQuery = dataQuery[:-1]
    userQuery = "insert into radreply (username,attribute,op,value) values " + dataQuery + " ON DUPLICATE KEY UPDATE value = VALUES(value);"
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
        print(str(cursor.rowcount)+" Cantidad de Bandwith insertados correctamente : ")
        cursor.close()
        result = 1
    except mysql.connector.Error as error:
        print("Fallo en Bandwith  {}".format(error))

    except Exception as error:
        print(error)
    return result

def insertPPPoeEIP(data):
    dataQuery = ''

    for i in data:
        dataQuery = dataQuery + "('"+str(i[0])+"','Framed-IP-Address',':=','"+str(i[3])+"'),"
    dataQuery = dataQuery[:-1]
    userQuery = "insert into radreply(username,attribute,op,value) values " + dataQuery +" ON DUPLICATE KEY UPDATE attribute = VALUES(attribute),value = VALUES(value);"
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
        print(str(cursor.rowcount)+" Cantidad de PPPoE IP insertados correctamente ")
        cursor.close()
        result = 1
    except mysql.connector.Error as error:
        print("Fallo en PPPoE IP  {}".format(error))

    except Exception as error:
        print(error)
    return result

def deleteNoPPPoeEIP(data):
    dataQuery = '('
    for i in data:
        dataQuery = dataQuery + "'" + str(i[0]) + "',"
    dataQuery = dataQuery[:-1]
    dataQuery = dataQuery + ");"
    userQuery = "delete from radreply where attribute = 'Framed-IP-Address' and username not in " + dataQuery
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
        print(str(cursor.rowcount)+" Cantidad de PPPoE IP Borrados correctamente ")
        cursor.close()
        result = 1
    except mysql.connector.Error as error:
        print("Fallo en PPPoE IP  {}".format(error))

    except Exception as error:
        print(error)
    return result

def deleteRadReply():
    userQuery = "delete from radreply where attribute = 'Mikrotik-Rate-Limit';"
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
        print(str(cursor.rowcount)+" Cantidad de RadReply Borrados correctamente ")
        cursor.close()
        result = 1
    except mysql.connector.Error as error:
        print("Fallo en RadReply  {}".format(error))

    except Exception as error:
        print(error)
    return result

def insertPPPoeEDeudor(data):
    dataQuery = ''
    for i in data:
        dataQuery = dataQuery + "('"+str(i[0])+"','Mikrotik-Address-List',':=','Deudores'),"
    dataQuery = dataQuery[:-1]
    userQuery = "insert into radreply(username,attribute,op,value) values " + dataQuery +" ON DUPLICATE KEY UPDATE attribute = VALUES(attribute),value = VALUES(value);"
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
        print(str(cursor.rowcount)+" Cantidad de Deudores insertados correctamente: ")
        cursor.close()
        result = 1
    except mysql.connector.Error as error:
        print("Fallo en Deudores  {}".format(error))

    except Exception as error:
        print(error)
    return result

def insertCatvDeudor(data):
    dataQuery = ''
    for i in data:
        dataQuery = dataQuery + "('"+str(i[0])+"','PorDesactivar'),"
    dataQuery = dataQuery[:-1]
    userQuery = "insert into catvAdmin(pppoe,status) values " + dataQuery +" ON DUPLICATE KEY UPDATE status = 'PorDesactivar',try_counter = '0';"
    result = 0
    MySQLInfo = MySQL_GRAFANA()
    try:
        connection = mysql.connector.connect(host=MySQLInfo.host,
                                         database=MySQLInfo.database,
                                         user=MySQLInfo.user,
                                         password=MySQLInfo.password)
        cursor = connection.cursor()
        cursor.execute(userQuery)
        connection.commit()
        print(str(cursor.rowcount)+" Cantidad de Deudores CATV insertados correctamente: ")
        cursor.close()
        result = 1
    except mysql.connector.Error as error:
        print("Fallo en Deudores  {}".format(error))

    except Exception as error:
        print(error)
    return result

def insertCatvNoDeudor(data):
    dataQuery = ''
    for i in data:
        dataQuery = dataQuery + "('"+str(i[0])+"','PorActivar'),"
    dataQuery = dataQuery[:-1]
    userQuery = "insert into catvAdmin(pppoe,status) values " + dataQuery +" ON DUPLICATE KEY UPDATE status = 'PorActivar',try_counter = '0';"
    result = 0
    MySQLInfo = MySQL_GRAFANA()
    try:
        connection = mysql.connector.connect(host=MySQLInfo.host,
                                         database=MySQLInfo.database,
                                         user=MySQLInfo.user,
                                         password=MySQLInfo.password)
        cursor = connection.cursor()
        cursor.execute(userQuery)
        connection.commit()
        print(str(cursor.rowcount)+" Cantidad de NoDeudores CATV insertados correctamente: ")
        cursor.close()
        result = 1
    except mysql.connector.Error as error:
        print("Fallo en Deudores  {}".format(error))

    except Exception as error:
        print(error)
    return result

def insertPPPoeENoDeudor(data):
    dataQuery = '('
    for i in data:
        dataQuery = dataQuery + "'"+str(i[0])+"',"
    dataQuery = dataQuery[:-1]
    dataQuery = dataQuery + ');'
    userQuery = 'delete from radreply where attribute = "Mikrotik-Address-List" and username in ' + dataQuery
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
        print(str(cursor.rowcount)+" Cantidad de PPPoE NoDeudores eliminados correctamente")
        cursor.close()
        result = 1
    except mysql.connector.Error as error:
        print("Fallo en NoDeudores  {}".format(error))

    except Exception as error:
        print(error)
    return result

def getISPCUBE(pppoe):
    if(pppoe):
        userQuery = "select radiususer from customer join connections on customer.idcustomer=connections.idcustomer join plans on connections.idplan=plans.idplan where radiususer is not null;"
    else:
        userQuery = "select radiususer,speedup,speeddown,ip,status from customer join connections on customer.idcustomer=connections.idcustomer join plans on connections.idplan=plans.idplan where radiususer is not null;"
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
        print("Fallo en obtener datos desde ISPCube  {}".format(error))
    return result

def getCurrentDebts():
    userQuery = 'select username from radreply where value = "Deudores";'
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
        print("Fallo en obtener datos desde Radius  {}".format(error))
    return result

def getPPPoEIP(pppoe):
    userQuery = 'select ip from mikrotik where mikrotik_pppoe = "'+pppoe+'";'
    result = 0
    MySQLInfo = MySQL_GRAFANA()
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
        print("Fallo en obtener datos desde Radius  {}".format(error))
    return result

def deleteDB(table):
    userQuery = "delete from "+str(table)+";"
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
        logging.error("Fallo en borrar mac_validation en DB Local  {}".format(error))
    
    return result

def sendDeAuth(address,pppoeList):
    try:
        try:
            router = Api(address, user='kevins', password='kevins', port=28728)
            #r = router.talk('/ppp/active/print')
            r = router.talk('/interface/pppoe-server/print')
        except Exception as error:
            print("Error en MK: "+str(address)+ " : "+ str(error))
        counter = 0
        for line in r:
            line=json.dumps(line,indent=4)
            data=json.loads(line)
            for aux in pppoeList:
                if(data['user'] in aux):
                    #print("aca: "+str(data['user']+" : "+aux))
                    found = data
                else:
                    pass
                    #print("no encontrado: "+str(data['user']+" : "+aux))
                    found = ""
            #found = [x for x in pppoeList if str(x[0]) == data["user"]]
            if(found):
                try: 
                    print(router.talk('/interface/pppoe-server/remove\n=.id='+data[".id"]))
                    counter = counter + 1
                    #print("Desauntenticado correctamente: "+str(found))
                except Exception as e:
                    print("Error!: "+str(e))

        print(str(counter)+" Cantidad de Usuarios Desauntenticados "+" IP: "+address)
    except Exception as error:
        print("IP: "+address+" Excepcion: "+str(error))
    
def readIP():
    ips = []
    ipList = open("ipList.txt","r")
    response = []
    for ip in ipList:
        ips.append(ip.replace("\n",""))
    ipList.close
    ipList = open("ipListWireless.txt","r")
    response = []
    for ip in ipList:
        ips.append(ip.replace("\n",""))
    ipList.close
    return ips

def getAllPPP():
    userQuery = 'select * from radcheck;'
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
        print("Fallo en obtener datos desde Radius  {}".format(error))
    return result

def deletePPPTable(pppoe_list,tablename):
    dataQuery = '('
    for i in pppoe_list:
        dataQuery = dataQuery + "'" + str(i) + "',"
    dataQuery = dataQuery[:-1]
    dataQuery = dataQuery + ");"
    userQuery = "delete from "+str(tablename)+" where username in " + dataQuery
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
        print(str(cursor.rowcount)+" Cantidad de PPPoE IP Borrados correctamente ")
        cursor.close()
        result = 1
    except mysql.connector.Error as error:
        print("Fallo en PPPoE IP  {}".format(error))

    except Exception as error:
        print(error)
    return result

def syncDeletePPP(pppoe_list):
    deletePPPTable(pppoe_list,"radreply")
    deletePPPTable(pppoe_list,"radcheck")
    deletePPPTable(pppoe_list,"radusergroup")
    


if __name__ == "__main__":
    print("Solicitando datos ISPCUBE")
    data = getISPCUBE(False)
    deleteRadReply()
    #radreply,radcheck,radusergroup
    current_ppp = getAllPPP()
    syncPPPoE = getISPCUBE(True)
    syncList = []
    print("Datos ISPCUBE obtenidos")
    for line in (syncPPPoE):
        syncList.append(str(line[0]))
    syncDelete = []
    #print(syncPPPoE)
    for line in current_ppp:
        #print(line[1])
        if(str(line[1]) in syncList):
            pass
        else:
            syncDelete.append(str(line[1]))

    if(syncDelete):
        syncDeletePPP(syncDelete)
    ip_clients = []
    deudores_clients = []
    no_deudores_clients = []
    deudores_actuales = getCurrentDebts()


    for line in data:
        if(line[3]!='' and line[3]!=None):
            ip_clients.append(line)
    
    for line in data:
        if(line[4] == 1):
            deudores_clients.append(line)
        else:
            no_deudores_clients.append(line)
    response = 0
    while(response == 0):
        response = insertPPPoeEData(data)
        if (response):
            print("PPPoE Data Correcto")
        else:
            time.sleep(1)
            print("PPPoE Data Incorrecto")
    response = 0
    while(response == 0):
        response = insertPPPoeEPlan(data)  
        if (response):
            print("PPPoE Plan Correcto")
        else:
            time.sleep(1)
            print("PPPoE Plan Incorrecto")
    response = 0
    while(response == 0):
        response = insertPPPoeEBandwith(data)  
        if (response):
            print("PPPoE Bandwith Correcto")
        else:
            time.sleep(1)
            print("PPPoE Bandwith Incorrecto")
    response = 0
    while(response == 0):
        response = deleteNoPPPoeEIP(ip_clients)  
        if (response):
            print("Borrado PPPoE IP Correcto")
        else:
            time.sleep(1)
            print("Borrado PPPoE IP Incorrecto")
    response = 0
    while(response == 0):
        response = insertPPPoeEIP(ip_clients)  
        if (response):
            print("PPPoE IP Correcto")
        else:
            time.sleep(1)
            print("PPPoE IP Incorrecto") 
    response = 0
    while(response == 0):
        response = insertPPPoeEDeudor(deudores_clients)  
        if (response):
            print("PPPoE Deudor Correcto")
        else:
            time.sleep(1)
            print("PPPoE Deudor Incorrecto")
    response = 0
    while(response == 0):
        response = insertPPPoeENoDeudor(no_deudores_clients)
        if (response):
            print("PPPoE NoDeudor Correcto")
        else:
            time.sleep(1)
            print("PPPoE NoDeudor Incorrecto")

    reboot_clients = []
    for client in deudores_actuales:
        find = [x for x in no_deudores_clients if x[0] == client[0]]
        if(find):
            reboot_clients.append(client[0])
    
    ip_list = []
    for client in reboot_clients:
        ip = getPPPoEIP(client)
        try:
            ip = ip[0][0]
        except Exception as error:
            print("Error!: "+str(error))
        ip_list.append({"IP":ip,"pppoe":str(client)})

    ips = readIP()

    for ip in ips:
        deauth_clients = []
        for client in ip_list:
            if(client['IP'] == ip):
                to_add = client['pppoe']
                ''.join(e for e in to_add if e.isalnum())
                deauth_clients.append(to_add)
        if(deauth_clients):
            print("IP: "+ip+" Deautenticando: "+str(deauth_clients))
            sendDeAuth(ip,deauth_clients)
