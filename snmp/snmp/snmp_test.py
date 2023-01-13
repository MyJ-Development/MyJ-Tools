import mysql.connector
from easysnmp import *
from pysnmp.hlapi import *
import time
import multiprocessing
import datetime
import math
import requests
import json

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
        try:
            rx = i['db']
        except:
            rx = ""
        dataQuery = dataQuery + "('"+str(address)+"','" +"null"+ "','" +str(i['mac_olt'])+ "','"+ str(i['pon'])+ "','" + str(i['slot']) + "','"+ str(rx) +"','"+str(tx)+ "'),"

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
        print(str(cursor.rowcount)+" IP: "+ address +" Cantidad de pppoe insertados correctamente en DB local: ")
        cursor.close()
        result = 1
    except mysql.connector.Error as error:
        print("IP: "+address+" Fallo en insertar en OLT DB Local INSERTOLTDATA  {}".format(error))
    if(result==0):
        time.sleep(1)
        result = insertOltData(address,data)
    if(result==1):
        print(str(cursor.rowcount)+" IP: "+ address +" Insertado Correctamente")

    return result

def getZTE():
    url = "https://myjchile.smartolt.com/api/onu/get_onus_signals"
    payload = {}
    headers = {
    'X-Token': 'bb62f634c0d2464cacaee86e43358d39'
    }
    response = requests.request("GET", url, headers=headers, data = payload)
    response = response.json()
    data = []
    for line in response['response']:
        #print(line['sn']+" "+line['port']+" "+line['onu']+" "+line['signal_1310'])
        data.append({"mac_olt":line['sn'],"pon":line['port'],"slot":line['onu'],"db":line['signal_1310']} )
    insertOltData("172.16.50.135",data)



def getMac(address):
    userQuery = "select mac_olt,pon,slot from olt where ip_olt='"+address+"';"
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
        print("Fallo en obtener datos desde ISPCube  {}".format(error))
    return result

def getOid1KTEPON(address,session,oid):
    data = []
    t = time.time()
    ret = "null"
    try:
        ret = session.bulkwalk(oid)
    except Exception as e:
        print("IP: " +address+ " ERROR - SNMP error: {}".format(e))
    for line in ret:
        pon = -1
        slot = -1
        try:
            id = line.oid
            id = str(id).split(".")
            id = id[-1]
            pon = str(line.value).split(":")
            slot = str(pon[1]).replace('"',"")
            pon = str(pon[0]).split("/")
            pon = pon[1]
            #print(" id "+str(id)+" pon "+str(pon)+" slot"+str(slot))
            data.append({"id":str(id),"pon":str(pon),"slot":str(slot)})
        except Exception as e:
            print("IP: "+address+" Excepcion KTEPON Oid 1: "+str(e)+ " LINE: "+str(line))
        #print("ID: "+str(id)+" PON: "+str(pon) + " SLOT: "+str(slot))
    print("Fin Oid 1: "+address)
    print(time.time() - t, 's')
    
    return data

def getOid2KTEPON(address,session,oid):
    data = []
    t = time.time()
    ret = "null"
    try:
        ret = session.bulkwalk(oid)
    except Exception as e:
        print("IP: " +address+ " ERROR - SNMP error: {}".format(e))
    for line in ret:
        try:
            mac = line.value
            mac = mac.replace(" ","").replace('"',"")
            id = line.oid
            id = id.split(".")
            id = id[-1]
            #print("ID: "+str(id)+" PON: "+str(pon) + " SLOT: "+str(slot))
            #print("ID:"+str(id)+" MAC :"+str(mac))
            data.append({"id":str(id),"mac":str(mac)})
        except Exception as e:
            pass
            print("IP: "+address+" Excepcion KTEPON Oid 2: "+str(e)+ " LINE: "+str(line))

    print("Fin Oid 2: "+address)
    print(time.time() - t, 's')
    return data

def getOid3KTEPON(address,session,oid):
    data = []
    t = time.time()
    ret = "null"
    try:
        ret = session.bulkwalk(oid)
    except Exception as e:
        print("IP: " +address+ " ERROR - SNMP error: {}".format(e))
    for line in ret:
        try: 
            
            id = str(line.oid).split(".")
            id = id[-4]
            db = line.value
            if(db!='0'):
                db = db[:3] + ',' + db[3:]
            #print("ID: "+str(id)+" MAC : "+str(db))
            data.append({"id":str(id),"db":str(db)})
        except Exception as e:
            print("IP: "+address+" Excepcion KTEPON Oid 3: "+str(e)+ " LINE: "+str(line))

    print("Fin Oid 3: "+address)
    print(time.time() - t, 's')
    return data

