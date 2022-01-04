import sys
import threading
import logging
import socket
import paramiko

logging.basicConfig()
logger = logging.getLogger()

running = True
host_key = paramiko.RSAKey(filename='id_rsa')


def ssh_command_handler(command):
    print('default : ', command)


class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        print("test2")
        if kind == 'session':
            print("test3")
            return paramiko.OPEN_SUCCEEDED

    def check_auth_publickey(self, username, key):
        return paramiko.AUTH_SUCCESSFUL

    #def get_allowed_auths(self, username):
    #    return 'publickey'

    def check_channel_exec_request(self, channel, command):
        print("test")
        global running
        # This is the command we need to parse
        if command == 'exit':
            running = False
        ssh_command_handler(command)
        self.event.set()
        return True
    
    def check_auth_password(self, username, password):
        print(username)
        print(password)
        if username == "user" and password == "password":
            return paramiko.AUTH_SUCCESSFUL
        else:
            return paramiko.AUTH_FAILED


def listener():
    print('listener')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', 2224))

    sock.listen(100)
    client, addr = sock.accept()

    t = paramiko.Transport(client)
    #t.set_gss_host(socket.getfqdn(""))
    #t.load_server_moduli()
    t.add_server_key(host_key)
    server = Server()
    t.start_server(server=server)

    # Wait 30 seconds for a command
    print("server wait")
    server.event.wait(4)
    print("server wait finished")
    session=t.open_session()
    while True:
        command= session.recv(1024).decode('utf-8')
        print(command)

    server.event.wait(30)
    t.close()
    print('end listener')


def run_server(command_handler):
    global running
    global ssh_command_handler
    ssh_command_handler = command_handler
    listener()
    #while running:
    #    try:
    #        listener()
    #    except KeyboardInterrupt:
    #        sys.exit(0)
    #    except Exception as exc:
    #        logger.error(exc)


def run_in_thread(command_handler):
    thread = threading.Thread(target=run_server, args=(command_handler,))
    thread.start()


if __name__ == '__main__':
    run_in_thread(ssh_command_handler)