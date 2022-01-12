import socket
import time
import paramiko
from paramiko.ssh_exception import SSHException
from threading import Thread
import threading
import logging




PROXY_PORT=2222
SSH_SERVER_PORT=22
host_key = paramiko.RSAKey(filename='id_rsa')


logging.basicConfig()
logging.getLogger("paramiko").setLevel(logging.DEBUG)



#Here is the thread that will handle incoming message from the client
#and send them to the vulnerable SSH server
class ClientThread(Thread):
    def __init__(self,port):
        super(ClientThread, self).__init__()
        self.server = None # ssh server transport not known yet but we need it to send the messages
        self.port = port

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('',port))
        self.socket.listen()
        print('listening...')
        self.client, address = self.socket.accept()
        print('Incoming connexion from' + str(address))

        #We create the transport object with Paramiko
        self.t = paramiko.Transport(self.client)
        self.t.set_gss_host(socket.getfqdn(""))
        self.t.add_server_key(host_key)

        #Here, we proceed to the key negociation, the fonction is in the Paramiko's code source
        self.t.start_server()

        #Here we stop the negociaiton
        self.t.active=False
        
    def run(self):
        while True:
            try:
                print("run client")

                #We are reading the message from the client
                ptype, message = self.t.packetizer.read_message()
                
                #print("Received from client : ")
                
                #print(message.get_text)
                #print(len(message.asbytes))
                #print("______________________________________________________________\n")
            
                #We are sending the message to the server
                self.server._send_message(message)
            except EOFError:
                print("Client : EOF")
                time.sleep(1)

              
#Here is the part of the proxy that will handle incoming message from the vulnerable SSH server
#and send them to the client
class ServerThread(Thread):
    def __init__(self,port):
        super(ServerThread, self).__init__()
        self.client = None # client socket not known yet
        self.sshSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sshSocket.connect(('',SSH_SERVER_PORT))

        #We create the transport object
        self.t = paramiko.Transport(self.sshSocket)

        #Here we perfom key negociation
        self.t.start_client()

        #Here we stop the negociation
        self.t.active=False

    def run(self):
        while True:
            try:
                print("run server")
                ptype, reception = self.t.packetizer.read_message()
                
                #print("Received from SSH server : ")
                #print(reception.asbytes)
                
                #print("______________________________________________________________\n")
        
                self.client._send_message(reception)
            except EOFError:
                print("Server : EOF")
                time.sleep(1)

class ProxySSH(Thread):
    def __init__(self,clientPort, serverPort):
        super(ProxySSH, self).__init__()
        self.clientPort = clientPort
        self.serverPort = serverPort

    def run(self):
        #Here we create the 2 threads
        self.clientThread = ClientThread(self.clientPort)
        self.serverThread = ServerThread(self.serverPort)

        #We give to the client thread the transport object of the server 
        #thread and vice versa
        self.clientThread.server = self.serverThread.t
        self.serverThread.client = self.clientThread.t

        self.clientThread.start()
        self.serverThread.start()


proxy= ProxySSH(PROXY_PORT,SSH_SERVER_PORT)
proxy.start()

                