def getKTEPON(address):
    response = 0
    #.1.3.6.1.4.1.17409.2.3.4.2.1.13 <- Potencia
    try:
        session = Session(hostname=address,community="public", version=2,timeout=100,retries=10,use_sprint_value=True)
        print("Sesion: "+address+" Correcta")
    except Exception as e:
        print("IP: " +address+ " ERROR - SNMP error: {}".format(e))

    KTEPON_position=getOid1KTEPON(address,session,"iso.3.6.1.4.1.17409.2.3.4.1.1.2")
    KTEPON_mac=getOid2KTEPON(address,session,"iso.3.6.1.4.1.17409.2.3.4.1.1.7")
    KTEPON_db = getOid3KTEPON(address,session,".1.3.6.1.4.1.17409.2.3.4.2.1.13")
    data = []
    for mac in KTEPON_mac:
        find = 0
        try:
            
            find = [x for x in KTEPON_position if x['id'] == mac['id']]
            find = find[0]
            find_db = [x for x in KTEPON_db if int(x['id']) == int(mac['id'])]
            find_db = find_db[0]
            #print("ID MAC: "+str(mac['id'])+" ID FIND: "+str(find['id'])+ " MAC: "+str(mac['mac'])+ " PON: "+str(find['pon'])+" Slot: "+str(find['slot'])+" dBm: "+str(find_db['db']) )
            data.append({"mac_olt":str(mac['mac']).upper(),"pon":str(find['pon']),"slot":str(find['slot']),"db":str(find_db['db'])})
        except:
            print("IP: "+address+" Excepcion en find: " + " MAC: "+str(mac['mac'])+ " ID: "+str(mac['id']))
    response = insertOltData(address,data)
    
    if (response):
        print("IP: "+address+" Datos insertados correctamente")
        print("IP: "+address+" Finalizada")
    else:
        print("IP: "+address+ " Error Insertando Datos")
    #print("Data: "+str(data))

def getOid1KTEPON101(address,oid):
    data = []
    t = time.time()
    iterator = bulkCmd(SnmpEngine(),
                    CommunityData('public'),
                    UdpTransportTarget((address, 161)),
                    ContextData(),
                    0,20,
                    ObjectType(ObjectIdentity(oid)),
            lookupMib=False, lexicographicMode=False)
    print("Sesion: "+address+" Correcta")
    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
    for (errorIndication, errorStatus, errorIndex, varBinds) in iterator:
        for varBind in varBinds:
            pon = -1
            slot = -1
            try:
                line =(' = '.join([x.prettyPrint() for x in varBind])) 
                line = line.split("=")
                id = line[0].split(".")
                id = id[-1]
                pon = line[1].split(":")
                slot = pon[1]
                pon = pon[0].split("/")[1]
                data.append({"id":str(id),"pon":str(pon),"slot":str(slot)})
            except Exception as e:
                print("IP: "+address+" Excepcion KTEPON Oid 1: "+str(e)+ " LINE: "+str(line))
            #print("ID: "+str(id)+" PON: "+str(pon) + " SLOT: "+str(slot))

    if errorIndication:  # SNMP engine errors
        print(errorIndication)
    else:
        if errorStatus:  # SNMP agent errors
            print('%s at %s' % (
                errorStatus.prettyPrint(),
                varBinds[int(errorIndex)-1] if errorIndex else '?'))
    print("Fin Oid 1: "+address)
    print(time.time() - t, 's')
    
    return data

def getOid2KTEPON101(address,oid):
    data = []
    t = time.time()
    iterator = bulkCmd(SnmpEngine(),
                    CommunityData('public'),
                    UdpTransportTarget((address, 161)),
                    ContextData(),
                    0,20,
                    ObjectType(ObjectIdentity(oid)),
            lookupMib=False, lexicographicMode=False)

    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

    for (errorIndication, errorStatus, errorIndex, varBinds) in iterator:
        for varBind in varBinds:
            try: 
                line =(' = '.join([x.prettyPrint() for x in varBind]))
                line = line.split("=")
                id = line[0].split(".")
                id = id[-1]
                mac = line[1]
                mac = mac[3:]
                #print("ID: "+str(id)+" PON: "+str(pon) + " SLOT: "+str(slot))
                #print("ID:"+str(id)+"MAC : "+str(mac))
                data.append({"id":str(id),"mac":str(mac)})
            except Exception as e:
                print("IP: "+address+" Excepcion KTEPON Oid 2: "+str(e)+ " LINE: "+str(line))

    if errorIndication:  # SNMP engine errors
        print("IP: "+address+" Error en snmp:"+str(errorIndication))
    else:
        if errorStatus:  # SNMP agent errors
            print('%s at %s' % (
                errorStatus.prettyPrint(),
                varBinds[int(errorIndex)-1] if errorIndex else '?'))

    print("Fin Oid 2: "+address)
    print(time.time() - t, 's')
    return data

