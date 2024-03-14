import socket

HOST = '192.168.103.2'
PORT = 23


def send_command(socket: socket.socket, string_command: str):
    command = string_command.encode('ascii') + b'\r\n'
    s.sendall(command)


def receive_data(socket: socket.socket) -> str:
    data = socket.recv(1024)
    string_data = data.decode('ascii').replace('\r\n', '')
    return string_data


def open_socket() -> socket.socket:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    return s


def close_socket(socket: socket.socket) -> None:
    socket.close()


def log_cognex(socket: socket.socket, user: str, password: str):
    data_received = receive_data(socket)
    if data_received == 'User: ':
        send_command(socket, user)
        print('User sent')
    else:
        print('Error logging in')
    data_received = receive_data(socket)
    if data_received == 'Password: ':
        send_command(socket, password)
        print('Password sent')
    else:
        print('Error logging in')


if __name__ == '__main__':
    s = open_socket()
    data_received = receive_data(s)
    if data_received.startswith('Welcome'):
        print('Connected to Cognex')
    log_cognex(s, 'admin', '')
    data_received = receive_data(s)
    if data_received == 'User Logged In':
        print('Logged in')
    else:
        print('Error logging in')
        print(data_received)
    send_command(s, 'gva000')
    print(receive_data(s))
    close_socket(s)
