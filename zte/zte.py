import requests
import json
import mysql.connector


class MySQL_LOCAL:
  def __init__(self):
    self.host = '10.19.11.9'
    self.user = 'myjdev'
    self.password = 'myjdev'
    self.database = 'olt_sync'

def insertOltData(address,data):
    dataQuery = ''
    for i in data:
        rx = ""
        tx = ""
        dataQuery = dataQuery + "('"+str(address)+"','" +"null"+ "','" +str(i['mac_olt'])+ "','"+ str(i['pon'])+ "','" + i['slot'] + "','"+ str(i['rx']) +"','"+str(tx)+ "'),"
    dataQuery = dataQuery[:-1]
    userQuery = "insert into olt (ip_olt,olt_mac_mikrotik,mac_olt,pon,slot,rx,tx) values " + dataQuery +" ON DUPLICATE KEY UPDATE ip_olt = VALUES(ip_olt), mac_olt = VALUES(mac_olt),pon = VALUES(pon),slot = VALUES(slot),rx=VALUES(rx),tx=VALUES(tx);"
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
        if (connection.is_connected()):
            connection.close()
    except mysql.connector.Error as error:
        print("Fallo en insertar en OLT DB Local INSERTOLTDATA  {}".format(error))

    finally:
            return result

url = "https://myjchile.smartolt.com/api/onu/get_onus_signals?olt_id=2"

payload = {}
headers = {
  'X-Token': '21a18ba0e9844b7e8000c10f42d159b2'
}

response = requests.request("GET", url, headers=headers, data = payload)
response = response.json()

data = []
for line in response['response']:
    #print(line['sn']+" "+line['port']+" "+line['onu']+" "+line['signal_1310'])
    data.append({"mac_olt":line['sn'],"pon":line['port'],"slot":line['onu'],"rx":line['signal_1310']} )

insertOltData("172.16.50.135",data)

#print(len(response['onus']))