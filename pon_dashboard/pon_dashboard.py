import requests
import mysql.connector
import time

class MySQL_LOCAL:
  def __init__(self):
    self.host = '10.19.11.2'
    self.user = 'myjdev'
    self.password = 'myjdev'
    self.database = 'olt_sync'

def insertOltData(data):
    query = """
        INSERT INTO pon_dashboard (olt, board, pon, down)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE down = VALUES(down);
    """
    
    MySQLInfo = MySQL_LOCAL()
    
    try:
        connection = mysql.connector.connect(
            host=MySQLInfo.host,
            database=MySQLInfo.database,
            user=MySQLInfo.user,
            password=MySQLInfo.password
        )
        
        cursor = connection.cursor()
        
        # Convertir la lista de diccionarios en una lista de tuplas
        data_tuples = [(equipo['olt'], equipo['board'], equipo['pon'], equipo['down']) for equipo in data]
        
        # Ejecutar la inserción con ON DUPLICATE KEY UPDATE
        cursor.executemany(query, data_tuples)
        
        connection.commit()
        print(str(cursor.rowcount) + " Cantidad de registros insertados o actualizados correctamente en DB local")
        
        cursor.close()
        result = 1
    except mysql.connector.Error as error:
        print("Fallo en insertar/actualizar en OLT DB Local INSERTOLTDATA  {}".format(error))
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
            data.append({"mac_olt":line['sn'],"pon":line['port'],"slot":line['onu'],"rx":line['signal_1310'],"board":line["board"]})
    except Exception as e:
        print("Fallo en getZTE: "+str(e))
        return -1
        
    equipos_por_board_pon = {}

    # Recorrer los datos y contar equipos con rx "-" y los que no por board y pon
    for equipo in data:
        board = equipo['board']
        rx = equipo['rx']
        pon = equipo['pon']
        
        if board not in equipos_por_board_pon:
            equipos_por_board_pon[board] = {}
        
        if pon not in equipos_por_board_pon[board]:
            equipos_por_board_pon[board][pon] = {'con_rx': 0, 'sin_rx': 0}
        
        if rx == '-':
            equipos_por_board_pon[board][pon]['con_rx'] += 1
        else:
            equipos_por_board_pon[board][pon]['sin_rx'] += 1

    # Ordenar las claves de PON de forma incremental
    for board, pons in equipos_por_board_pon.items():
        pons_sorted = sorted(pons.keys(), key=lambda x: int(x))
        equipos_por_board_pon[board] = {pon: pons[pon] for pon in pons_sorted}

    # Contar la cantidad total de equipos por board y pon
    oltData = []
    for board, pons in equipos_por_board_pon.items():
        for pon, conteo in pons.items():
            total = conteo['con_rx'] + conteo['sin_rx']
            oltData.append({"olt":olt_data["name"],"board":board,"pon":pon,"down":str(conteo["con_rx"])+"/"+str(total)})
    insertOltData(oltData)
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