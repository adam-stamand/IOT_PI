from rpimqttclient import *
from rpitv import *
from rpitify import *
from rpicast import *
from edgemqttclient import *
import threading
import time
from omxplayer.player import OMXPlayer
from time import sleep
import signal
import sys
import subprocess

DOOR_TOPIC = 'living_room/doorsensor1'

pi_tv = RpiTV(RPI_HDMI)
pi_player = Rpitify()
pi_tv.turn_off()

url = 'https://www.youtube.com/watch?v=eyU3bRy2x44'
proc = subprocess.Popen(
    ['youtube-dl', '-f', 'best', '-g', url], stdout=subprocess.PIPE)
realurl = proc.stdout.read()
vid_player = OMXPlayer(realurl.decode("utf-8", "strict")[:-1], pause=True)
vid_player.mute()


def door_parser(data):
    if data[0] == 1:
        print("OCCUPIED COMMAND RECVED")
        pi_tv.turn_on()
        #pi_tv.select_source(RPI_HDMI)
        vid_player.play()
        vid_player.mute()
        pi_player.connect()
        pi_player.loadPlaylist('Classy Jazz')
        pi_player.shufflePlaylist()
        pi_player.playPlaylist(0)
        pi_player.setVol(85)
        pi_player.disconnect()
        subprocess.call(['/home/pi/programs/tv_source.sh'])

    elif data[0] == 0:
        print("VACATED COMMAND RECVED")
        subprocess.call(['/home/pi/programs/tv_off.sh'])
        vid_player.mute()
        vid_player.pause()
        vid_player.set_position(0)
        #pi_tv.turn_off()
        pi_player.connect()
        pi_player.pause()
        pi_player.disconnect()
        #house vacated


def on_message(client, userdata, msg):
    if msg.topic == DOOR_TOPIC:
        door_parser(msg.payload)
        print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))


def DoorClientThread():
    door_client = EdgeMqttClient(DOOR_PORT_NUM)
    door_client.connect(DOOR_MAC)
    door_client.register_handler(DATA_CHARACTERISTIC)
    door_client.run()


def MqttClientThread():
    mqtt_client = RpiMqttClient('mqtt_master')
    mqtt_client.connect(RPI_PORT_NUM)
    mqtt_client.register_handler(on_message)
    mqtt_client.subscribe(DOOR_TOPIC)
    mqtt_client.run()


try:
    t1 = threading.Thread(target=DoorClientThread, args=())
    t2 = threading.Thread(target=MqttClientThread, args=())

    # starting thread 1
    t1.start()
    # starting thread 2
    t2.start()

    # wait until thread 1 is completely executed
    t1.join()
    # wait until thread 2 is completely executed
    t2.join()

finally:
    vid_player.quit()
    pi_player.cleanup()
    pi_tv.turn_off()
