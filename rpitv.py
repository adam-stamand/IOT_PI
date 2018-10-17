import cec

RPI_HDMI = bytes([0x30, 0x00])
CHROMECAST_HDMI = bytes([0x40, 0x00])


class RpiTV():
    def __init__(self, hdmi_source):
        cec.init()
        self.tv = cec.Device(cec.CECDEVICE_TV)
        self.select_source(hdmi_source)

    def turn_on(self):
        self.tv.power_on()

    def turn_off(self):
        self.tv.standby()

    def select_source(self, hdmi_source):
        destination = cec.CECDEVICE_BROADCAST
        opcode = cec.CEC_OPCODE_ACTIVE_SOURCE
        cec.transmit(destination, opcode, hdmi_source)
