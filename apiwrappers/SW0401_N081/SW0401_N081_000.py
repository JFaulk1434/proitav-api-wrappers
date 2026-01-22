"""
Python Wrapper for SW0401-N081-000
HDMI2.1 Switcher 4x1 with ARC Extraction

"""

import serial
from time import sleep


class SW0401N081_Device:
    def __init__(self, device_name) -> None:
        """Needs to send RS232 device.
        Example : "/dev/ttyUSB0"
        Example : "COM3"
        """
        self.control = "RS232"
        self.device = device_name  # string
        self.rs232_baud = 115200
        self.rs232_data_bits = 8
        self.rs232_parity = "N"
        self.rs232_stop_bits = 1
        self.rs232_flow_control = "N"
        self.rs232_timeout = 1
        self.serial = serial.Serial(
            port=self.device,
            baudrate=self.rs232_baud,
            timeout=self.rs232_timeout,
            bytesize=self.rs232_data_bits,
            parity=self.rs232_parity,
            stopbits=self.rs232_stop_bits,
        )

    def send_command(self, command) -> str:
        """Send command, returns response"""
        command_encoded = command.encode("ascii") + b"\r\n"
        print(f"Sent: {command}")
        self.serial.write(command_encoded)
        data = self.serial.read_until(b"\r\n")

        if not data:
            print(f"No response received within {self.rs232_timeout}s")
            return f"No response received within {self.rs232_timeout}s"
        else:
            data_decoded = data.decode("ascii")
            print(f"Received: {data_decoded}")
            return data_decoded

    def switch_input_output(self, input: int, output="out"):
        """Switch input to the output"""
        command = f"SET SW in{input} {output}"
        response = self.send_command(command)
        return response

    def get_input_output(self):
        """Returns Which input is currently attached to output"""
        command = "GET MP out"
        response = self.send_command(command)
        return response

    def set_cec_power(self, on_off: str):
        """Turn CEC on or off"""
        command = f"SET CEC_PWR out {on_off}"
        response = self.send_command(command)
        return response

    def factory_reset(self):
        """Factory Reset Unit"""
        command = "RESET"
        response = self.send_command(command)
        return response

    def system_reboot(self):
        """Reboot Unit"""
        command = "REBOOT"
        response = self.send_command(command)
        return response

    def get_firmware_ver(self):
        """Get current firmware version"""
        command = "GET VER"
        response = self.send_command(command)
        return response

    def get_autoswitch(self):
        """Get Autoswitch status"""
        command = "GET AUTOSW_FN"
        response = self.send_command(command)
        return response

    def set_autoswitch(self, on_off):
        """Turn autoswitch on or off"""
        command = f"SET AUTOSW_M {on_off}"
        response = self.send_command(command)
        return response

    def help(self):
        """Prints out all functions available"""
        functions = [
            func
            for func in dir(self)
            if callable(getattr(self, func))
            and not func.startswith("__")
            and not func.startswith("_")
        ]
        num_functions = len(functions)
        print("Available functions:")
        for i in range(0, num_functions, 2):
            func_name_1 = functions[i]
            func_name_2 = functions[i + 1] if i + 1 < num_functions else ""
            print("{:<30}{:<30}".format(func_name_1, func_name_2))
        print("")


if __name__ == "__main__":
    switch = SW0401N081_Device("/dev/cu.usbserial-A9UK1ODD")
    switch.help()
    switch.get_firmware_ver()

    print("10 Min input test starting....")
    sleep(2)
    for _ in range(10):
        switch.switch_input_output(1)
        sleep(30)
        switch.switch_input_output(2)
        sleep(30)
    print("Done...")
