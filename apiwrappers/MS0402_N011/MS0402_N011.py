from telnetlib import Telnet
import time


class MS0402N011_Device:
    def __init__(
        self, ip, port=23, user="admin", password="admin", debug=False, verbose=False
    ):
        self.ip = ip
        self.port = port
        self.user = user
        self.password = password
        self.debug = debug
        self.verbose = verbose
        self.tn = None

    def connect(self):
        attempt = 0
        while attempt < 2:
            try:
                self.tn = Telnet(self.ip, self.port, timeout=5)
                if self.debug:
                    self.tn.set_debuglevel(1)  # Enable debugging output

                # Handle login
                self.tn.read_very_eager()
                self.tn.read_until(b"Login: ", timeout=1)
                self.tn.write(self.user.encode("ascii") + b"\r\n")
                self.tn.read_until(b"Password:", timeout=1)
                # print("Received the password prompt")
                self.tn.write(self.password.encode("ascii") + b"\r\n")
                self.tn.write(self.password.encode("ascii") + b"\r\n")

                # Check for login errors and welcome message
                start_time = time.time()
                while True:
                    response = self.tn.read_until(
                        b"Welcome to use MS42-Switcher control system", timeout=2
                    )

                    if b"Username or password error" in response:
                        print("Username or password error.")
                        self.close()
                        return "Username or password error."

                    if b"Welcome! " in response:
                        # print("Connected successfully.")
                        # Flush the buffer to remove any remaining welcome message data
                        time.sleep(
                            0.5
                        )  # Small delay to allow any remaining data to arrive
                        self.tn.read_eager()  # Flush the buffer
                        return "Connected successfully."

                    if time.time() - start_time > 10:  # Timeout after 10 seconds
                        break

                print("Failed to receive welcome message.")
                self.close()
                return "Failed to receive welcome message."

            except Exception as e:
                attempt += 1
                print(f"Attempt {attempt} failed to connect: {e}")
                self.tn = None
                time.sleep(1)  # Small delay before retrying

        return "Unable to connect after 2 attempts."

    def send_command(self, command, end_marker=b"\r\n"):
        if not self.tn:
            connection_status = self.connect()
            if connection_status != "Connected successfully.":
                print(connection_status)
                return connection_status

        try:
            # Flush the telnet buffer before sending the command
            self.tn.read_very_eager()  # This will clear any pending data in the buffer
            self.tn.write(command.encode("ascii") + b"\n")
            time.sleep(0.10)  # Small delay to allow the command to be processed

            response = b""
            while True:
                part = self.tn.read_very_eager()
                response += part
                time.sleep(0.1)
                if not part:
                    break

            response = response.decode("ascii").strip()
            # Remove the command from the response
            if response.startswith(command):
                response = response[len(command) :].strip()
            if self.verbose:
                print(f"Sent: {command}\nReceived: \n{response}\n")
            return response
        except Exception as e:
            print(f"Failed to send command: {e}")
            self.close()
            return None

    def close(self):
        if self.tn:
            self.tn.close()
            self.tn = None
            print("Connection closed.")

    def get_api_commands(self):
        command = "help"
        response = self.send_command(command)
        response = response.replace("Welcome to use MS42-Switcher system", "").strip()
        return response

    def get_firmware_version(self, prm="main"):
        """prm = {main, arm, usb_c_video, hdmi, usb_c_cc, hdbt_3.0, cpld, all}"""
        return self.send_command(f"get ver {prm}")

    def system_factory_reset(self):
        return self.send_command("reset")

    def system_reboot(self):
        return self.send_command("reboot")

    def set_telnet_login(self, old_user, new_user, old_password, new_password):
        return self.send_command(
            f"set tel_usnm {old_user} {new_user} tel_pwd {old_password} {new_password}"
        )

    def set_input(self, input, output):
        """Sets input to output

        Args:
            input: {IN1, IN2, IN3, IN4}
            output: {OUT1, OUT2}"""
        command = f"SET SW {output} {input}"
        return self.send_command(command)

    def get_input(self, output):
        """Gets input to output

        Args:
            output: {OUT1, OUT2}"""
        command = f"GET SW {output}"
        return self.send_command(command)

    def set_autoswitch(self, on_off):
        """Set to open the video and USB automatic switching mode

        Args:
            on_off: {on, off}"""
        command = f"SET AUTOSW_FN {on_off}"
        return self.send_command(command)

    def get_autoswitch(self):
        return self.send_command("GET AUTOSW_FN")

    def set_autoswitch_port(self, output, on_off):
        """Sets the status of the automatic switching function status of hdmi out ports

        Args:
            output: {OUT1, OUT2}
            on_off: {on, off}"""
        command = f"SET AUTOSW_PORT {output} {on_off}"
        return self.send_command(command)

    def get_autoswitch_port(self, output):
        """Gets the status of the automatic switching function status of hdmi out ports

        Args:
            output: {OUT1, OUT2}"""
        command = f"GET AUTOSW_PORT {output}"
        return self.send_command(command)

    def set_usba_autoswitch(self, on_off):
        """Set the status of USBA auto-switching status.

        Args:
            on_off: {on, off}"""
        command = f"SET USBASW_FN {on_off}"
        return self.send_command(command)

    def get_usba_autoswitch(self):
        return self.send_command("GET USBASW_FN")

    def set_video_autoswitch(self, status):
        """Set the video auto switch mode

        Args:
            status: {LIFO, PRIORITY}"""
        command = f"SET AUTOSW_MD {status}"
        return self.send_command(command)

    def get_video_autoswitch(self):
        return self.send_command("GET AUTOSW_MD")

    def set_lifo(self, on_off):
        """Set if OUT2 can select the same input source with OUT1 when currently selected video device is disconnected.

        Args:
            on_off: {on, off}
            on - can select the same source
            off - cannot select the same source"""
        command = f"SET LIFO_SO {on_off}"
        return self.send_command(command)

    def get_lifo(self):
        return self.send_command("GET LIFO_SO")

    def set_cec_power(self, out, on_off):
        """Sets CEC/PWR On/Off

        Args:
            out: {OUT1, OUT2, ALL}
            on_off: {on, off}"""
        command = f"SET CEC_PWR {out} {on_off}"
        return self.send_command(command)

    def set_cec_auto(self, out, on_off):
        """Sets CEC Auto Power On/Off

        Args:
            out: {OUT1, OUT2, ALL}
            on_off: {on, off}"""
        command = f"SET AUTOCEC_FN {out} {on_off}"
        return self.send_command(command)

    def get_cec_auto(self, out):
        """Gets CEC Auto Power On/Off

        Args:
            out: {OUT1, OUT2, ALL}"""
        command = f"GET AUTOCEC_FN {out}"
        return self.send_command(command)

    def set_cec_power_delay(self, out, minutes):
        """Set CEC auto power delay
        out = {OUT1, OUT2, ALL}
        minutes = {1,2,3,...} // minutes

        Default is 2 minutes
        Max is 30 minutes"""
        command = f"SET AUTOCEC_D {out} {minutes}"
        return self.send_command(command)

    def get_cec_power_delay(self, out):
        """Get CEC auto power delay
        out = {OUT1, OUT2, ALL}"""
        command = f"GET AUTOCEC_D {out}"
        return self.send_command(command)

    def set_cec_volup(self, out):
        """Sets CEC volume increase
        out = {OUT1, OUT2, ALL}
        """
        return self.send_command(f"SET CEC_VOL_INC {out}")

    def set_cec_voldown(self, out):
        """Sets CEC volume decrease
        out = {OUT1, OUT2, ALL}
        """
        return self.send_command(f"SET CEC_VOL_DEC {out}")

    def set_cec_volmute(self, out):
        """Sets CEC volume mute
        out = {OUT1, OUT2, ALL}
        """
        return self.send_command(f"SET CEC_VOL_MUTE {out}")

    def set_cec_poweron_command(self, out, command):
        """Sets CEC power on command
        out = {OUT1, OUT2, ALL}
        command = hex value less than 16"""
        return self.send_command(f"SET CECCMD_EDIT {out} pwron {command}")

    def set_cec_poweroff_command(self, out, command):
        """Sets CEC power off command
        out = {OUT1, OUT2, ALL}
        command = hex value less than 16"""
        return self.send_command(f"SET CECCMD_EDIT {out} pwroff {command}")

    def get_cec_poweron_command(self, out):
        """Gets CEC power on command
        out = {OUT1, OUT2, ALL}"""
        return self.send_command(f"GET CECCMD_EDIT {out} pwron")

    def get_cec_poweroff_command(self, out):
        """Gets CEC power off command
        out = {OUT1, OUT2, ALL}"""
        return self.send_command(f"GET CECCMD_EDIT {out} pwroff")

    def set_cec_send(self, out, command):
        """Sends CEC command
        out = {OUT1, OUT2, ALL}
        command = hex value less than 16"""
        return self.send_command(f"SET CEC_CMD {out} {command}")

    def set_rs232_baud(self, baud):
        """Sets RS232 baud rate
        baud = {9600, 19200, 38400, 57600, 115200}"""
        command = f"SET UART_B UART1 {baud}"
        return self.send_command(command)

    def get_rs232_baud(self):
        return self.send_command("GET UART_B UART1")

    def set_rs232_autopower(self, on_off):
        """Sets RS232 Auto Power On/Off
        on_off = {on, off}"""
        command = f"SET UARTPWR_FN UART1 {on_off}"
        return self.send_command(command)

    def get_rs232_autopower(self):
        return self.send_command("GET UARTPWR_FN UART1")

    def set_rs232_autopower_delay(self, minutes):
        """Set RS232 auto power delay
        minutes = {1,2,3,...} // minutes

        Default is 2 minutes
        Max is 30 minutes"""
        command = f"SET UARTPWR_D UART1 {minutes}"
        return self.send_command(command)

    def get_rs232_autopower_delay(self):
        return self.send_command("GET UARTPWR_D UART1")

    def set_rs232_command(self, task, type, command):
        """Sets RS232 power on command

        task = {poweron, poweroff, volumemute, volumeunmute, volumeup, volumedown}
        type = {hex, string}
        command = hex value less than 48 or string"""
        return self.send_command(f"SET UART_CMD UART1 {task} {type} {command}")

    def get_rs232_command(self):
        """Get's all RS232 commands"""
        return self.send_command("GET UART_CMD UART1")

    def set_rs232_command_send(self, task):
        """Sends RS232 command
        task = {poweron, poweroff, volumemute, volumeunmute, volumeup, volumedown}"""
        return self.send_command(f"SET UART_CMD_S UART1 {task}")

    def set_rs232_send(self, type, command):
        """Sends RS232 command
        type = {hex, string}
        command = hex value less than 36 or string"""
        return self.send_command(f"SET UART_S UART1 {type} {command}")

    def set_ip_mode(self, mode):
        """
        Set the IP mode of the device.
        static
        dhcp
        """
        return self.send_command(f"SET IP MODE {mode}")

    def set_ip_address(self, ip, subnet, gateway):
        return self.send_command(f"SET IPADDR {ip} {subnet} {gateway}")

    def get_ip_address(self):
        return self.send_command("GET IPADDR")

    def set_NIC_status(self, on_off):
        """Set the Network Interface Card status
        status = {on, off}"""
        return self.send_command(f"SET NIC_STATUS {on_off}")

    def get_NIC_status(self):
        return self.send_command("GET NIC_STATUS")

    def set_vlan_enable(self, on_off):
        """Set the VLAN status
        status = {on, off}"""
        return self.send_command(f"SET VLAN_ENABLE {on_off}")

    def get_vlan_enable(self):
        return self.send_command("GET VLAN_ENABLE")

    def get_vidin_status(self, input="ALL"):
        """Get the status of the video input
        input = {IN1, IN2, IN3, IN4, ALL}"""
        return self.send_command(f"GET VIDIN_SIG {input}")

    def set_vidin_HDCP(self, input, on_off):
        """Set the HDCP status
        input = {IN1, IN2, IN3, IN4, ALL}
        on_off = {on, off}"""
        return self.send_command(f"SET VIDIN_HDCP_FN {input} {on_off}")

    def get_vidin_HDCP(self, input="ALL"):
        """Get the HDCP status
        input = {IN1, IN2, IN3, IN4, ALL}"""
        return self.send_command(f"GET VIDIN_HDCP {input}")

    def set_scaler_output(self, output, on_off):
        """Set the scaler output
        output = {OUT1, OUT2, OUT3, OUT4, ALL}
        on_off = {on, off, force}"""
        return self.send_command(f"SET SCALER {output} {on_off}")

    def get_scaler_output(self, output="ALL"):
        """Get the scaler output
        output = {OUT1, OUT2, OUT3, OUT4, ALL}"""
        return self.send_command(f"GET SCALER {output}")

    def get_vidout_HDCP(self, output="ALL"):
        """Get the HDCP status
        output = {OUT1, OUT2, OUT3, OUT4, ALL}"""
        return self.send_command(f"GET HDCP {output}")

    def set_web_user_pass(self, old_user, new_user, old_password, new_password):
        """Set the web user and password
        old_user = old username
        new_user = new username
        old_password = old password
        new_password = new password"""
        return self.send_command(
            f"SET WEB_USNM {old_user} {new_user} WEB_PWD {old_password} {new_password}"
        )

    def set_usb_work_mode(self, mode):
        """Set the USB work mode
        mode = {FOLLOW1, FOLLOW2, INDEPENDENT}"""
        return self.send_command(f"SET USB_M {mode}")

    def get_usb_work_mode(self):
        """Get the USB work mode"""
        return self.send_command("GET USB_M")

    def set_usb_switch(self, input):
        """Set the USB switch from one input source to all output sink"""
        return self.send_command(f"SET USBSW {input}")

    def get_usb_switch(self):
        """Get the USB switch from one input source to all output sink"""
        return self.send_command("GET USBSW")

    def set_usb_NIC(self, input, on_off):
        """Set the USB NIC status
        input = {IN1, IN2, IN3, IN4, ALL}
        on_off = {on, off}"""
        return self.send_command(f"SET USBNIC {input} {on_off}")

    def get_usb_NIC(self, input):
        """Get the USB NIC status
        input = {IN1, IN2, IN3, IN4, ALL}"""
        return self.send_command(f"GET USBNIC {input}")

    def set_video_port_priority(self, output, input, priority):
        """Set the video port priority
        output = {OUT1, OUT2, OUT3, OUT4, ALL}
        input = {IN1, IN2, IN3, IN4, ALL}
        priority = {
            0 = This port is ignored
            1 = Level 1 (High Priority)
            2 = Level 2
            3 = Level 3
            4 = Level 4 (Lowest Priority)}"""
        return self.send_command(f"SET VIDEO_P {output} {input} {priority}")

    def get_video_port_priority(self, input="ALL", output="ALL"):
        """Get the video port priority
        input = {IN1, IN2, IN3, IN4, ALL}
        output = {OUT1, OUT2, OUT3, OUT4, ALL}"""
        return self.send_command(f"GET VIDEO_P {output} {input}")

    def set_usb_port_priority(self, input, priority):
        """Set the USB port priority
        input = {IN1, IN2, IN3, IN4, ALL}
        priority = {
            0 = This port is ignored
            1 = Level 1 (High Priority)
            2 = Level 2
            3 = Level 3
            4 = Level 4 (Lowest Priority)}"""
        return self.send_command(f"SET USB_P {input} {priority}")

    def get_usb_port_priority(self, input="ALL"):
        """Get the USB port priority
        input = {IN1, IN2, IN3, IN4, ALL}"""
        return self.send_command(f"GET USB_P {input}")

    def set_audio_mute(self, output, on_off):
        """Set the audio mute status
        output = {OUT1, OUT2, DeEmbed, ALL}
        on_off = {on, off}"""
        return self.send_command(f"SET AUD_MUTE {output} {on_off}")

    def get_audio_mute(self, output="ALL"):
        """Get the audio mute status
        output = {OUT1, OUT2, DeEmbed, ALL}"""
        return self.send_command(f"GET AUD_MUTE {output}")

    def set_audio_switch(self, output):
        """Set the audio switch
        output = {OUT1, OUT2}"""
        return self.send_command(f"SET AUDSW {output}")

    def get_audio_switch(self):
        """Get the audio switch"""
        return self.send_command("GET AUDSW")

    def set_edid_mode(self, input, mode):
        """Set the EDID mode
            input = {IN1, IN2, IN3, IN4, ALL}
            mode = {
                mode1: Fixed 4K@60Hz 2.0ch (Default).
                mode2: Copy from the OUT 1.
                mode3: Copy from the OUT 2.
                mode4: Fixed 4K@60Hz 7.1ch.
                mode5: Fixed 4K@30Hz 2.0ch.
                mode6: Fixed 4K@30Hz 7.1ch.
                mode7: 1080P@60 2.0ch
                mode8: 1080P@60 5.1ch
                mode9: 1080P@60 7.1ch
                mode10: Custom EDID 1
                mode11: Custom EDID 2
        }"""
        return self.send_command(f"SET EDID_M {input} {mode}")

    def get_edid_mode(self, input="ALL"):
        """Get the EDID mode
        input = {IN1, IN2, IN3, IN4, ALL}"""
        return self.send_command(f"GET EDID {input}")

    def get_edid_output(self, output):
        """Get the EDID
        output = {OUT1, OUT2}"""
        return self.send_command(f"GET EDID_R {output}")

    def set_usbc_sst_mode(self, on_off):
        """Set the SST mode
        on_off = {on, off}"""
        return self.send_command(f"SET USBC3_SST {on_off}")

    def get_usbc_sst_mode(self):
        """Get the SST mode"""
        return self.send_command("GET USBC3_SST")

    def set_usbc_dp_mode(self, mode):
        """Set the DP mode
        mode = {SST, MST}"""
        return self.send_command(f"SET USBC4_DM {mode}")

    def get_usbc_dp_mode(self):
        """Get the DP mode"""
        return self.send_command("GET USBC4_DM")

    def set_usbc_strategy(self, mode):
        """Set the USB strategy
        mode = {MODE1, MODE2}
        mode1: 1 USBC + 2 HDMI
        mode2: 2 USBC + 1 HDMI"""
        return self.send_command(f"SET USBC4_STRA {mode}")

    def get_usbc_strategy(self):
        """Get the USB strategy"""
        return self.send_command("GET USBC4_STRA")

    def set_debug_mode(self, on_off):
        """Set the debug mode
        on_off = {on, off}"""
        return self.send_command(f"SET LOGDBG {on_off}")

    def get_debug_mode(self):
        """Get the debug mode"""
        return self.send_command("GET LOGDBG")


