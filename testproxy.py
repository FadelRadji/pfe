import paramiko
import logging
import socket
import time
logging.basicConfig(filename="/home/pfe/pfe/authrequest8.log")
logging.getLogger("paramiko").setLevel(logging.DEBUG)

hostname = "127.0.0.1"
port = 22
user = "pfe"
passwd = "Tatata1"

strerr = "00 00 00 1C 0A 06 00 00 00 0C 73 73 68 2D 75 73" #message qui doit etre refusé
str1 = "05 00 00 00 0C 73 73 68 2D 75 73 65 72 61 75 74" #message de demande d'authentification
str2 = "68"


sock = socket.socket()
try:
    sock.connect((str(hostname), int(port)))
    transport = paramiko.transport.Transport(sock)
    transport.set_hexdump(True)
    transport.start_client()
    time.sleep(1)
    transport.active=False
    time.sleep(1)
    print(transport.is_active())
    time.sleep(1)
    bytes1 = bytearray.fromhex(str1)
    bytes2 = bytearray.fromhex(str2)
    message = paramiko.message.Message()
    message.add_bytes(bytes1)
    message.add_bytes(bytes2)
    transport._send_message(message)
    
    time.sleep(1)
    messageerr = paramiko.message.Message()
    byteserr = bytearray.fromhex(strerr)
    messageerr.add_bytes(byteserr)
    transport._send_message(messageerr)


    time.sleep(1)
    transport.packetizer.read_message()
    time.sleep(1)
    
    
    
except Exception as err:
    pass
    