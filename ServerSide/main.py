from network import LoRa
import socket
import time
import utime
import ubinascii
import pycom
import base64
import machine
try:
    import urequests as requests
except ImportError:
    import requests
from loramesh import Loramesh

from network import WLAN
wlan = WLAN(mode=WLAN.STA)

nets = wlan.scan()
for net in nets:
    if net.ssid == 'FrankliniPhone':
        print('Network found!')
        wlan.connect(net.ssid, auth=(net.sec, '12345678'), timeout=5000)
        while not wlan.isconnected():
            machine.idle() # save power while waiting
        print('WLAN connection succeeded!')
        break

pycom.wifi_on_boot(True)
pycom.heartbeat(False)
pycom.rgbled(0x000000)

lora = LoRa(mode=LoRa.LORA, region=LoRa.US915, bandwidth=LoRa.BW_125KHZ, sf=7)
MAC = str(ubinascii.hexlify(lora.mac()))[2:-1]
print("LoRa MAC: %s"%MAC)

mesh = Loramesh(lora)

DevIP = mesh.ipaddr()[-2]
print(DevIP)
#decode from base64, split by spaces, string.split, get 2nd item


def Request(value,info):
    r = requests.get('http://172.20.10.12:3000/'+value, data = info )
    print(r.text)
    return r


# waiting until it connected to Mesh network
while True:
    mesh.led_state()
    print("%d: State %s, single %s"%(time.time(), mesh.cli('state'), mesh.cli('singleton')))
    #printsomething()
    #getRequest()
    time.sleep(2)
    if not mesh.is_connected():
        continue

    print('Neighbors found: %s'%mesh.neighbors())
    break

# create UDP socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
myport = 1234
s.bind(myport)



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
        if rcv_data.startswith("Emergency!"):
            try:
                s.sendto('ACK ' + MAC + ' ' + str(rcv_data)[2:-1], (rcv_ip, rcv_port))
                print('Write to Emergency Beacon Section')
            except Exception:
                pass
        if rcv_data.startswith("makeGETrequest"):
            try:
                parsed = base64.decode(rcv_data) .split(' ')
                value = parsed[1]
                info = parsed[2]
                r = Request(value,info)
                print(r.text)
                s.sendto(r.text, ('ff03::1', myport))
                print('Sent DatabaseGET')
                r.close()


            except Exception:
                print('db message failed')
                pass
        mesh.blink(7, .3)

pack_num = 1
msg = "Hello World Frank! MAC: " + MAC + ", pack: "
ip = mesh.ip()
mesh.mesh.rx_cb(receive_pack)

# infinite main loop
while True:
    mesh.led_state()
    print("%d: State %s, single %s, IP %s"%(time.time(), mesh.cli('state'), mesh.cli('singleton'), mesh.ip()))
    #s.sendto('test', ('ff03::1', myport))
    # check if topology changes, maybe RLOC IPv6 changed
    new_ip = mesh.ip()
    if ip != new_ip:
        print("IP changed from: %s to %s"%(ip, new_ip))
        ip = new_ip

    # update neighbors list
    neigbors = mesh.neighbors_ip()
    print("%d neighbors, IPv6 list: %s"%(len(neigbors), neigbors))
    print(str(mesh.ipaddr()))
    # send PING and UDP packets to all neighbors
    for neighbor in neigbors:
        if mesh.ping(neighbor) > 0:
            print('Ping OK from neighbor %s'%neighbor)
            mesh.blink(10, .1)
        else:
            print('Ping not received from neighbor %s'%neighbor)

        #Ping Everyone
        if mesh.ping('ff03::1') > 0:
            print('Ping received from neighbors')

        else:
            print('No Pings from neighbors')


        time.sleep(5)

        time.sleep(5 + machine.rng()%20)

    # random sleep time
    time.sleep(6)
