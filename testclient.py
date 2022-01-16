import paramiko
import logging
logging.basicConfig(filename="/home/pfe/pfe/lBRATATATATATATA.txt")
logging.getLogger("paramiko").setLevel(logging.DEBUG)

hostname = "127.0.0.1"
port = 22
user = "pfe"
passwd = "Tatata1"

try:
    client = paramiko.SSHClient()

    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, port=port, username=user, password=passwd)
    while True:
        try:
            cmd = input("$> ")
            if cmd == "exit": break
            stdin, stdout, stderr = client.exec_command(cmd)
            print(stdout.read().decode())
        except KeyboardInterrupt:
            break
        client.close()
except Exception as err:
    print(str(err))
    