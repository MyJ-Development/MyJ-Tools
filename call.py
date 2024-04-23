import time
from asterisk.ami import AMIClient, SimpleAction

client = AMIClient(address='170.239.188.18', port=5038)
client.login(username='admin', secret='myjnet2022')

action = SimpleAction(
    'Originate',
    Channel='SIP/siptrunk1001/945760262',  # Número de teléfono al que quieres llamar
    Context='default',
    Exten='s',
    Priority=1,
    Callerid='945760262',
    Timeout=30000,
    Async=True,
)

future = client.send_action(action)

try:
    response = future.response
    print(response)
except Exception as e:
    print("Error: ", e)

time.sleep(1)

client.logoff()
