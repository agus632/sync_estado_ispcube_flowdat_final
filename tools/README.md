Comando en curl para enviar activacion de cliente por SOAP a Flowdat

En los archivos XML se debe copeltar la IP del servidor al igual que en las lineas mas abajo ademas de usuario y contraseña

'''bash
curl -u usuario:contraseña -H "Content-Type: text/xml;charset=UTF-8" -H "SOAPAction: activeCmcliente" -d @active_client.xml http://XXX.XXX.XXX.XXX/api/v_2_0_3/cmclienteSoap
'''

Comando en curl para enviar suspencion de cliente por SOAP a Flowdat


'''bash
curl -u usuario:contraseña -H "Content-Type: text/xml;charset=UTF-8" -H "SOAPAction: suspendedCmcliente" -d @suspend_client.xml http://XXX.XXX.XXX.XXX/api/v_2_0_3/cmclienteSoap
'''
