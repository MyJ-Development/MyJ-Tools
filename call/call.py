from asterisk.ami import *
import mysql.connector
import requests
import time
from datetime import datetime
import re

class MySQL_ISPCUBE:
  def __init__(self):
    self.host = '170.239.188.10'
    self.user = 'myjdev'
    self.password = '2020myjdev'
    self.database = '105'

class MySQL_GRAFANA:
  def __init__(self):
    self.host = '10.19.11.9'
    self.user = 'myjdev'
    self.password = 'myjdev'
    self.database = 'olt_sync'

def getISPCUBE():
    userQuery = 'select * from customer where status = 0 and duedebt>0 and idcustomer not like "%ZZ%" and free=0'
    #userQuery = 'select * from customer where status = 0 and duedebt>0  and idcustomer not like "%ZZ%"'
    
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
        connection.close()
    except mysql.connector.Error as error:
        print("Fallo en obtener datos desde ISPCube  {}".format(error))
    
    return result

def getNumber(rut):
    URL = "http://10.19.11.9:3003/api/scheduler/client?rut="+str(rut)
    #PARAMS = {'address':location}
    r = requests.get(url = URL)
    data = r.json()
    return data

def callClient(number):
    client = AMIClient(address='170.239.188.18',port=5038)
    client.login(username='MYJBOT',secret='myjbot2020')
    action = SimpleAction(
        'Originate',
        Channel='SIP/siptrunk1000/'+str(number),
        Exten='999',
        Priority=1,
        Context='Deudores',
        CallerID='python',
    )
    future = client.send_action(action)
    response = future.response
    client.logoff()

def insertNumber(data):
    dataQuery = ''
    for i in data:
        rx = "null"
        tx = "null"
        dataQuery = dataQuery + "('"+str(i)+"'),"
    dataQuery = dataQuery[:-1]
    userQuery = "insert ignore into callHistory (telefono) values " + dataQuery +";"
    result = 0
    MySQLInfo = MySQL_GRAFANA()
    try:
        connection = mysql.connector.connect(host=MySQLInfo.host,
                                         database=MySQLInfo.database,
                                         user=MySQLInfo.user,
                                         password=MySQLInfo.password)
        cursor = connection.cursor()
        cursor.execute(userQuery)
        connection.commit()
        print(str(cursor.rowcount)+" >>> Nuevos numeros insertados ")
        cursor.close()
        result = 1
    except mysql.connector.Error as error:
        print("Fallo en insertar telefonos  {}".format(error))

    except Exception as error:
        print(error)
    return result

def insertCallDate(telefono,date):
    dataQuery = ''
    dataQuery = dataQuery + "('"+str(date)+"')"
    userQuery = "update callHistory set last_call='"+date+"' where telefono ='"+telefono+"';"
    result = 0
    MySQLInfo = MySQL_GRAFANA()
    try:
        connection = mysql.connector.connect(host=MySQLInfo.host,
                                         database=MySQLInfo.database,
                                         user=MySQLInfo.user,
                                         password=MySQLInfo.password)
        cursor = connection.cursor()
        cursor.execute(userQuery)
        connection.commit()
        print(str(cursor.rowcount)+" fecha de llamado actualizada! ")
        cursor.close()
        result = 1
    except mysql.connector.Error as error:
        print("Fallo en insertar en OLT DB Local INSERT PPPoE Data  {}".format(error))

    except Exception as error:
        print(error)
    return result

def checkCall(telefono,date):
    userQuery = 'select *  from callHistory where telefono="'+telefono+'";'
    result = 0
    MySQLInfo = MySQL_GRAFANA()
    try:
        connection = mysql.connector.connect(host=MySQLInfo.host,
                                         database=MySQLInfo.database,
                                         user=MySQLInfo.user,
                                         password=MySQLInfo.password)
        cursor = connection.cursor()
        cursor.execute(userQuery)
        result = cursor.fetchall()
        cursor.close()
        connection.close()
    except mysql.connector.Error as error:
        print("Fallo en obtener datos desde ISPCube  {}".format(error))
    
    return result

deudores=getISPCUBE()
##callClient('945760262')
print(str(len(deudores)))
find = re.compile(r'(9[.0-9]{8})')
exit(1)

i = 0
numberList = []

