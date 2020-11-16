from pysnmp.hlapi import *
import time

def getOid(oid):
    t = time.time()
    iterator = bulkCmd(SnmpEngine(),
                    CommunityData('public'),
                    UdpTransportTarget(('172.16.50.100', 161)),
                    ContextData(),
                    0,20,
                    ObjectType(ObjectIdentity(oid)),
            lookupMib=False, lexicographicMode=False)

    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

    for (errorIndication, errorStatus, errorIndex, varBinds) in iterator:
        for varBind in varBinds:
            line =(' = '.join([x.prettyPrint() for x in varBind]))
            pon = -1
            slot = -1
            line = line.split("=")
            id = line[0].split(".")
            id = id[-1]
            pon = line[1].split(":")
            slot = pon[1]
            pon = pon[0].split("/")[1]
            
            print("ID: "+str(id)+" PON: "+str(pon) + " SLOT: "+str(slot))

    if errorIndication:  # SNMP engine errors
        print(errorIndication)
    else:
        if errorStatus:  # SNMP agent errors
            print('%s at %s' % (
                errorStatus.prettyPrint(),
                varBinds[int(errorIndex)-1] if errorIndex else '?'))

    print(time.time() - t, 's')

getOid("iso.3.6.1.4.1.17409.2.3.4.1.1.2")