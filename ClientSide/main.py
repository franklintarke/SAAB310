from network import LoRa
import socket
import time
import utime
import ubinascii
import pycom
import machine
try:
    import urequests as requests
except ImportError:
    import requests
from loramesh import Loramesh

pycom.wifi_on_boot(True)
pycom.heartbeat(False)

lora = LoRa(mode=LoRa.LORA, region=LoRa.US915, bandwidth=LoRa.BW_125KHZ, sf=7)
MAC = str(ubinascii.hexlify(lora.mac()))[2:-1]
print("LoRa MAC: %s"%MAC)


mesh = Loramesh(lora)

DevIP = mesh.ipaddr()[-2]
print(DevIP)

def printsomething():
    print('hi')


# create UDP socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
myport = 1234
s.bind(myport)



def MakeGETRequest():

    try:
        s.sendto('makeGETrequest', ('ff03::1', myport))
        print('Sent GET request')
    except Exception:
        pass
        print('failedtosend')
    time.sleep(5 + machine.rng()%20)


# handler responisble for receiving packets on UDP Pymesh socket
def receive_pack():
    # listen for incomming packets
    while True:
        rcv_data, rcv_addr = s.recvfrom(128)
        if len(rcv_data) == 0:
            break
        rcv_ip = rcv_addr[0]
        rcv_port = rcv_addr[1]
        print('Incomming %d bytes from %s (port %d)'%(len(rcv_data), rcv_ip, rcv_port))
        print(rcv_data)
        # could send some ACK pack:
        if rcv_data.startswith("Hello"):
            try:
                s.sendto('ACK ' + MAC + ' ' + str(rcv_data)[2:-1], (rcv_ip, rcv_port))
            except Exception:
                pass
        if rcv_data.startswith("makeGETrequest"):
            try:
                r = getRequest()
                print(r.text)
                s.sendto('ACK ' + MAC + ' ' + str(rcv_data)[2:-1], (rcv_ip, rcv_port))
                print('Sent message ')
                r.close()
            except Exception:
                pass
        mesh.blink(7, .3)
