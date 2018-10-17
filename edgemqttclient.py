import sys
from binascii import hexlify
import time
import socket
import pygatt
from iotmessage import *

DATA_CHARACTERISTIC = "0000ffe1-0000-1000-8000-00805f9b34fb"
DOOR_MAC = '58:7A:62:4F:AE:50'
DOOR_PORT_NUM = 1886
OUTPUT_INIT_FLAG = True


class EdgeMqttClient():
    def __init__(self, port_num):

        # TODO implement CRC CHeck

        # Create a UDP socket
        self.sock = socket.socket(socket.AF_INET,
                                  socket.SOCK_DGRAM)  # socket.SOCK_STREAM
        # Bind the socket to the port
        self.server_addr = ('', port_num)
        print('starting up on {} port {}'.format(*self.server_addr))

        self.output = b""
        self.newdata = False

    def handle_data(self, handle, value):
        global OUTPUT_INIT_FLAG
        #print("Handling Raw Data - {}".format(hexlify(value)))
        if len(value) < 2:
            return

        if OUTPUT_INIT_FLAG == True:
            for i in range(0, len(value) - 1):
                if value[i:i + 2] == START_SEQ:
                    OUTPUT_INIT_FLAG = False
                    self.output = value[i:]
                    break
        else:
            self.output = self.output + value

        if len(self.output) >= PACKET_SZ:
            OUTPUT_INIT_FLAG = True
            self.newdata = True

    def register_handler(self, characteristic):
        self.device.subscribe(characteristic, callback=self.handle_data)

    def connect(self, mac_addr):
        self.adapter = pygatt.GATTToolBackend()
        self.adapter.start()
        while (1):
            try:
                self.device = self.adapter.connect(
                    address=mac_addr, timeout=10)
                break
            except:
                continue

    def run(self):
        print("----------------connect entered--------------")
        # data, client_addr = sock.recvfrom(4096)
        while 1:
            if self.newdata:
                self.newdata = False
                if (len(self.output) < 7):
                    continue
                data_type, data = deframe_iot_packet(self.output)
                print("deframed data - %s" % hexlify(data))
                self.output = b""

                if len(data) == 0:
                    print("ERROR: parsing failed")
                    continue
                print("length of data = " + str(len(data)))
                if data_type == DS_PRINT_MSG_TYPE:
                    print(data.decode("utf-8"))
                else:
                    num_bytes_sent = self.sock.sendto(data, self.server_addr)
                    print('sent {} number of bytes to host - {}'.format(
                        num_bytes_sent, self.server_addr))

                    recv_data = self.sock.recv(
                        PACKET_SZ)  # TODO find non blocking method or use flag
                    print('received {} from host'.format(hexlify(recv_data)))
                    data_out = frame_iot_data(recv_data)
                    #TODO will break if data_out is less than 10
                    for i in range(0, 10):
                        #print('sent {} to ble device',
                        #      hexlify(data_out[10 * i:10 * (i + 1)]))
                        self.device.char_write(
                            "0000ffe1-0000-1000-8000-00805f9b34fb",
                            data_out[10 * i:10 * (i + 1)])

    def cleanup(self):
        self.adapter.stop()
        self.sock.close()
