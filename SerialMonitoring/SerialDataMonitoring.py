import serial
from csv import writer
from datetime import datetime

class SerialDataLogger:
    def __init__(self, port, baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.serial_port = serial.Serial(self.port, baudrate=self.baudrate, timeout=1)

    def csv_store(self, data):
        try:
            date_time = datetime.now()
            with open('SmartLight.csv', 'a', newline='') as f_object:
                writer_object = writer(f_object)
                f_object.writelines(f'{date_time}, {data}\n')
                f_object.close()
        except:
            print("CSV File unable to open")

    def run(self):
        try:
            while True:
                data = self.serial_port.readline()
                if data:
                    data_str = data.decode().strip()
                    print(data_str)
                    self.csv_store(data_str)
                else:
                    pass
        except KeyboardInterrupt:
            self.serial_port.close()
            print("Serial port closed.")

if __name__ == "__main__":
    port_no = input("Please Enter COM Port -> ")
    data_logger = SerialDataLogger('COM'+port_no, baudrate=9600)
    data_logger.run()
