import json

strDevNetId = "10"
strValveNum = "1"

iDevNetId = int(strDevNetId, base=16)
iValveNum = int(strValveNum)

send_buff = [0x7E, 0x08, iDevNetId, 0, iValveNum, 0x20, 0x20, 0x20, 0x5A]

values = bytearray(send_buff)

values[3] = bytes("S", "ascii")[0]

print("Sent packet: ", end =" ")
for value in values:
    print("0x{:02x}".format(value), end =" ")
print("")

with open('../config-vinnitsa.json') as json_file:
    data = json.load(json_file)

    for key, value in data.items() :
        print (key, value)

    for dev in data['irrcon0A515']:
        print("Device Net ID: {}".format(dev))

    print("User ID: {}".format(data['user_id']))

