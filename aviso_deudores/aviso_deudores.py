import time
from asterisk.ami import AMIClient, SimpleAction
import time
import logging
import mysql.connector
import re

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

class MySQL_LOCAL:
  def __init__(self):
    self.host = '10.19.11.2'
    self.user = 'myjdev'
    self.password = 'myjdev'
    self.database = 'olt_sync'


def makeCall(number_list):
    client = AMIClient(address='170.239.188.18', port=5038)
    client.login(username='admin', secret='nocmyj2023')

    for i, number in enumerate(number_list):
        while True:
            try:
                logging.info("calling: "+str(number))
                action = SimpleAction(
                    'Originate',
                    Channel=f'SIP/siptrunk1000/{number}',  # Número de teléfono al que quieres llamar
                    Context='aviso-cortepordeuda',
                    Exten='s',
                    Priority=1,
                    Callerid='999',
                    Timeout=30000,
                    Async=True,
                    Retry=0
                )
                future = client.send_action(action)
                remaining = len(number_list) - (i + 1)
                logging.info(f"Quedan {remaining} números por llamar.")
                time.sleep(15)
                break  # si no ocurre ninguna excepción, salimos del bucle while
            except Exception as e:
                logging.error("Error: "+str(e))
                time.sleep(10)
                client = AMIClient(address='170.239.188.18', port=5038)
                client.login(username='admin', secret='myjnet2022')


def getNumbers():
    userQuery = "SELECT contacto1,contacto2 FROM deudores WHERE intdate >= DATE_SUB(CURDATE(), INTERVAL 2 MONTH) AND intdate <= CURDATE() and duedebt>0;"
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
        logging.error("Fallo en obtener datos desde Local  {}".format(error))
        return -1
    return result

if __name__ == '__main__':
    numberList = getNumbers()
    patron = r"9\d{8}"
    contact_list = []
    for i in numberList:
        resultado = re.findall(patron, str(i))
        for contact in resultado:
            contact_list.append(contact)
    lista_sin_duplicados = list(set(contact_list))
    #lista_sin_duplicados = [number for number in set(contact_list) if number not in numeros_a_eliminar]
    logging.info("cantidad de numeros:"+str(len(lista_sin_duplicados)))
    #lista_sin_duplicados = ["990578558"]
    makeCall(lista_sin_duplicados)
    
