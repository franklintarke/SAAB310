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



#eid_socket.sendto("01234567890123456789", ("1::2", 1235))
