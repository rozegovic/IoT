import network
import machine
import dht
import time
import umqtt.simple as mqtt


def fun(topic, msg): #promjena stanja LED diode na osnovu primljene MQTT poruke
    print(msg)
    if msg == b"OFF":
        stanje.off()
    else:
        stanje.on()

def check(t): #provjera da li ima novih MQTT poruka
    mq.check_msg()

def send_temp(t):# slanje temperature i vlaznosti na openHAB
    i = 0
    
    while i < 10:
        try:
            d.measure()
            break
        except:
            i = i + 1
            

    if i == 10:
        print("DHT senszor se ne moze ocitati")
        return

    mq.publish(b"etf/iot/projekat/temp", str(d.temperature()))
    mq.publish(b"etf/iot/projekat/vlaznost", str(d.humidity()))

def reconnect(t): #spajanje na WIFI
    try:
        wlan.disconnect()
        wlan.active(False)
        wlan.active(True)
        wlan.connect('123', 'emirrime')
    except:
        return

d = dht.DHT11(machine.Pin(12))
signal = machine.Pin(2, machine.Pin.OUT) #ugradena led dioda na wemos D1 R32
signal.on() # indikacija da se skripta pokrenula
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

reconnect(0)
wifi_timer = machine.Timer(0,mode=machine.Timer.PERIODIC, period=20000, callback=reconnect) #nekad se konekcija zaglavi pa je potrebno ponovo pozvati "connect"
while not wlan.isconnected():
    pass

wifi_timer.deinit()

print("Connected!")
signal.off()
mq = mqtt.MQTTClient(b"123user", b"broker.hivemq.com")

while True:
    try:
        mq.connect()
    except:
        break
mq.set_callback(fun)
mq.subscribe(b"etf/iot/projekat/light/stanje")

stanje = machine.Pin(13, machine.Pin.OUT) # LED dioda koja se upravlja sa openHAB
stanje.on()
mq.publish(b"etf/iot/projekat/light", b"1")

signal.off()
machine.Timer(1,mode=machine.Timer.PERIODIC, period=1000, callback=check)
machine.Timer(2,mode=machine.Timer.PERIODIC, period=10000, callback=send_temp)
