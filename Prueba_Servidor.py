import socket
import select
import pickle
import random

# Configuración del servidor
host = 'localhost'  # Dirección IP del servidor
port = 12345  # Puerto del servidor
contador = 0  # Contador que manda color cuando llega a 2, mientras no hace nada
# Crear un socket TCP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Vincular el socket a la dirección y puerto
sock.bind((host, port))
# Poner el socket en modo de escucha
sock.listen(2)
print('Servidor escuchando en {}:{}'.format(host, port))
# Lista de conexiones de los clientes
connections = []

while len(connections) < 2:
    # Aceptar nuevas conexiones de clientes
    conn, addr = sock.accept()
    print('Cliente conectado:', addr)
    contador = contador + 1

    # Agregar la nueva conexión a la lista
    connections.append(conn)

print('Dos clientes conectados. Comenzando a transmitir mensajes.')

while True:
    # Utilizar select para verificar si hay datos disponibles para recibir en los clientes
    rlist, _, _ = select.select(connections, [], [])

    for client in rlist:
        # Recibir datos del cliente
        data = client.recv(4098)

        if not data:
            # Si no se reciben datos, se cierra la conexión con el cliente
            print('Cliente desconectado:', client.getpeername())
            client.close()
            connections.remove(client)
            break

        # Deserializar la lista recibida del cliente
        received_list = pickle.loads(data)

        # Enviar la lista recibida a los demás clientes
        for other_client in connections:
            if other_client != client and contador >= 2:
                if contador == 2:
                    print("Color de piezas")
                    # Crear código que elige de forma aleatoria el color de las piezas para los jugadores
                    palabra = random.choice(["Blancas", "Negras"])
                    palabra_opuesta = "Blancas" if palabra == "Negras" else "Negras"

                    # Enviar la palabra al cliente 1
                    palabra_serializada = pickle.dumps([palabra])
                    client.sendall(palabra_serializada)

                    # Enviar la palabra opuesta al cliente 2
                    palabra_opuesta_serializada = pickle.dumps([palabra_opuesta])
                    other_client.sendall(palabra_opuesta_serializada)

                    print("Palabra enviada al Cliente 1:", palabra)
                    print("Palabra enviada al Cliente 2:", palabra_opuesta)
                    contador = contador + 1

                else:
                    # Serializar la lista antes de enviarla
                    serialized_list = pickle.dumps(received_list)
                    other_client.sendall(serialized_list)
                    print("Se envió el mensaje", serialized_list)

# Cerrar las conexiones con los clientes
for conn in connections:
    conn.close()

# Cerrar el socket del servidor
sock.close()