def getOid3KTEPON101(address,oid):
    data = []
    t = time.time()
    iterator = bulkCmd(SnmpEngine(),
                    CommunityData('public'),
                    UdpTransportTarget((address, 161)),
                    ContextData(),
                    0,20,
                    ObjectType(ObjectIdentity(oid)),
            lookupMib=False, lexicographicMode=False)

    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

    for (errorIndication, errorStatus, errorIndex, varBinds) in iterator:
        for varBind in varBinds:
            try: 
                line =(' = '.join([x.prettyPrint() for x in varBind]))
                line = line.split("=")
                id = line[0].split(".")
                id = id[-4]
                db = line[1]
                if(db!=' 0'):
                    db = db[:4] + ',' + db[4:]
                #print("ID:"+str(id)+"MAC : "+str(mac))
                data.append({"id":str(id),"db":str(db)})
            except Exception as e:
                print("IP: "+address+" Excepcion KTEPON Oid 3: "+str(e)+ " LINE: "+str(line))

    if errorIndication:  # SNMP engine errors
        print("IP: "+address+" Error en snmp:"+str(errorIndication))
    else:
        if errorStatus:  # SNMP agent errors
            print('%s at %s' % (
                errorStatus.prettyPrint(),
                varBinds[int(errorIndex)-1] if errorIndex else '?'))

    print("Fin Oid 3: "+address)
    print(time.time() - t, 's')
    return data

def getKTEPON101(address):
    response = 0
    #.1.3.6.1.4.1.17409.2.3.4.2.1.13 <- Potencia
    KTEPON_position=getOid1KTEPON101(address,"iso.3.6.1.4.1.17409.2.3.4.1.1.2")
    KTEPON_mac=getOid2KTEPON101(address,"iso.3.6.1.4.1.17409.2.3.4.1.1.7")
    KTEPON_db = getOid3KTEPON101(address,".1.3.6.1.4.1.17409.2.3.4.2.1.13")
    
    data = []
    for mac in KTEPON_mac:
        find = 0
        try:
            find = [x for x in KTEPON_position if x['id'] == mac['id']]
            find = find[0]
            find_db = [x for x in KTEPON_db if int(x['id']) == int(mac['id'])]
            find_db = find_db[0]
            #print("ID MAC: "+str(mac['id'])+" ID FIND: "+str(find['id'])+ " MAC: "+str(mac['mac'])+ " PON: "+str(find['pon'])+" Slot: "+str(find['slot'])+" dBm: "+str(find_db['db']) )
            data.append({"mac_olt":str(mac['mac']).upper(),"pon":str(find['pon']),"slot":str(find['slot']),"db":str(find_db['db'])})
        except:
            print("IP: "+address+" Excepcion en find: " + " MAC: "+str(mac['mac'])+ " ID: "+str(mac['id']))

    response = insertOltData(address,data)
    if (response):
        print("IP: "+address+" Finalizada")
    else:
        print("IP: "+address+ " Error Insertando Datos")
    #print("Data: "+str(data))

def getOid1EPON1(address,session,oid):
    data = []
    t = time.time()
    ret = "null"
    try:
        ret = session.bulkwalk(oid)
    except Exception as e:
        print("IP: " +address+ " ERROR - SNMP error: {}".format(e))

    for line in ret:
        pon = -1
        slot = -1
        try:
            mac = line.value
            id = line.oid.split(".")
            pon = id[-2]
            id = id[-1]
            mac = str(mac).replace(" ","").replace('"',"").upper()
            data.append({"id":str(id),"pon":str(pon),"mac":str(mac)})
        except Exception as e:
            print("IP: "+address+" Excepcion EPON1 Oid 1: "+str(e)+ " LINE: "+str(line))
            #print("ID: "+str(id)+" PON: "+str(pon) + " SLOT: "+str(slot))

    print("Fin Oid 1: "+address)
    print(time.time() - t, 's')
    return data

