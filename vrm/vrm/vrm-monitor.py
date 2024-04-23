import time
from asterisk.ami import AMIClient, SimpleAction
import requests
import telegram
import asyncio
import time
import json

def makeCall(number_list):
    #get today day name in spanish
    today = time.strftime("%A")
    if today == "Monday":
        today = "lunes"
    elif today == "Tuesday":
        today = "martes"
    if today == "Wednesday":
        today = "miercoles"
    elif today == "Thursday":
        today = "jueves"
    elif today == "Friday":
        today = "viernes"
    elif today == "Saturday":
        today = "sabado"
    elif today == "Sunday":
        today = "domingo"
    print("today: ", today)
    client = AMIClient(address='170.239.188.18', port=5038)
    client.login(username='admin', secret='nocmyj2023')
    print(number_list[today])
    for number in number_list[today]:
        print("calling: ", number)
        action = SimpleAction(
            'Originate',
            Channel=f'SIP/siptrunk1000/{number}',  # Número de teléfono al que quieres llamar
            Context='context-critical-call',
            Exten='s',
            Priority=1,
            Callerid='999',
            Timeout=30000,
            Async=True
        )
        future = client.send_action(action)
        try:
            response = future.response
            print(response)
        except Exception as e:
            print("Error: ", e)
        time.sleep(20)
        #client.logoff()
    
async def monitor():
    #read file monitor-config.json, that has this structure:{
    #"number_list":["945760262","95760262"]
    bot = telegram.Bot("5753479653:AAFpNG9ip59sgl2UVDPxDRzmNaL9DJTmO_A") #myj
    #bot = telegram.Bot("5850630526:AAG-EBitssm7s-izdwuWZeYLN_MyPcxaP2E") #test
    with open("monitor-config.json", "r") as file:
        content = file.read()
        numbers_data = json.loads(content)
    alert_counter = -1
    while True:
        try:
            url_login = 'https://vrmapi.victronenergy.com/v2/auth/login'
            json_data = {"username": "k.salazarhenriquez@gmail.com","password": "cuajito123@"}
            url_alarm = "https://vrmapi.victronenergy.com/v2/installations/303615/alarms"
            response = requests.post(url_login,json=json_data)
            token = response.json()['token']
            idUser = response.json()['idUser']
            response = requests.get(url_alarm,headers={'x-authorization': f"Bearer {token}"})
            data = response.json()["alarms"]
            alert_list = []
            for i in data:
                if(i["meta_info"]["alarm_active"] == True):
                    alert_list.append(i)
            if(len(alert_list) > 0):
                for i in alert_list:
                    print(i["meta_info"]["name"]+" : "+i["meta_info"]["dataAttribute"]+" : "+i["meta_info"]["status"])
                    await bot.send_message(text=f'Alerta en Inversor {i["meta_info"]["name"]} : {i["meta_info"]["dataAttribute"]} : {i["meta_info"]["status"]}', chat_id=-1001547382511)
                    time.sleep(3)
                if(alert_counter > 4 or alert_counter == -1):
                            print("makecall:"+str(alert_counter))  
                            makeCall(numbers_data)
                            alert_counter = 0
                alert_counter += 1
            else:
                #print("no hay alertas")
                alert_counter = -1

            time.sleep(60)
        except Exception as e:
            error = str(e)
            print(error)
            await bot.send_message(text=f'excepcion en monitoreo vrm: {error}', chat_id=1319124913)
            time.sleep(10)


if __name__ == '__main__':
    asyncio.run(monitor())
