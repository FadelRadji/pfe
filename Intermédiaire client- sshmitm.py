import socket
import time
import paramiko
from paramiko.ssh_exception import SSHException
from threading import Thread
import threading




PROXY_PORT=2222
SSH_SERVER_PORT=22
host_key = paramiko.RSAKey(filename='id_rsa')

class ClientThread(Thread):
    def __init__(self,port):
        super(ClientThread, self).__init__()
        self.server = None # ssh server socket not known yet
        self.port = port

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('',port))
        self.socket.listen()
        print('listening...')
        self.client, address = self.socket.accept()
        print('Incoming connexion from' + str(address))

        self.t = paramiko.Transport(self.client)
        self.t.set_gss_host(socket.getfqdn(""))
        self.t.add_server_key(host_key)
        start_server(self.t)


    def run(self):
        while True:
            try:
                print("run")
                message = self.t.packetizer.read_message()
                print("Received from client : ")
                print(message)
                print("______________________________________________________________\n")
            
                
                self.server._send_message(message[1])
            except EOFError:
                print("Client : EOF")
                time.sleep(1)
              

class ServerThread(Thread):
    def __init__(self,port):
        super(ServerThread, self).__init__()
        self.client = None # client socket not known yet
        self.sshSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sshSocket.connect(('',SSH_SERVER_PORT))
        self.t = paramiko.Transport(self.sshSocket)
        self.t.start_client()
   

    def run(self):
        while True:
            try:
                reception = self.t.packetizer.read_message()
                print("Received from SSH server : ")
                print(reception)
                print("______________________________________________________________\n")
        
                self.client._send_message(reception[1])
            except EOFError:
                print("Server : EOF")
                time.sleep(1)
                
            

class ProxySSH(Thread):
    def __init__(self,clientPort, serverPort):
        super(ProxySSH, self).__init__()
        self.clientPort = clientPort
        self.serverPort = serverPort

    def run(self):
        self.clientThread = ClientThread(self.clientPort)
        self.serverThread = ServerThread(self.serverPort)
        self.clientThread.server = self.serverThread.t
        self.serverThread.client = self.clientThread.t

        self.clientThread.start()
        self.serverThread.start()


#PROgrammer : trouver moyen de déchiffrer le trafic dans le proxy

proxy= ProxySSH(PROXY_PORT,SSH_SERVER_PORT)
proxy.start()

def start_server(t, event=None, server=None):
        if server is None:
            server = paramiko.ServerInterface()
        t.server_mode = True
        t.server_object = server
        t.active = True
        if event is not None:
            # async, return immediately and let the app poll for completion
            t.completion_event = event
            t.start()
            return

        # synchronous, wait for a result
        t.completion_event = event = threading.Event()
        t.start()
        while True:
            event.wait(0.1)
            if not t.active:
                e = t.get_exception()
                if e is not None:
                    raise e
                raise SSHException("Negotiation failed.")
            if event.is_set():
                print("Negociation completed")
                #t.active=False
                break
                
                