def getOid2EPON1(address,session,oid):
    data = []
    t = time.time()
    ret = "null"
    try:
        ret = session.bulkwalk(oid)
    except Exception as e:
        print("IP: " +address+ " ERROR - SNMP error: {}".format(e))
        pon = -1
        slot = -1
    for line in ret:
        try:
            #line =(' = '.join([x.prettyPrint() for x in varBind])) 
            #line = line.split("=")
            slot = line.value
            id = line.oid.split(".")
            pon = id[-2]
            id = id[-1]
            #print("ID: "+id+ " PON: "+pon+ " SLOT: "+slot)
            data.append({"id":str(id),"pon":str(pon),"slot":str(slot)})
        except Exception as e:
            print("IP: "+address+" Excepcion EPON1 Oid 2: "+str(e)+ " LINE: "+str(line))
        #print("ID: "+str(id)+" PON: "+str(pon) + " SLOT: "+str(slot))

    print("Fin Oid 2: "+address)
    print(time.time() - t, 's')
    return data

def getOid3EPON1(address,session,oid):
    data = []
    t = time.time()
    ret = "null"
    try:
        ret = session.bulkwalk(oid)
    except Exception as e:
        print("IP: " +address+ " ERROR - SNMP error: {}".format(e))
        pon = -1
        slot = -1
    for line in ret:
        pon = -1
        db = -1
        try:
            #line =(' = '.join([x.prettyPrint() for x in varBind])) 
            #line = line.split("=")
            #print(line)
            db = line.value
            id = line.oid.split(".")
            pon = id[-2]
            id = id[-1]
            if(float(db)):
                try:
                    db = "0.00"+db
                    db = float((10*math.log(float(db),10)))
                except:
                    print("error: "+db)
            #print("IP: "+address+" SLOT: "+id+ " PON: "+pon+ " DB: "+str(db))
            data.append({"slot":str(id),"pon":str(pon),"db":str(db)})
        except Exception as e:
            print("IP: "+address+" Excepcion EPON1 Oid 3: "+str(e)+ " LINE: "+str(line))
        #print("ID: "+str(id)+" PON: "+str(pon) + " SLOT: "+str(slot))

    print("Fin Oid 3: "+address)
    print(time.time() - t, 's')
    return data

def getOid1EPON2(address,session,oid):
    data = []
    t = time.time()
    ret = "null"
    try:
        ret = session.bulkwalk(oid)
    except Exception as e:
        print("IP: " +address+ " ERROR - SNMP error: {}".format(e))
        pon = -1
        slot = -1

    for line in ret:
        pon = -1
        slot = -1
        try:
            id = line.oid
            id = id.split(".")
            id = id[-1]
            mac=line.value
            mac=str(mac).replace(" ","").replace('"',"")
            #print("ID: "+id+ " MAC: "+mac)
            data.append({"id":str(id),"mac":str(mac)})
        except Exception as e:
            pass
                #print("IP: "+address+" Excepcion EPON2 Oid 1: "+str(e)+ " LINE: "+str(line))
            #print("ID: "+str(id)+" PON: "+str(pon) + " SLOT: "+str(slot))
    print("Fin Oid 1: "+address)
    print(time.time() - t, 's')
    return data

def getOid2EPON2(address,session,oid):
    data = []
    t = time.time()
    ret = "null"
    try:
        ret = session.bulkwalk(oid)
    except Exception as e:
        print("IP: " +address+ " ERROR - SNMP error: {}".format(e))
        pon = -1
        slot = -1

    for line in ret:
        pon = -1
        slot = -1
        try:
            id = str(line.oid).split(".")
            id = id[-1]
            pon = str(line.value).replace('"',"").replace(" ","").split(":")
            slot = pon[1]
            pon = pon[0]
            pon = pon.split("/")
            pon = pon[1]
            #print("ID: "+id+" PON: "+pon+" SLOT: "+slot)
            data.append({"id":str(id),"pon":str(pon),"slot":str(slot)})
        except Exception as e:
            pass
            #print("IP: "+address+" Excepcion EPON2 Oid 2: "+str(e)+ " LINE: "+str(line))
        #print("ID: "+str(id)+" PON: "+str(pon) + " SLOT: "+str(slot))

    print("Fin Oid 2: "+address)
    print(time.time() - t, 's')
    return data

