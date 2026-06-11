import socket

def recv_exact(client_socket, length):
    raw = bytearray()
    while len(raw) < length:
        raw += client_socket.recv(length - len(raw))
    print("Received: {}".format(len(raw)))
    return raw

def client_program():
    host = '10.10.100.154'
    port = 9991

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    while True:
        raw = recv_exact(client_socket, 4)

        length = (raw[0] << 24) + (raw[1] << 16) + (raw[2] << 8) + raw[3]
        print("Length: {}".format(length))

        raw = recv_exact(client_socket, length)

        message = "Done!\n"

        client_socket.sendall(message.encode())

    client_socket.close()


if __name__ == '__main__':
    client_program()