for line in deudores:
    ##callClient('945760262')
    data = getNumber(line[14])
    valid = re.search(find,data['contacto1'])
    if(valid):
        #print(valid[0])
        numberList.append(valid[0])
    i += 1
    #pass
insertNumber(numberList)

for line in deudores:
    if(datetime.today().strftime('%d') == '05'):
        if(line[31] == '30'):
            data = getNumber(line[14])
            if(data):
                #print(data)
                print(line[14])
                print(data['contacto1'] + " :::: "+data['contacto2'])
                valid = re.search(find,data['contacto1'])
                if(valid):
                    print("numero 1 valido! verificando si se ha llamado..."+ str(valid[0]))
                    called = checkCall(valid[0],"07-05")
                    try:
                        number = ""
                        date = ""
                        try:
                            number=str(called[0][0])
                            date=str(called[0][1])
                        except:
                            exists = ""
                        if("07-05" in date):
                            print("Ya se ha llamado a este cliente")
                        elif(str(valid[0]) in number):
                            print("Llamando... "+ str(valid[0]))
                            callClient(valid[0])
                            insertCallDate(str(valid[0]),str(datetime.today()))
                            time.sleep(15)
                    except Exception as e:
                        print(str(valid)+ " Excepcion!: "+str(e))
                else:
                    print("numero 1 no valido")
                time.sleep(1)
                if(data['contacto1'] != data['contacto2']):
                    valid = re.search(find,data['contacto2'])
                    if(re.search(find,data['contacto2'])):
                        print("numero 2 valido! verificando si se ha llamado..."+ str(valid[0]))
                        called = checkCall(valid[0],"07-05")
                        try:
                            number = ""
                            date = ""
                            try:
                                number=str(called[0][0])
                                date=str(called[0][1])
                            except:
                                exists = ""
                            if("07-05" in date):
                                print("Ya se ha llamado a este cliente")
                            elif(str(valid[0]) in number):
                                print("Llamando... "+ str(valid[0]))
                                callClient(valid[0])
                                insertCallDate(str(valid[0]),str(datetime.today()))
                                time.sleep(15)
                        except Exception as e:
                                print(str(valid)+ " Excepcion!: "+str(e))
                    else:
                        print("numero 2 no valido")
                time.sleep(1)

    if(datetime.today().strftime('%d') == '05'):
        if(line[31] == '15'):
            data = getNumber(line[14])
            if(data):
                print(line[14])
                print(data['contacto1'] + " :::: "+data['contacto2'])
                valid = re.search(find,data['contacto1'])
                if(valid):
                    print("numero 1 valido! verificando si se ha llamado..."+ str(valid[0]))
                    called = checkCall(valid[0],"07-05")
                    try:
                        number = ""
                        date = ""
                        try:
                            number=str(called[0][0])
                            date=str(called[0][1])
                        except:
                            exists = ""
                        if("07-05" in date):
                            print("Ya se ha llamado a este cliente")
                        elif(str(valid[0]) in number):
                            print("Llamando... "+ str(valid[0]))
                            callClient(valid[0])
                            insertCallDate(str(valid[0]),str(datetime.today()))
                            time.sleep(15)
                    except Exception as e:
                        print(str(valid)+ " Excepcion!: "+str(e))
                else:
                    print("numero 1 no valido")
                time.sleep(1)
                if(data['contacto1'] != data['contacto2']):
                    valid = re.search(find,data['contacto2'])
                    if(re.search(find,data['contacto2'])):
                        print("numero 2 valido! verificando si se ha llamado..."+ str(valid[0]))
                        called = checkCall(valid[0],"07-05")
                        try:
                            number = ""
                            date = ""
                            try:
                                number=str(called[0][0])
                                date=str(called[0][1])
                            except:
                                exists = ""
                            if("07-05" in date):
                                print("Ya se ha llamado a este cliente")
                            elif(str(valid[0]) in number):
                                print("Llamando... "+ str(valid[0]))
                                callClient(valid[0])
                                insertCallDate(str(valid[0]),str(datetime.today()))
                                time.sleep(15)
                        except Exception as e:
                            print(str(valid)+ " Excepcion!: "+str(e))
                    else:
                        print("numero 2 no valido")
                    time.sleep(1)