def getOid3EPON2(address,session,oid):
    data = []
    t = time.time()
    ret = "null"
    try:
        ret = session.bulkwalk(oid)
    except Exception as e:
        print("IP: " +address+ " ERROR - SNMP error: {}".format(e))
        pon = -1
        slot = -1

    for line in ret:
        pon = -1
        slot = -1
        try:
            id = str(line.oid).split(".")
            slot = id[-1]
            pon = id[-2]
            db = str(line.value)
            db = db[:-6]
            db = db[10:]
            db = str(db).replace(".",",")
            #print("PON: "+pon+" SLOT: "+slot+" DB: "+db)
            data.append({"pon":str(pon),"slot":str(slot),"db":str(db)})
        except Exception as e:
            pass
            #print("IP: "+address+" Excepcion EPON2 Oid 2: "+str(e)+ " LINE: "+str(line))
        #print("ID: "+str(id)+" PON: "+str(pon) + " SLOT: "+str(slot))

    print("Fin Oid 3: "+address)
    print(time.time() - t, 's')
    return data

def getEPON1(address):
    response = 0
    try:
        session = Session(hostname=address,community="public", version=2,timeout=100,retries=10,use_sprint_value=True)
        print("Sesion: "+address+" Correcta")
    except:
        print("IP: "+address+" ERROR - SNMP error:")

    EPON1_mac=getOid1EPON1(address,session,"1.3.6.1.4.1.34592.1.3.3.12.1.1.4.1")
    EPON1_position=getOid2EPON1(address,session,"1.3.6.1.4.1.34592.1.3.3.12.1.1.3.1")
    olt_mac = getMac(address)
    connected = 1
    EPON1_db = 0
    while(connected):
        EPON1_db=getOid3EPON1(address,session,"iso.3.6.1.4.1.34592.1.3.4.1.1.36.1")
        if(EPON1_db):
            connected = 0
        else:
            print("IP: "+address+" Error SNMP ")
        time.sleep(5)
    data = []
    for mac in olt_mac:
        find = 0
        try:
            find = [x for x in EPON1_mac if x['mac'] == mac[0]]
            if(find):
                pass
            else:
                db = 0
            #print("mac_olt " + str(mac[0])+ " pon "+str(mac[1])+" slot "+str(mac[2])+" db "+str(db))    
            data.append({"mac_olt":str(mac[0]),"pon":str(mac[1]),"slot":str(mac[2]),"db":str(db)})
        except Exception as e:
            pass
            #print("IP: "+address+" Excepcion en find: "+str(find) + " MAC: "+str(mac['mac'])+ " ID: "+str(mac['id']))    
        #print("ID MAC: "+str(mac['id'])+" ID FIND: "+str(find['id'])+ " MAC: "+str(mac['mac'])+ " PON: "+str(find['pon'])+" Slot: "+str(find['slot']) )
    if(data):
        response = insertOltData(address,data)




    for mac in EPON1_mac:
        find = 0
        try:
            db = 0
            find = [x for x in EPON1_position if x['id'] == mac['id']]
            find = find[0]
            find_db = [x for x in EPON1_db if x['pon'] == mac['pon']]
            if(find_db):
                try:
                    db = [x for x in find_db if x['slot'] == find['slot']]
                    db = db[0]
                    db = db['db']
                    db = db[:6]
                    db = db.replace(".",",")
                except:
                    db = 0
            else:
                print("not found")
                db = 0
            #print(mac['id']+" " +mac['mac'] + " " + mac['pon']+ " " + find['slot']+" "+str(db))
            data.append({"mac_olt":str(mac['mac']),"pon":str(mac['pon']),"slot":str(find['slot']),"db":str(db)})
        except Exception as e:
            print(e)
            print("IP: "+address+" Excepcion en find: "+str(find) + " MAC: "+str(mac['mac'])+ " ID: "+str(mac['id']))
    response = insertOltData(address,data)

    #print(EPON1_potencia)
    if (response):
        print("IP: "+address+" Finalizada")
    else:
        print("IP: "+address+ " Error Insertando Datos")
    #print("Data: "+str(data))

