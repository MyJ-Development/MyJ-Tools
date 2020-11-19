from pysnmp.hlapi import *
import time
import mysql.connector
import multiprocessing
import datetime

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
        print("Fallo en insertar en OLT DB Local INSERTOLTDATA  {}".format(error))
    return result

def getOid1KTEPON(address,oid):
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

def getOid2KTEPON(address,oid):
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

def getKTEPON(address):
    response = 0
    KTEPON_position=getOid1KTEPON(address,"iso.3.6.1.4.1.17409.2.3.4.1.1.2")
    KTEPON_mac=getOid2KTEPON(address,"iso.3.6.1.4.1.17409.2.3.4.1.1.7")
    data = []
    for mac in KTEPON_mac:
        find = 0
        try:
            find = [x for x in KTEPON_position if x['id'] == mac['id']]
            find = find[0]
            data.append({"mac_olt":str(mac['mac']).upper(),"pon":str(find['pon']),"slot":str(find['slot'])})
        except:
            print("IP: "+address+" Excepcion en find: "+str(find) + " MAC: "+str(mac['mac'])+ " ID: "+str(mac['id']))
        #print("ID MAC: "+str(mac['id'])+" ID FIND: "+str(find['id'])+ " MAC: "+str(mac['mac'])+ " PON: "+str(find['pon'])+" Slot: "+str(find['slot']) )
    response = insertOltData(address,data)
    if (response):
        print("IP: "+address+" Finalizada")
    else:
        print("IP: "+address+ " Error Insertando Datos")
    #print("Data: "+str(data))

def getOid1EPON1(address,oid):
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
            pon = -1
            slot = -1
            try:
                line =(' = '.join([x.prettyPrint() for x in varBind])) 
                line = line.split("=")
                id = line[0].split(".")
                pon = line[0].split(".")
                pon = pon[-2]
                id = id[-1]
                mac=line[1]
                mac = mac[3:]
                mac = mac.upper()
                data.append({"id":str(id),"pon":str(pon),"mac":str(mac)})
            except Exception as e:
                print("IP: "+address+" Excepcion EPON1 Oid 1: "+str(e)+ " LINE: "+str(line))
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

def getOid2EPON1(address,oid):
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
            pon = -1
            slot = -1
            try:
                line =(' = '.join([x.prettyPrint() for x in varBind])) 
                line = line.split("=")
                id = line[0].split(".")
                pon = line[0].split(".")
                pon = pon[-2]
                id = id[-1]
                slot = line[1]
                #print("ID: "+id+ " PON: "+pon+ " SLOT: "+slot)
                data.append({"id":str(id),"pon":str(pon),"slot":str(slot)})
            except Exception as e:
                print("IP: "+address+" Excepcion EPON1 Oid 2: "+str(e)+ " LINE: "+str(line))
            #print("ID: "+str(id)+" PON: "+str(pon) + " SLOT: "+str(slot))

    if errorIndication:  # SNMP engine errors
        print(errorIndication)
    else:
        if errorStatus:  # SNMP agent errors
            print('%s at %s' % (
                errorStatus.prettyPrint(),
                varBinds[int(errorIndex)-1] if errorIndex else '?'))
    print("Fin Oid 2: "+address)
    print(time.time() - t, 's')
    return data

def getOid1EPON2(address,oid):
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
            pon = -1
            slot = -1
            try:
                line =(' = '.join([x.prettyPrint() for x in varBind])) 
                line = line.split("=")
                #print(line)
                id = line[0].split(".")
                id = id[-1]
                mac=line[1]
                mac = mac[3:]
                mac = mac.upper()
                #print("ID: "+id+ " MAC: "+mac)
                data.append({"id":str(id),"mac":str(mac)})
            except Exception as e:
                pass
                #print("IP: "+address+" Excepcion EPON2 Oid 1: "+str(e)+ " LINE: "+str(line))
            #print("ID: "+str(id)+" PON: "+str(pon) + " SLOT: "+str(slot))

    if errorIndication:  # SNMP engine errors
        print(errorIndication)
    else:
        if errorStatus:  # SNMP agent errors
            print('%s at %s' % (
                errorStatus.prettyPrint(),
                varBinds[int(errorIndex)-1] if errorIndex else '?'))
    print("Fin Oid 2: "+address)
    print(time.time() - t, 's')
    return data

def getOid2EPON2(address,oid):
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
            pon = -1
            slot = -1
            try:
                line =(' = '.join([x.prettyPrint() for x in varBind])) 
                line = line.split("=")
                id = line[0].split(".")
                id = id[-1]
                pon = line[1].split(":")
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

    if errorIndication:  # SNMP engine errors
        print(errorIndication)
    else:
        if errorStatus:  # SNMP agent errors
            print('%s at %s' % (
                errorStatus.prettyPrint(),
                varBinds[int(errorIndex)-1] if errorIndex else '?'))
    print("Fin Oid 2: "+address)
    print(time.time() - t, 's')
    return data

def getEPON1(address):
    response = 0
    EPON1_position=getOid2EPON1(address,"1.3.6.1.4.1.34592.1.3.3.12.1.1.3.1")
    EPON1_mac=getOid1EPON1(address,"1.3.6.1.4.1.34592.1.3.3.12.1.1.4.1")
    data = []
    for mac in EPON1_mac:
        find = 0
        try:
            find = [x for x in EPON1_position if x['id'] == mac['id']]
            find = find[0]
            #print(mac['id']+" " +mac['mac'] + " " + mac['pon']+ " " + find['slot'])
            data.append({"mac_olt":str(mac['mac']),"pon":str(mac['pon']),"slot":str(find['slot'])})
        except:
            print("IP: "+address+" Excepcion en find: "+str(find) + " MAC: "+str(mac['mac'])+ " ID: "+str(mac['id']))
        #print("ID MAC: "+str(mac['id'])+" ID FIND: "+str(find['id'])+ " MAC: "+str(mac['mac'])+ " PON: "+str(find['pon'])+" Slot: "+str(find['slot']) )
    response = insertOltData(address,data)
    if (response):
        print("IP: "+address+" Finalizada")
    else:
        print("IP: "+address+ " Error Insertando Datos")
    #print("Data: "+str(data))

def getEPON2(address):
    response = 0
    EPON2_mac=getOid1EPON2(address,"1.3.6.1.2.1.2.2.1.6")
    EPON2_position=getOid2EPON2(address,"1.3.6.1.2.1.2.2.1.2")
    
    data = []
    for mac in EPON2_mac:
        find = 0
        try:
            find = [x for x in EPON2_position if x['id'] == mac['id']]
            find = find[0]
            #print(mac['id']+" " +mac['mac'] + " " + find['pon']+ " " + find['slot'])
            data.append({"mac_olt":str(mac['mac']),"pon":str(find['pon']),"slot":str(find['slot'])})
        except:
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
    a = 0
    for ip in KTEPON:
        p.append(multiprocessing.Process(target=getKTEPON, args=(ip,)))
        p[pcounter].start()
        pcounter = pcounter + 1
        
    for ip in EPON1:
        #getEPON1("172.16.50.109")
        p.append(multiprocessing.Process(target=getEPON1, args=(ip,)))
        p[pcounter].start()
        pcounter = pcounter + 1
        
    for ip in EPON2:
        #getEPON1("172.16.50.109")
        p.append(multiprocessing.Process(target=getEPON2, args=(ip,)))
        p[pcounter].start()
        pcounter = pcounter + 1
        
    TIMEOUT = 900
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