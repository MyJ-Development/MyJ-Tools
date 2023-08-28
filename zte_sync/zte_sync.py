import requests
import mysql.connector

class MySQL_LOCAL:
  def __init__(self):
    self.host = '10.19.11.2'
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
        print(str(cursor.rowcount)+" Cantidad de pppoe insertados correctamente en DB local: "+","+str(address))
        cursor.close()
        result = 1
    except mysql.connector.Error as error:
        print("Fallo en insertar en OLT DB Local INSERTOLTDATA  {}".format(error))
        return -1
    return 0

olt_list = [{"id":2,"name":"ZTE Quilicura"},
            {"id":3,"name":"ZTE Melipilla Culipran"},
            {"id":6,"name":"ZTE Quilicura 2"},
            {"id":7,"name":"ZTE Melipilla San pedro"},
            {"id":8,"name":"ZTE Melipilla Alcalde 2"},
            {"id":9,"name":"ZTE Maipu"},
            {"id":10,"name":"ZTE Quincanque Alto"},
            {"id":11,"name":"ZTE Los Guindos - Tantehue"},
            {"id":12,"name":"ZTE QUILICURA 3 - NEW ZTE"}]

def getZTE(olt_data):
    url = f"https://myjchile.smartolt.com/api/onu/get_onus_signals?olt_id={olt_data['id']}"
    payload = {}
    headers = {
    'X-Token': 'b4f4bcd529b24e46b302cf2d5a77ee7f'
    }
    data = []
    try:
        response = requests.request("GET", url, headers=headers, data = payload)
        response = response.json()
        for line in response["response"]:
            line['signal_1310'] = line['signal_1310'].replace(" dBm","")
            data.append({"mac_olt":line['sn'],"pon":line['port'],"slot":line['onu'],"rx":line['signal_1310']} )
        insertOltData(olt_data["name"],data)
    except Exception as e:
        print("Fallo en getZTE: "+str(e))
        return -1
    return len(data)
        

if __name__ == "__main__":
    error = 0
    counter = 0
    for olt in olt_list:
        response = getZTE(olt)
        counter = counter + response
        if response == -1:
            error = -1
    print("Cantidad de OLTs actualizadas: "+str(counter))
    exit(error)