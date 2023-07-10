from datetime import datetime as dt
import time
from telegram import Bot
import asyncio
import telnetlib
import telegram

def getStatus(ip):
    user = "cisco"
    password = "myjchile.2020"
    command = "show environment temperatures"
    terminal_length = "terminal length 0"
    tn = telnetlib.Telnet(ip)
    tn.read_until(b"Username: ")
    tn.write(user.encode('ascii') + b"\n")
    if password:
        tn.read_until(b"Password: ")
        tn.write(password.encode('ascii') + b"\n")
    tn.read_until(b"#")
    tn.write(terminal_length.encode('ascii') + b"\n")
    tn.read_until(b"#")
    tn.write(command.encode('ascii') + b"\n")
    output = tn.read_until(b"#").decode('ascii')
    tn.write(b"exit\n")
    # Procesar salida aquí para obtener temperaturas
    temperatures = []
    lines = output.split("\n")
    for line in lines:
        if "host" in line:
            temperature = (line.split()[1], float(line.split()[2]))
            temperatures.append((temperature))
    return temperatures

async def run():
    
    ip_list  = {"172.16.100.10"}
    bot = telegram.Bot("5753479653:AAFpNG9ip59sgl2UVDPxDRzmNaL9DJTmO_A")
    while(True):
        print(f"Obteniendo temperaturas: {dt.now()}")
        for ip in ip_list:
            try:
                temperatures = getStatus(ip)
            except Exception as e:
                print(f"Error al obtener las temperaturas: {e}")
            for temperature in temperatures:
                if temperature[1] > 60 :
                    try:
                        async with bot:
                            message = f"Alerta de temperatura en Cisco. Interfaz: <{temperature[0]}> Temperatura actual: {temperature[1]}"
                            await bot.send_message(text=message, chat_id=-1001547382511)
                    except Exception as e:
                        print(f"Error al enviar alerta de Telegram: {e}")
            time.sleep(5)
        time.sleep(1800)

if __name__ == '__main__':
    asyncio.run(run())
