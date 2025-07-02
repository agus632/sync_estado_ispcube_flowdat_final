Comando en curl para enviar activacion de cliente por SOAP a Flowdat


'''bash
curl -u usuario:contraseña -H "Content-Type: text/xml;charset=UTF-8" -H "SOAPAction: activeCmcliente" -d @active_client.xml http://XXX.XXX.XXX.XXX/api/v_2_0_3/cmclienteSoap
'''

Comando en curl para enviar suspencion de cliente por SOAP a Flowdat


'''bash
curl -u usuario:contraseña -H "Content-Type: text/xml;charset=UTF-8" -H "SOAPAction: suspendedCmcliente" -d @suspend_client.xml http://XXX.XXX.XXX.XXX/api/v_2_0_3/cmclienteSoap
'''