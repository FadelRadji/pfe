import sys
import threading
import time
import logging
import socket
import paramiko
from paramiko.ssh_exception import SSHException

logging.basicConfig()
logger = logging.getLogger()

running = True
host_key = paramiko.RSAKey(filename='id_rsa')

def ssh_command_handler():
    return

def listener():
    print('listener')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', 2224))

    sock.listen(100)
    client, addr = sock.accept()

    t = paramiko.Transport(client)
    t.set_gss_host(socket.getfqdn(""))
    t.add_server_key(host_key)
    start_server(t)

    print("envoi message")
    message=t.packetizer.read_message()
    print(message)

    #t._send_message("Test")

    #while t.completion_event:
    #    print("negociation in progress")
    #    time.sleep(0.2)
    #    pass

    time.sleep(10)
    print("finish")


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
                t.active=False
                break
                
                