def print_all_device_info(device):
    """Prints all available device information using get commands

    Args:
        device: MS0402N011_Device instance
    """
    print("\n=== Device Information ===")
    print("\nFirmware Versions:")
    print("Main:", device.get_firmware_version("main"))
    print("ARM:", device.get_firmware_version("arm"))
    print("USB-C Video:", device.get_firmware_version("usb_c_video"))
    print("HDMI:", device.get_firmware_version("hdmi"))
    print("USB-C CC:", device.get_firmware_version("usb_c_cc"))
    print("HDBT 3.0:", device.get_firmware_version("hdbt_3.0"))
    print("CPLD:", device.get_firmware_version("cpld"))

    print("\nNetwork Settings:")
    print("IP Mode:", device.get_ip_mode())
    print("IP Address Info:", device.get_ip_address())
    print("NIC Status:", device.get_NIC_status())
    print("VLAN Enable:", device.get_vlan_enable())

    print("\nVideo Settings:")
    print("Video Input Status:", device.get_vidin_status())
    print("Video Input HDCP:", device.get_vidin_HDCP())
    print("Video Output HDCP:", device.get_vidout_HDCP())
    print("Scaler Output:", device.get_scaler_output())

    print("\nSwitch Settings:")
    print("Input OUT1:", device.get_input("OUT1"))
    print("Input OUT2:", device.get_input("OUT2"))

    print("\nAutoswitch Settings:")
    print("Autoswitch:", device.get_autoswitch())
    print("Autoswitch Port OUT1:", device.get_autoswitch_port("OUT1"))
    print("Autoswitch Port OUT2:", device.get_autoswitch_port("OUT2"))
    print("USBA Autoswitch:", device.get_usba_autoswitch())
    print("Video Autoswitch Mode:", device.get_video_autoswitch())
    print("LIFO Setting:", device.get_lifo())

    print("\nCEC Settings:")
    print("CEC Auto OUT1:", device.get_cec_auto("OUT1"))
    print("CEC Auto OUT2:", device.get_cec_auto("OUT2"))
    print("CEC Power Delay OUT1:", device.get_cec_power_delay("OUT1"))
    print("CEC Power Delay OUT2:", device.get_cec_power_delay("OUT2"))
    print("CEC Power On Command OUT1:", device.get_cec_poweron_command("OUT1"))
    print("CEC Power On Command OUT2:", device.get_cec_poweron_command("OUT2"))
    print("CEC Power Off Command OUT1:", device.get_cec_poweroff_command("OUT1"))
    print("CEC Power Off Command OUT2:", device.get_cec_poweroff_command("OUT2"))

    print("\nRS232 Settings:")
    print("RS232 Baud Rate:", device.get_rs232_baud())
    print("RS232 Auto Power:", device.get_rs232_autopower())
    print("RS232 Auto Power Delay:", device.get_rs232_autopower_delay())
    print("RS232 Commands:", device.get_rs232_command())

    print("\nUSB Settings:")
    print("USB Work Mode:", device.get_usb_work_mode())
    print("USB Switch:", device.get_usb_switch())
    print("USB NIC Status:", device.get_usb_NIC("ALL"))
    print("USB Port Priority:", device.get_usb_port_priority())

    print("\nAudio Settings:")
    print("Audio Mute Status:", device.get_audio_mute())
    print("Audio Switch:", device.get_audio_switch())

    print("\nEDID Settings:")
    print("EDID Mode:", device.get_edid_mode())
    print("EDID Output 1:", device.get_edid_output("OUT1"))
    print("EDID Output 2:", device.get_edid_output("OUT2"))


# Example usage:
if __name__ == "__main__":
    device = MS0402N011_Device(
        ip="10.0.50.9", user="admin", password="admin", debug=False, verbose=False
    )
    print_all_device_info(device)
