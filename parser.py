

with open('/home/pfe/pfe/logstest.txt') as f:
    lines = f.readlines()

# print(lines)
# print(lines[10])

str = '68 61 32 2D 6E 69 73 74 70 33 38 34 2C 65 63 64'
txt = "ha2-nistp384,ecd"

str = str.replace(' ', '')
# print(str)

bytes = bytearray.fromhex(str)
# print(bytes)

parsed=[]
for line in lines:
    if line.startswith("DEBUG:paramiko.transport:IN") or line.startswith("DEBUG:paramiko.transport:OUT"):
        parsed.append(line)

# print(parsed[0])
# print(parsed[0][30:77])
# print(parsed[70])
# print(parsed[70][29:76])


for k in range(len(parsed)):
    if parsed[k].startswith("DEBUG:paramiko.transport:OUT"):
        parsed[k]=parsed[k][30:77]

    
    elif parsed[k].startswith("DEBUG:paramiko.transport:IN"):
        parsed[k]=parsed[k][29:76]

for line in parsed:
    print(