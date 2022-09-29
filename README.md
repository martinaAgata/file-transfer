ClientThread

- Thread
- ClientAddress
- Sender
- UDPSocket

+ __init__(UDPSocket)

+ updateClientAddress(client_address)
+ abort()




Mensajes que le pueden llegar a un thread

Thread Main

- Nuevo cliente:
	- Si hay thread disponible.
		- Pasar al ClientThread la direccion y el mensaje
		- ClientThread debe "reiniciarse"
	- Si no:
		- Si hay espacio en la cola de espera:
			- Encolar
		- Si no:
			- Rechazar cliente nuevo
			
Llega un mensaje a thread main
El mensaje es delegado al cliente correspondiente

El mensaje de sobre que el cliente termino su transferencia

```
while True:
	try:
		msg = skt.recv()
		client.send(msg)
	except e:
		pass
	finally:
		if there_is_free_thread and cola.not_empty():
			client_free.update(cola.desencolar())	
```





