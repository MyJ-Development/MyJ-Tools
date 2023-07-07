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


class MySQL_LOCAL:
  def __init__(self):
    self.host = '10.19.11.2'
    self.user = 'myjdev'
    self.password = 'myjdev'
    self.database = 'olt_sync'



def insertGrafana():
    userQuery = """INSERT INTO grafana_log(folio, pppoe, domicilio, mac_ispcube, mac_olt, mac_mikrotik, ip, vlan, onu_ip, ip_olt, pon, slot, rx, tx)
    SELECT DISTINCT folio, pppoe, domicilio, mac_ispcube, mac_olt, mac_mikrotik, ip, vlan, onu_ip, ip_olt, pon, slot, rx, tx
    FROM mac_validation
    JOIN olt ON mac_ispcube = mac_olt
    JOIN mikrotik ON pppoe = mikrotik_pppoe
    ON DUPLICATE KEY UPDATE
    domicilio = VALUES(domicilio),
    mac_ispcube = VALUES(mac_ispcube),
    mac_olt = VALUES(mac_olt),
    mac_mikrotik = VALUES(mac_mikrotik),
    ip = VALUES(ip),
    vlan = VALUES(vlan),
    onu_ip = VALUES(onu_ip),
    ip_olt = VALUES(ip_olt),
    pon = VALUES(pon),
    slot = VALUES(slot),
    rx = VALUES(rx),
    tx = VALUES(tx);"""
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
        updated_records = cursor.fetchall()
        print("Updated records ", updated_records)
        cursor.close()
    except mysql.connector.Error as error:
        print("Fallo en insertar {}".format(error))
        return -1
    return 0

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
    except mysql.connector.Error as error:
        print("Fallo en Borrar  {}".format(error))
        return -1
    return 0

if __name__ == "__main__":
    #response = deleteGrafana()
    response = 0
    if response == 0:
        logging.info("Borrado de datos de grafana exitoso")
        exit(insertGrafana())
    else:
        exit(1)