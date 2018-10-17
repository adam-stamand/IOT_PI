import binascii

PACKET_SZ = 100
START_SEQ = b'\x01\xaa'
END_SEQ = b'\x54\xDD'
DS_MQTT_MSG_TYPE = 0
DS_PRINT_MSG_TYPE = 1


def deframe_iot_packet(data):
    #print(data)

    if data[0:2] != START_SEQ:
        print("Start SEQ failed - Expected: " +
              str(binascii.hexlify(START_SEQ)) + " Received: " +
              str(binascii.hexlify(data[0:2])))
        print("Data: " + str(binascii.hexlify(data)))
        return 0, b''
    if data[PACKET_SZ - 2:PACKET_SZ] != END_SEQ:
        print("End SEQ failed - Expected: " + str(binascii.hexlify(END_SEQ)) +
              " Received: " + str(binascii.hexlify(data[PACKET_SZ - 2:])))
        print("Data: " + str(binascii.hexlify(data)))
        return 0, b''
    #TODO implement crc
    return data[3], bytearray(data[4:data[2] + 1 + 3])


def frame_iot_data(data):
    packet = bytearray(PACKET_SZ)
    packet[0:2] = START_SEQ
    packet[PACKET_SZ - 2:] = END_SEQ
    if data[0] == 1:
        data_len = int.from_bytes(data[1:3], byteorder='big')
    else:
        data_len = data[0]
    #TODO implement crc
    packet[2] = data_len
    packet[3] = DS_MQTT_MSG_TYPE
    packet[4:data_len + 4] = data
    return packet
