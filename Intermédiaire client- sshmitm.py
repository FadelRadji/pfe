import socket
import time
import paramiko
from paramiko.ssh_exception import SSHException
from threading import Thread
import threading
import logging
from queue import Queue




PROXY_PORT=2221
SSH_SERVER_PORT=22
SSH_SERVER_PORT_DROP_BEAR=2223
host_key = paramiko.RSAKey(filename='id_rsa')


#logging.basicConfig()
#logging.getLogger("paramiko").setLevel(logging.DEBUG)




#Here is the thread that will handle incoming message from the client
#and send them to the vulnerable SSH server
class ClientThread(Thread):
    def __init__(self,port):
        super(ClientThread, self).__init__()
        self.server1 = None # ssh servers transports not known yet but we need them to send the messages
        self.server2 = None
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

        
    def run(self):
        while True:
            try:
                #We are reading the message from the client
                ptype, message = self.t.packetizer.read_message_after_kex()
            
                #We are sending the message to the server
                #print(message)
                self.server1._send_message(message)
                self.server2._send_message(message)

            except EOFError:
                print("Client : EOF")
                exit(0)
                

              
#Here is the part of the proxy that will handle incoming message from the vulnerable SSH server
#and send them to the client
#mode 0 is for redirect outgoing trafic to the client
#mode 1 is for redirect outgoing trafic to the IDS
class ServerThread(Thread):
    def __init__(self,port,mode,queue):
        super(ServerThread, self).__init__()
        self.client = None # client socket not known yet
        self.port = port
        self.sshSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sshSocket.connect(('',self.port))
        self.mode=mode
        self.queue = queue

        #We create the transport object
        self.t = paramiko.Transport(self.sshSocket)

        #Here we perfom key negociation
        self.t.start_client()

    def run(self):
        while True:

            try:
                ptype, reception = self.t.packetizer.read_message_after_kex()
                
                if(self.mode==0):
                    self.client._send_message(reception)
                    #print("Return from OpenSSH:\n")
                    #print(reception)
                    #print('\n')
                #else:
                    #print("Return from DropBear:\n")
                    #print(reception)
                    #print('\n')
                self.queue.put(reception)
            except EOFError:
                if(self.mode==0):
                    print("Server 1 : EOF")
                elif(self.mode==1):
                    print("DropBear Server : EOF")
                exit(0)
                

class Comparateur(Thread):

    def __init__(self, queueDropBear, queue):
        super(Comparateur, self).__init__()
        self.queue = queue
        self.queueDropBear = queueDropBear
        self.packetListDropBear = []
        self.packetList = []

    def run(self):
        while True:
            message = self.queue.get()
            self.packetList.append(message)

            messageDropBear = self.queueDropBear.get()
            self.packetListDropBear.append(messageDropBear)
            self.compare(message, messageDropBear)
            time.sleep(0.1)

    def compare(self, packet, packetDropBear):
        print("Message from OpenSSH:")
        print(packet)
        print("Message from Dropbear:")
        print(packetDropBear)
        if(packetDropBear==packet):
            print("sync\n")
        else:
            print("desync...\n")

class ProxySSH(Thread):
    def __init__(self, clientPort, serverPort1, serverPort2):
        super(ProxySSH, self).__init__()
        self.clientPort = clientPort
        self.serverPort1 = serverPort1
        self.serverPort2 = serverPort2
        self.qDropBear=Queue()
        self.q=Queue()

    def run(self):
        #Here we create the 2 threads
        self.clientThread = ClientThread(self.clientPort)

        self.serverThread1 = ServerThread(self.serverPort1,0,self.q)
        self.serverThread2 = ServerThread(self.serverPort2,1,self.qDropBear)
        self.comparateurThread = Comparateur(self.qDropBear,self.q)

        #We give to the client thread the transport object of the server 
        #thread and vice versa
        self.clientThread.server1 = self.serverThread1.t
        self.clientThread.server2 = self.serverThread2.t

        self.serverThread1.client = self.clientThread.t
        self.serverThread2.client = self.clientThread.t

        self.clientThread.start()
        self.serverThread1.start()
        self.serverThread2.start()
        self.comparateurThread.start()


proxy= ProxySSH(PROXY_PORT,SSH_SERVER_PORT,SSH_SERVER_PORT_DROP_BEAR)
proxy.start()

                