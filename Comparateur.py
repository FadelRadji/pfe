import paramiko
client=paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# com="ls"
client.connect('localhost',22, username='pfe', password='Tatata1')

# stdin, stdout, stderr = client.exec_command(com)

with open('/home/pfe/sshproxy/sshin.txt') as f:
    lines = f.readlines()

for com in lines:
    
    stdin, stdout, stderr = client.exec_command(com)
    stdout=stdout.readlines()
    for line in stdout:
        print(line)
    

print ("ssh succuessful. Closing connection")

client.close()
print ("Connection closed")

# print (stdout)
# print (com)
# for line in stdout:
    # output=output+line
# if output!="":
    # print (output)
# else:
    # print ("There was no output for this command")