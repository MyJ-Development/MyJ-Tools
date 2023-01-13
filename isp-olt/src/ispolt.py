import mysql.connector
import json
import re

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

def insertOltData(address,data):
    dataQuery = ''
    for i in data:
        rx = "null"
        tx = "null"
        dataQuery = dataQuery + "('"+str(address)+"','" +"null"+ "','" +str(i['mac_olt'])+ "','"+ str(i['pon'])+ "','" + i['slot'] + "','"+ str(rx) +"','"+str(tx)+"','"+i['status']+"'),"
    dataQuery = dataQuery[:-1]
    userQuery = "insert into olt (ip_olt,olt_mac_mikrotik,mac_olt,pon,slot,rx,tx,status) values " + dataQuery +" ON DUPLICATE KEY UPDATE ip_olt = VALUES(ip_olt), mac_olt = VALUES(mac_olt),pon = VALUES(pon),slot = VALUES(slot),rx=VALUES(rx),tx=VALUES(tx);"
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
        print("IP: "+address+" Fallo en insertar en OLT DB Local INSERTOLTDATA  {}".format(error))
        print("Query: ")
        print(userQuery)

    finally:
            return result

def getISPCUBE():
    userQuery = "select * from olt_active where idnode is not null;"
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

def main():
    data = getISPCUBE()
    find_mac = re.compile(r'([0-9a-zA-Z]{2}[:]){5}[0-9a-zA-Z]{2}')
    olt_data = []
    for line in data:
        mac = re.findall(find_mac,line[1])
        
        if(mac):
            address= str(re.findall('\d+', line[0]))
            address=address.replace("[","").replace("]","").replace("'","")
            mac = str(line[1])
            mac = mac.replace(":","")
            olt_data.append({"address":"172.16.50."+address, "mac_olt":mac,"pon":line[2],"slot":line[3],"status":line[4]})

    #insertOltData("172.16.50.100",[x for x in olt_data if x['address'] == '172.16.50.100'])
    insertOltData("172.16.50.101",[x for x in olt_data if x['address'] == '172.16.50.101'])
    insertOltData("172.16.50.103",[x for x in olt_data if x['address'] == '172.16.50.103'])
    insertOltData("172.16.50.104",[x for x in olt_data if x['address'] == '172.16.50.104'])
    insertOltData("172.16.50.105",[x for x in olt_data if x['address'] == '172.16.50.105'])
    insertOltData("172.16.50.106",[x for x in olt_data if x['address'] == '172.16.50.106'])
    insertOltData("172.16.50.107",[x for x in olt_data if x['address'] == '172.16.50.107'])
    insertOltData("172.16.50.109",[x for x in olt_data if x['address'] == '172.16.50.109'])
    #insertOltData("172.16.50.110",[x for x in olt_data if x['address'] == '172.16.50.110'])
    #insertOltData("172.16.50.111",[x for x in olt_data if x['address'] == '172.16.50.111'])
    #insertOltData("172.16.50.112",[x for x in olt_data if x['address'] == '172.16.50.112'])
    #insertOltData("172.16.50.113",[x for x in olt_data if x['address'] == '172.16.50.113'])
    #insertOltData("172.16.50.114",[x for x in olt_data if x['address'] == '172.16.50.114'])
    #insertOltData("172.16.50.115",[x for x in olt_data if x['address'] == '172.16.50.115'])
    #insertOltData("172.16.50.116",[x for x in olt_data if x['address'] == '172.16.50.116'])
    #insertOltData("172.16.50.117",[x for x in olt_data if x['address'] == '172.16.50.117'])
    #insertOltData("172.16.50.118",[x for x in olt_data if x['address'] == '172.16.50.118'])
    #insertOltData("172.16.50.119",[x for x in olt_data if x['address'] == '172.16.50.119'])
    #insertOltData("172.16.50.120",[x for x in olt_data if x['address'] == '172.16.50.120'])
    insertOltData("172.16.50.121",[x for x in olt_data if x['address'] == '172.16.50.121'])
    insertOltData("172.16.50.122",[x for x in olt_data if x['address'] == '172.16.50.122'])
    insertOltData("172.16.50.123",[x for x in olt_data if x['address'] == '172.16.50.123'])
    insertOltData("172.16.50.124",[x for x in olt_data if x['address'] == '172.16.50.124'])
    insertOltData("172.16.50.125",[x for x in olt_data if x['address'] == '172.16.50.125'])
    #insertOltData("172.16.50.126",[x for x in olt_data if x['address'] == '172.16.50.126'])
    insertOltData("172.16.50.127",[x for x in olt_data if x['address'] == '172.16.50.127'])
    insertOltData("172.16.50.128",[x for x in olt_data if x['address'] == '172.16.50.128'])
    insertOltData("172.16.50.129",[x for x in olt_data if x['address'] == '172.16.50.129'])
    insertOltData("172.16.50.130",[x for x in olt_data if x['address'] == '172.16.50.130'])
    insertOltData("172.16.50.131",[x for x in olt_data if x['address'] == '172.16.50.131'])
    insertOltData("172.16.50.132",[x for x in olt_data if x['address'] == '172.16.50.132'])
    insertOltData("172.16.50.141",[x for x in olt_data if x['address'] == '172.16.50.141'])

main()