def getEPON2(address):
    response = 0
    try:
        session = Session(hostname=address,community="public", version=2,timeout=100,retries=10,use_sprint_value=True)
        print("Sesion: "+address+" Correcta")
    except Exception as e:
        print("IP: " +address+ " ERROR - SNMP error: {}".format(e))
    
    EPON2_mac=getOid1EPON2(address,session,"1.3.6.1.2.1.2.2.1.6")
    EPON2_position=getOid2EPON2(address,session,"1.3.6.1.2.1.2.2.1.2")
    connected = 1
    EPON2_db = 0
    olt_mac = getMac(address)
    while(connected):
        EPON2_db=getOid3EPON2(address,session,"iso.3.6.1.4.1.37950.1.1.5.12.2.1.8.1.7")
        if(EPON2_db):
            connected = 0
        time.sleep(5)
    data = []

    for mac in olt_mac:
        try:
            #print("Mac a buscar: "+str(mac))
            find = [x for x in EPON2_mac if x['mac'] == mac[0]]
            if(find):
                pass
                #print("Encontrado: "+str(find))
            else:
                db = 0
                #print("No Encontrado: "+str(mac))
            data.append({"mac_olt":str(mac[0]),"pon":str(mac[1]),"slot":str(mac[2]),"db":str(db)})
        except Exception as error:
            pass

    if(data):
        response = insertOltData(address,data)

    for mac in EPON2_mac:
        find = 0
        try:
            find = [x for x in EPON2_position if x['id'] == mac['id']]
            find = find[0]

            find_db = [x for x in EPON2_db if x['pon'] == find['pon']]
            if(find_db):
                try:
                    db = [x for x in find_db if x['slot'] == find['slot']]
                    db = db[0]
                    db = db['db']
                except:
                    db = 0

            else:
                db = 0
            #print(mac['id']+" " +mac['mac'] + " " + find['pon']+ " " + find['slot']+" "+str(db))
            data.append({"mac_olt":str(mac['mac']),"pon":str(find['pon']),"slot":str(find['slot']),"db":str(db)})
        except Exception as e:
            pass
            #print("IP: "+address+" Excepcion en find: "+str(find) + " MAC: "+str(mac['mac'])+ " ID: "+str(mac['id']))
        #print("ID MAC: "+str(mac['id'])+" ID FIND: "+str(find['id'])+ " MAC: "+str(mac['mac'])+ " PON: "+str(find['pon'])+" Slot: "+str(find['slot']) )
    response = insertOltData(address,data)
    if (response):
        print("IP: "+address+" Finalizada")
    else:
        print("IP: "+address+ " Error Insertando Datos")
    #print("Data: "+str(data))

def readKTEPON():
    f = open("KTEPON.txt","r")
    response = []
    for i in f:
        response.append(str(i).replace("\n",""))
    return response

def readEPON1():
    f = open("EPON1.txt","r")
    response = []
    for i in f:
        response.append(str(i).replace("\n",""))
    return response

def readEPON2():
    f = open("EPON2.txt","r")
    response = []
    for i in f:
        response.append(str(i).replace("\n",""))
    return response

def main():
    KTEPON = readKTEPON()
    EPON1 = readEPON1()
    EPON2 = readEPON2()
    p = []
    pcounter = 0
    t = time.time()
    getZTE()
    for ip in KTEPON:
        if(ip!="172.16.50.101"):
            p.append(multiprocessing.Process(target=getKTEPON, args=(ip,)))
        else:
            p.append(multiprocessing.Process(target=getKTEPON101, args=(ip,)))
        p[pcounter].start()
        pcounter = pcounter + 1
        pass
    
    for ip in EPON1:
        #getEPON1("172.16.50.109")
        p.append(multiprocessing.Process(target=getEPON1, args=(ip,)))
        p[pcounter].start()
        pcounter = pcounter + 1
        #pass

    for ip in EPON2:
        p.append(multiprocessing.Process(target=getEPON2, args=(ip,)))
        p[pcounter].start()
        pcounter = pcounter + 1
        pass

    TIMEOUT = 1500
    start = time.time()
    logDate = datetime.datetime.today()
    logDate = datetime.datetime(logDate.year, logDate.month, logDate.day,logDate.hour,logDate.minute)
    while time.time() - start <= TIMEOUT:
        if not any(line.is_alive() for line in p):
            # All the processes are done, break now.
            logDate = datetime.datetime.today()
            logDate = datetime.datetime(logDate.year, logDate.month, logDate.day,logDate.hour,logDate.minute)
            print("Hora termino: " +str(logDate))
            break
        time.sleep(5)  # Just to avoid hogging the CPU
    else:
        # We only enter this if we didn't 'break' above.
        print("timed out, killing all processes")
        logDate = datetime.datetime.today()
        logDate = datetime.datetime(logDate.year, logDate.month, logDate.day,logDate.hour,logDate.minute)
        print("Hora termino: " +str(logDate))
        for line in p:
            line.terminate()
            line.join()

main()
