import mysql.connector
import logging
import telegram
import asyncio
import time

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

def getUsers():
    userQuery = "select ip,count(*) from log join mac_validation on pppoe=log_pppoe join mikrotik on pppoe=mikrotik_pppoe where online=0 group by ip;"
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
        logging.error("Fallo en obtener datos desde LOCAL  {}".format(error))
        return -1
    return result

async def sendAlert(ip, offline_users):
    bot = telegram.Bot("5753479653:AAFpNG9ip59sgl2UVDPxDRzmNaL9DJTmO_A")
    logging.info(f"Enviando alerta de {ip} con {offline_users} caidos")
    await bot.send_message(text=f"Mikrotik {ip} tiene {offline_users} caidos", chat_id=5635667098)

def update_alert_status(alerts, ip, status, offline_users):
    for alert in alerts:
        if alert["ip"] == ip:
            alert["alert"] = status
            alert["offline_users"] = offline_users
            if status == "1":
                alert["alert_time"] = time.time() + 1800  # Añade 30 minutos en segundos.
            break

if __name__ == '__main__':
    alerts = []
    while True:
        try:
            userData = getUsers()
            for i in userData:
                alert = next((a for a in alerts if a['ip'] == i[0]), None)
                if not alert: 
                    alerts.append({"ip":i[0], "offline_users":i[1], "alert":"0", "alert_time":0})
                    alert = alerts[-1]
                if i[1]>50 and alert["alert"] == "0":
                    asyncio.run(sendAlert(i[0], i[1]))
                    update_alert_status(alerts, i[0], "1", i[1])
                elif i[1]<=50 and alert["alert"] == "1":
                    update_alert_status(alerts, i[0], "0", i[1])
                elif alert["alert"] == "1" and time.time() >= alert["alert_time"]:
                    asyncio.run(sendAlert(i[0], i[1]))
                    update_alert_status(alerts, i[0], "1", i[1])
            time.sleep(180)
        except Exception as e:
            logging.error(f"Error en el main: {e}")
            time.sleep(60)