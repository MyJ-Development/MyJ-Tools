import requests
import json
import mysql.connector

class MySQL_LOCAL:
  def __init__(self):
    self.host = '10.19.11.2'
    self.user = 'myjdev'
    self.password = 'myjdev'
    self.database = 'olt_sync'

def insertGrafana():
    userQuery = "insert into grafana_log(folio,pppoe,domicilio,mac_ispcube,mac_olt,mac_mikrotik,ip,vlan,onu_ip,ip_olt,pon,slot,rx,tx) select distinct folio,pppoe,domicilio,mac_ispcube,mac_olt,mac_mikrotik,ip,vlan,onu_ip,ip_olt,pon,slot,rx,tx  from mac_validation join olt on mac_ispcube=mac_olt join mikrotik on pppoe=mikrotik_pppoe;"
    MySQLInfo = MySQL_LOCAL()
    try:
        connection = mysql.connector.connect(host=MySQLInfo.host,
                                         database=MySQLInfo.database,
                                         user=MySQLInfo.user,
                                         password=MySQLInfo.password)
        cursor = connection.cursor()
        cursor.execute(userQuery)
        print(str(cursor.rowcount)+" Cantidad de pppoe insertados correctamente en DB local: ")
        print("Insertado")
        connection.commit()
        cursor.close()
        
    except mysql.connector.Error as error:
        print("Fallo en insertar {}".format(error))

def deleteGrafana():
    userQuery = "delete from grafana_log;"
    MySQLInfo = MySQL_LOCAL()
    try:
        connection = mysql.connector.connect(host=MySQLInfo.host,
                                         database=MySQLInfo.database,
                                         user=MySQLInfo.user,
                                         password=MySQLInfo.password)
        cursor = connection.cursor()
        cursor.execute(userQuery)
        connection.commit()
        cursor.close()
        print("Borrado")
    except mysql.connector.Error as error:
        print("Fallo en Borrar  {}".format(error))

if __name__ == "__main__":
    deleteGrafana()
    insertGrafana()
