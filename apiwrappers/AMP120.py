"""APIWrapper for the AMP100 API"""

import time
import select
from telnetlib import Telnet


class AMP120_Device:
    def __init__(self, ip, port=24, output="out2", source="dante", debug=False):
        self.ip = ip
        self.port = port
        self.output = output
        self.source = source
        self.volume = -12  # Initial volume level, adjust as needed
        self.min_volume = -40
        self.max_volume = 0
        self.volume_step = 3  # Adjust step size as needed
        self.tn = None
        self.debug = debug

    def connect(self):
        if self.tn is None:
            self.tn = Telnet()
            if self.debug:
                self.tn.set_debuglevel(1)  # Enable debug output

        try:
            self.tn.open(self.ip, self.port, timeout=1)  # Increased timeout
            self.tn.read_until(b"Password:")
            # Directly use the password string here to avoid any issues
            password_line = "admin\r".encode("ascii")
            self.tn.write(password_line)
            self.tn.read_until(b">>")
            return True

        except Exception as e:
            print(f"Failed to connect to AMP-100 at {self.ip}. Error: {e}")
            self.tn = None
            return False

    def ensure_connection(self):
        """
        Ensures that the device is connected before sending commands.
        """
        if self.tn is None or self.tn.get_socket() is None:
            return self.connect()
        return True

    def send(self, message: str) -> str:
        """
        Sends a message to the Controller and returns the response, ensuring the device is connected.
        Includes a retry mechanism if the initial send fails due to a connection issue.
        """
        retry_attempts = 2  # Number of retry attempts
        for attempt in range(retry_attempts):
            if not self.ensure_connection():
                print(
                    f"Attempt {attempt + 1}: Unable to send command to {self.ip} device is not connected."
                )
                continue

            try:
                message_bytes = f"{message}\r".encode()
                self.tn.write(message_bytes)
                stdout = self.tn.read_until(b"\r\n>").decode()
                response = stdout.strip(">")
                # if response.startswith(message):
                #     response = response[len(message) :].strip()
                return response
            except Exception as e:
                print(
                    f"Attempt {attempt + 1}: Failed to send command to {self.ip}. Error: {e}"
                )
                self.disconnect()  # Ensure disconnection before retrying
                self.tn = None  # Reset the Telnet connection

                if attempt == retry_attempts - 1:
                    return "Failed to send command after retries"

        return "Failed to establish connection"

    def send_long(self, message: str, timeout: int = 2) -> str:
        """
        Sends a message to the Controller and reads the response until a timeout.
        This method is suitable for commands that require more time to complete and
        do not have a specific end-of-message indicator.
        """
        retry_attempts = 2  # Number of retry attempts

        for attempt in range(retry_attempts):
            if not self.ensure_connection():
                print(
                    f"Attempt {attempt + 1}: Unable to send command, device is not connected."
                )
                continue

            try:
                message_bytes = f"{message}\n".encode()
                self.tn.write(message_bytes)

                start_time = time.time()
                response_data = b""

                while (time.time() - start_time) < timeout:
                    ready, _, _ = select.select([self.tn.get_socket()], [], [], 0.1)
                    if ready:
                        data = self.tn.read_very_eager()
                        response_data += data
                        if not data:
                            break  # No more data to read

                response = response_data.decode("utf-8").strip()
                return response
            except Exception as e:
                print(f"Attempt {attempt + 1}: Failed to send command. Error: {e}")
                self.disconnect()

                if attempt == retry_attempts - 1:
                    return "Failed to send command after retries"

        return "Failed to establish connection"

    def disconnect(self):
        """
        Safely closes the Telnet connection if it exists.
        """
        if self.tn is not None:
            try:
                self.tn.close()
            except Exception as e:
                print(f"Error closing Telnet connection: {e}")
            finally:
                self.tn = None

    def set_audin_mode(self, output, input):
        """Set the Audio In Mode
        output={lineout, amp, dante}
        input={linein, mic, dante}"""
        command = f"set audin_mode {output} {input}"
        return self.send(command)

    def get_audin_mode(self, output):
        """Get the Audio Out Mode
        output={lineout, amp, dante}"""
        command = f"get audin_mode {output}"
        return self.send(command)

    def set_dsp_volume(self, direction, source, level):
        """Set the DSP Volume
        direction={in, out}
        source={linein, dante, mic} if direction=in
        source={lineout, dante, amp1, amp2} if direction=out
        level={-100 ~ 10} if direction=out
        level={-20 ~ 20} if direction=in and source=dante
        level={-20 ~ 40} if direction=in and source=mic"""
        command = f"set dsp_vol {direction} {source} {level}"
        return self.send(command)

    def get_dsp_volume(self, direction, source):
        """Get the DSP Volume
        direction={in, out}
        source={linein, dante, mic} if direction=in
        source={lineout, dante, amp1, amp2} if direction=out"""
        command = f"get dsp_vol {direction} {source}"
        return self.send(command)

    def set_dsp_mute(self, direction, source, status):
        """Set the DSP Mute on/off
        direction={in, out}
        source={linein, dante, mic} if direction=in
        source={lineout, dante, amp1, amp2} if direction=out
        status={on, off}"""
        command = f"set dsp_mute {direction} {source} {status}"
        return self.send(command)

    def get_dsp_mute(self, direction, source):
        """Get the DSP Mute status
        direction={in, out}
        source={linein, dante, mic} if direction=in
        source={lineout, dante, amp1, amp2} if direction=out"""
        command = f"get dsp_mute {direction} {source}"
        return self.send(command)

    def set_amp_mode(self, status):
        """Set the AMP Mode
        status={2ch, 4ch}"""
        command = f"set amp_out_mode {status}"
        return self.send(command)

    def get_amp_mode(self):
        """Get the AMP mode status"""
        command = "get amp_out_mode"
        return self.send(command)

    def set_ipaddr(self, ipv4, subnet, gateway):
        """Set the IP Address
        ipv4=xxx.xxx.xxx.xxx
        subnet=xxx.xxx.xxx.xxx
        gateway=xxx.xxx.xxx.xxx"""
        command = f"set ipaddr {ipv4} {subnet} {gateway}"
        return self.send(command)

    def get_ipaddr(self):
        """Get the IP Address"""
        command = "get ipaddr"
        return self.send(command)

    def set_net_config(self, status):
        """Set the DHCP/Static status
        status={dhcp, static}"""
        command = f"set netcfg mode {status}"
        return self.send(command)

    def get_net_config(self):
        """Get DHCP/Static status"""
        command = "get netcfg mode"
        return self.send(command)

    def factory_reset(self):
        """Factory reset unit"""
        command = "reset"
        return self.send(command)

    def reboot(self):
        """Reboot device"""
        command = "reboot"
        return self.send(command)

    def volume_up(self):
        """
        Increases the volume by the defined step, not exceeding the max volume.
        """
        new_volume = self.volume + self.volume_step
        if new_volume > self.max_volume:
            new_volume = self.max_volume
        self.volume = new_volume
        self.set_volume()

    def volume_down(self):
        """
        Decreases the volume by the defined step, not going below the min volume.
        """
        new_volume = self.volume - self.volume_step
        if new_volume < self.min_volume:
            new_volume = self.min_volume
        self.volume = new_volume
        self.set_volume()

    def set_volume(self):
        """
        Sends the command to set the volume on the device.
        """
        self.set_dsp_volume("out", self.output, self.volume)

    def get_firmware_version(self):
        """Get the version of the device"""
        response = self.send("get ver")
        return response


if __name__ == "__main__":
    amp = AMP120_Device(ip="10.0.110.201", debug=False)
    # amp.set_dsp_mute("out", "dante", "off")
    success = 0
    for i in range(20):
        version = amp.get_firmware_version()
        if version.startswith("VER"):
            success += 1
    print(success)
