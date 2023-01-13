import requests
import json
import mysql.connector
import time

class MySQL_LOCAL:
  def __init__(self):
    self.host = '170.239.188.2'
    self.user = 'myjdev'
    self.password = 'myjdev'
    self.database = 'olt_sync'

def getMAC():
    userQuery = "select mac_olt from olt where ip_olt='172.16.50.135'"
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
        print("Fallo en obtener datos desde SQL  {}".format(error))
    return result

def getZTE(mac):
    url = "https://myjchile.smartolt.com/api/onu/reboot/"
    payload = {}
    headers = {
    'X-Token': 'b4f4bcd529b24e46b302cf2d5a77ee7f'
    }
    url = url + mac
    response = requests.request("POST", url, headers=headers, data = payload)
    response = response.json()
    print(response)
    data = []

def main():
    mac_list = getMAC()
    for mac in mac_list:
        print(mac[0])
        getZTE(mac[0])
        time.sleep(1)

main()