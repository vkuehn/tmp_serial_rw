import asyncio
import serial
import serial.tools.list_ports


class SerialHandler:
    def __init__(self,baud=115200, debug=True, device='/dev/ttyUSB0'):
        self.data = ''
        self.debug = debug
        self.name = 'SerialHandler'
        self.ser = serial.Serial(device, baudrate=baud)
        self.ser.flushInput()

    def read(self):
        data = self.ser.readline()
        data = data.decode()
        data = str(data.strip())
        self.data = data

    async def read_async(self):
        self.read()

    def write(self, data):
        data = str(data) + '\r'
        self.ser.write(data.encode())
