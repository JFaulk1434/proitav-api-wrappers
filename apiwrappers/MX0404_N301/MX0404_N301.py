from telnetlib import Telnet
import time
import select


class MX0404N301_Device:
    """Class to interact with the MX0404-N301 device via Telnet using telnetlib3.
        It provides methods to send different commands to the device.

    - RS232 Settings
    Parameters
    Baud Rate	115200 bps
    Data bits	8 bits
    Parity	None
    Stop bits	1 bit
    Flow control	None

    - Telnet/TCP Settings
    Connect a control PC to the LAN port of the device. Before you intend to control the device through telnet API, you shall establish connection between this device and your computer. The form of the command for telnet connection is below: telnet ip (port)

    ip: The device's IP address.
    port: The device's port number, this is not required for some Telnet control tools. Default setting is 23.
    For example, if the device's IP address is 192.168.11.143, the command for telnet connection shall be the following:
    telnet 192.168.11.143

    Obtain IP address of the Device
    To obtain the device's IP address:

    Connect a control PC to the RS232 port of the device.
    Configure RS232 parameters for the PC's serial port correctly through a RS232 serial port tool, such as Serial Assist.
    Input the command GET IPADDR<CR><LF> and send. You will get a response with IP address, see following:
    Input:
    GET IPADDR<CR><LF>

    Response:
    IPADDR 172.16.18.173 MASK 255.255.255.0 GATEWAY 172.16.18.1

    Note: When all is configured properly, you can control the device through commands, which are available in the separate document.
    """

    def __init__(self, ip, port=23):
        """Initializes the Matrix class."""
        self.ip = ip
        self.port = port
        self.tn = None

    def connect(self):
        """
        Attempts to connect to the device, handling cases where the device might be offline or not responding.
        """
        if self.tn is None:
            self.tn = Telnet()  # Initialize without connecting
            # self.tn.set_debuglevel(1)
        try:
            self.tn.open(self.ip, self.port, timeout=1.0)
            self.tn.read_until(b"Welcome to Telnet!")
            self.tn.write(b"\n")
            self.tn.read_until(b">")

            return True
        except Exception as e:
            print(f"Failed to connect to {self.ip}. Error: {e}")
            self.tn = None  # Reset the connection
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
                message_bytes = f"{message}\n".encode()
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

    def set_mv_layout(self, prm):
        """Set Video output display layout as original.

        prm = {0, 1, 2, 4, 5}
        // 0: Original
        // 1: Dual-view
        // 2: Pip
        // 4: Master
        // 5: Quad
        """

        return self.send(f"SET VIDOUT_MODE {prm}")

    def get_mv_layout(self):
        """Get the video output layout"""

        return self.send("GET VIDOUT_MODE")

    def set_mv_dual_src(self, in_left, in_right):
        """Set the video source in dual layout mode

        in_left: {in1, in2, in3, in4}; left
        in_right: {in1, in2, in3, in4}; right"""

        return self.send(f"SET VIDOUT_DUAL_SRC {in_left} {in_right}")

    def get_mv_dual_src(self):
        """Get the videos ource in dual layout mode"""

        return self.send("GET VIDOUT_DUAL_SRC")

    def set_mv_pip_src(self, in_big, in_small):
        """Set the video source in PIP layout mode

        in_big: {in1, in2, in3, in4}; Big
        in_small: {in1, in2, in3, in4}; Small"""

        return self.send(f"SET VIDOUT_PIP_SRC {in_big} {in_small}")

    def get_mv_pip_src(self):
        """Get the video source in PIP layout"""

        return self.send("GET VIDOUT_PIP_SRC")

    def set_mv_quad_src(self, in_tl, in_tr, in_bl, in_br):
        """Set the video source in Quad layout mode

        in_tl: {in1, in2, in3, in4}; Top Left
        in_tr: {in1, in2, in3, in4}; Top Right
        in_bl: {in1, in2, in3, in4}; Bottom Left
        in_br: {in1, in2, in3, in4}; Bottom Right"""

        return self.send(f"SET VIDOUT_QUAD_SRC {in_tl} {in_tr} {in_bl} {in_br}")

    def get_mv_quad_src(self):
        """Get the video source in Quad Layout"""

        return self.send("GET VIDOUT_QUAD_SRC")

    def set_mv_master_src(self, in_left, in_tr, in_mr, in_br):
        """Set the video source in Master layout mode

        Parameters: {in1, in2, in3, in4}

        in_left: Input Left side
        in_tr: Input Small Top Right
        in_mr: Input Small Middle Right
        in_br: Input Small Bottom Right"""

        return self.send(f"SET VIDOUT_MASTER SRC {in_left} {in_tr} {in_mr} {in_br}")

    def get_mv_master_src(self):
        """Get the video sources in Master Layout"""

        return self.send("GET VIDOUT_MASTER_SRC")

    def set_mv_pip_smallsize(self, prm):
        """Set the pip small window size

        prm: {0, 1, 2}
        0: 1/4
        1: 1/9
        2: 1/16"""

        return self.send(f"SET VIDOUT_PIP_SIZE {prm}")

    def get_mv_pip_smallsize(self):
        """Get the pip small window size
        0: 1/4
        1: 1/9
        2: 1/16"""

        return self.send("GET VIDOUT_PIP_SIZE")

    def set_mv_pip_smalllocation(self, pos):
        """Set the pip small window location

        pos: {0, 1, 2, 3}
        0: Top Left
        1: Top Right
        2: Bottom Left
        3: Bottom Right"""

        return self.send("SET VIDOUT_PIP_POS {pos}")

    def get_mv_pip_smalllocation(self):
        """Get the pip small window location

        0: Top Left
        1: Top Right
        2: Bottom Left
        3: Bottom Right"""

        return self.send("GET VIDOUT_PIP_POS")

    def set_vidin_stretch(self, input, prm):
        """Set the input video stretch status

        input: {in1, in2, in3, in4}
        prm: {origin, full}"""

        return self.send(f"SET VIDIN_STRETCH {input} {prm}")

    def get_vidin_stretch(self, input):
        """Get the input video streatch status"""

        return self.send(f"GET VIDIN_STRETCH {input}")

    def set_audout_window(self, prm):
        """Set the audio out window

        prm: {in1, in2, in3, in4}"""

        return self.send(f"SET AUDOUT_WND {prm}")

    def get_audout_window(self):
        """Get the audio out window"""

        return self.send("GET AUDOUT_WND")

    def set_videowall(self, input, tl, tr, bl, br):
        """Set the video wall and select input source

        input: {in1, in2, in3, in4}
        prm: {out1, out2, out3, out4}
        tl: Top Left
        tr: Top Right
        bl: Bottom Left
        br: Bottom Right

        example: SET VIDWALL in1 out1 out2 out3 out4"""

        return self.send(f"SET VIDWALL {input} {tl} {tr} {bl} {br}")

    def get_videowall(self):
        """Get video wall settings and the input"""

        return self.send("GET VIDWALL")

    def set_vidmode(self, prm):
        """
        Set the video mode of the device.

        :param prm: Video mode to set, options are 'Matrix', 'VideoWall', 'MultiView'.
        :return: The command string to set the video mode.
        """
        return self.send(f"SET VIDMODE {prm}")

    def get_vidmode(self):
        """Get's the video output mode

        Command: GET VIDMODE
        Return: VIDMODE prm
        Return Parameter: Matrix, VideoWall
        Example: GET VIDMODE
        Returned: GET VIDMODE Matrix"""

        return self.send("GET VIDMODE")

    def set_vidwall_bezel(self, vw, ow, vh, oh):
        """
        Set the bezel correction values for the video wall.

        :param vw: Value for vertical width bezel correction (0-10000).
        :param ow: Value for offset width bezel correction (0-10000).
        :param vh: Value for vertical height bezel correction (0-10000).
        :param oh: Value for offset height bezel correction (0-10000).
        :return: The command string to set the video wall bezel correction.
        """
        return self.send(f"SET VIDWALLBEZEL {vw} {ow} {vh} {oh}")

    def get_vidwall_bezel(self):
        """Get the Video Wall bezel correction

        Command: GET VIDWALLBEZEL
        Return: VIDWALLBEZEL VW OW VH OH
        Parameter: 0-10000mm
        VW: Viewing Width
        OW: Outer Width
        VH: Viewing Height
        OH: Outer Height
        Example: GET VIDWALLBEZEL
        Returned: VIDWALLBEZEL 889 914 495 520"""

        return self.send("GET VIDWALLBEZEL")

    def set_vidwall_rotation(self, output, state):
        """
        Enable or disable 180° rotation for a specific output.

        :param output: The output number to set the rotation state.
        :param state: Rotation state, options are 'enable', 'disable'.
        :return: The command string to set the 180° rotation.
        """
        return self.send(f"SET VIDWALL_ROTATION {output} {state}")

    def get_vidwall_rotation(self, prm1):
        """Get the status of the 180° rotation

        Command: GET VIDWALL_ROTATION prm1
        Return: VIDWALL_ROTATION prm1 prm2
        Parameter prm1: out1, out2, out3, out4
        Parameter prm2: disable, enable
        Example: GET VIDWALL_ROTATION out2
        Returned: VIDWALL_ROTATION out2 disable"""

        return self.send(f"GET VIDWALL_ROTATION {prm1}")

    def set_switch(self, inp, out):
        """Switch one input (source) to one output (display)

        Command: SET SW in out
        Return: SW in1 out2
        Parameter in: in1, in2, in3, in4
        Parameter out: out1, out2, out3, out4
        Example: SET SW in1 out3
        Returned: SW in1 out3"""

        return self.send(f"SET SW {inp} {out}")

    def set_switch_all(self, input):
        """Switch one input (source) to all outputs (displays)

        Command: SET SW in all
        Return: SW in all
        Parameter in: in1, in2, in3, in4
        Example: SET SW in2 all
        Returned: SW in2 all"""

        return self.send(f"SET SW {input} all")

    def get_mapping_output(self, output):
        """Get the mapping status of an output

        Command: GET MP out
        Return: MP in out
        Parameter in: in1, in2, in3, in4
        Parameter out: out1, out2, out3, out4
        Example: GET MP out2
        Returned: MP in3 out2
        """

        return self.send(f"GET MP {output}")

    def get_mapping_all(self):
        """Gets the mapping status of all inputs and outputs

        Command: GET MP all

        Return: MP in out

        Parameter in: in1, in2, in3, in4

        Parameter out: out1, out2, out3, out4

        Example: GET MP all

        Returned:

        MP in1 out1
        MP in1 out2
        MP in1 out3
        MP in4 out4"""

        return self.send("GET MP ALL")

    def set_audio_mute(self, output, prm):
        """Set Audio Mute for specific Audio Output

        Command: SET AUDIO_MUTE out prm
        Return: AUDIO_MUTE out prm
        Parameter out: zone1, zone2
        Parameter prm: on, off
        Example: SET AUDIO_MUTE zone1 on
        Returned: AUDIO_MUTE zone1 on"""

        return self.send(f"SET AUDIO_MUTE {output} {prm}")

    def get_audio_mute(self, output):
        """Get Audio Mute for specific Audio Output

        Command: GET AUDIO_MUTE out
        Return: AUDIO_MUTE out prm
        Parameter out: zone1, zone2
        Parameter prm: on, off
        Example: GET AUDIO_MUTE zone1
        Returned: AUDIO_MUTE zone1 on"""

        return self.send(f"GET AUDIO_MUTE {output}")

    def set_cec_power(self, output, prm):
        """Set sink to power on or off

        Command: SET CEC_PWR out prm
        Return: CEC_PWR out prm
        Parameter out: out1, out2, out3, out4
        Parameter prm: on, off
        Example: SET CEC_PWR out1 on
        Return: CEC_PWR out1 on"""

        return self.send(f"SET CEC_PWR {output} {prm}")

    def set_cec_auto(self, output, prm):
        """Set sink auto power function on or off

        Command: SET AUTOCEC_FN out prm
        Return: AUTOCEC_FN out prm
        Parameter prm: on, off
        Parameter out: out1, out2, out3, out4
        Example: SET AUTOCEC_FN out1 on
        Return: AUTOCEC_FN out1 on"""

        return self.send(f"SET AUTOCEC_FN {output} {prm}")

    def get_cec_auto(self, output):
        """Get sink auto power function status

        Command: GET AUTOCEC_FN out
        Return: AUTOCEC_FN out prm
        Parameter out: out1, out2, out3, out4
        Parameter prm: on, off
        Example: GET AUTOCEC_FN out1
        Return: AUTOCEC_FN out1 on
        """

        return self.send(f"GET AUTOCEC_FN {output}")

    def set_cec_delay(self, output, prm):
        """Setup to automatically turn off display when no video for x amount of time

        Command: SET AUTOCEC_D out prm
        Return: AUTOCEC_D out prm
        Parameter out: out1, out2, out3, out4
        Parameter prm: 1-30 minutes. Default is 2
        Example: SET AUTOCEC_D out1 2
        Return: AUTOCEC_D out1 2
        Description:
        When no active signal to HDMI1, after 2 minutes CEC will turn off the display.
        """

        return self.send(f"SET AUTOCEC_D {output} {prm}")

    def get_cec_delay(self, output):
        """Get the status of the CEC auto power delay

        Command: GET AUTOCEC_D out
        Return: AUTOCEC_D out prm
        Parameter out: out1, out2, out3, out4
        Parameter prm: 1-30 minutes
        Example: GET AUTOCEC_D out1
        Return: AUTOCEC_D out1 2"""

        return self.send(f"GET AUTOCEC_D {output}")

    def set_hdcp(self, input, prm):
        """Turn on or off HDCP support for input

        Command: SET HDCP_S in prm
        Return: HDCP_S in prm
        Parameter prm: on, off
        Parameter in: in1, in2, in3, in4
        Example: SET HDCP_S in1 on
        Return: HDCP_S in1 on"""

        return self.send(f"SET HDCP_S {input} {prm}")

    def get_hdcp(self, input):
        """Get the HDCP status of input

        Command: GET HDCP_S in
        Return: HDCP_S in prm
        Parameter prm: on, off
        Parameter in: in1, in2, in3, in4
        Example: GET HDCP_S in1
        Return: HDCP_S in1 on
        """

        return self.send(f"GET HDCP_S {input}")

    def set_edid(self, input, prm):
        """Set the EDID for the Input

        Command: SET EDID in prm

        Return: EDID in prm

        Parameter in: in1, in2, in3, in4

        Parameter prm: 1-16

        1: Copy form hdmi output 1
        2: Copy form hdmi output 2
        3: Copy form hdmi output 3
        4: Copy form hdmi output 4
        5~10: Reserved
        11: Fixed 4K60 2.0CH PCM Audio with HDR
        12: Fixed 4K60 2.0CH PCM Audio with SDR
        13: Fixed 4K30 2.0CH PCM Audio with HDR
        14: Fixed 4K30 2.0CH PCM Audio with SDR
        15: Fixed 1080p@60Hz 2.0CH PCM Audio with HDR
        16: Fixed 1080p@60Hz 2.0CH PCM Audio with SDR
        Example: SET EDID in1 12

        Return: EDID in1 12
        Description:
        Set the EDID for input1 to 4k60 2.0CH PCM Audio with SDR"""

        return self.send(f"SET EDID {input} {prm}")

    def get_edid_all(self):
        """Get all input EDID status

        Command: GET EDID all

        Return:

        EDID in prm
        EDID in prm
        EDID in prm
        ...
        Parameter prm: 1-16

        1: Copy form hdmi output 1
        2: Copy form hdmi output 2
        3: Copy form hdmi output 3
        4: Copy form hdmi output 4
        5~10: Reserved
        11: Fixed 4K60 2.0CH PCM Audio with HDR
        12: Fixed 4K60 2.0CH PCM Audio with SDR
        13: Fixed 4K30 2.0CH PCM Audio with HDR
        14: Fixed 4K30 2.0CH PCM Audio with SDR
        15: Fixed 1080p@60Hz 2.0CH PCM Audio with HDR
        16: Fixed 1080p@60Hz 2.0CH PCM Audio with SDR
        Example: GET EDID all

        Return:

        EDID in1 01
        EDID in2 13
        EDID in3 12
        EDID in4 4"""

        return self.send("GET EDID all")

    def get_edid(self, input):
        """Get the EDID status of one input

        Command: GET EDID in

        Return: EDID in prm

        Parameter in: in1, in2, in3, in4

        Parameter prm: 1-16

        1: Copy form hdmi output 1
        2: Copy form hdmi output 2
        3: Copy form hdmi output 3
        4: Copy form hdmi output 4
        5~10: Reserved
        11: Fixed 4K60 2.0CH PCM Audio with HDR
        12: Fixed 4K60 2.0CH PCM Audio with SDR
        13: Fixed 4K30 2.0CH PCM Audio with HDR
        14: Fixed 4K30 2.0CH PCM Audio with SDR
        15: Fixed 1080p@60Hz 2.0CH PCM Audio with HDR
        16: Fixed 1080p@60Hz 2.0CH PCM Audio with SDR
        Example: GET EDID in1

        Return: EDID in1 12"""

        return self.send(f"GET EDID {input}")

    def set_edid_write(self, input, prm1, prm2):
        """Write EDID content to input

        Command: SET EDID_W in prm1 prm2

        Return: EDID_W in prm1 prm3

        Parameter in: in1, in2, in3, in4

        Parameter prm1: block0, block1

        Parameter prm2: one block of 256 bytes edid ascii data with spaces (hex data need conversion into ASCII code)

        Parameter prm3: ok, error

        error: Checksum error
        Example:

        SET EDID_W in block0 00ffffffffffff004c2d140f000e0001011c0103805932780a23ada4544d99260f474abdef80714f81c0810081809500a9c0b300010108e80030f2705a80b0588a00501d7400001e023a801871382d40582c4500501d7400001e000000fd00184b0f873c000a202020202020000000fc0053414d53554e470a20202020200177
        Return: EDID_W in1 block0 ok"""

        return self.send(f"SET EDID_W {input} {prm1} {prm2}")

    def get_edid_output(self, output):
        """Read the EDID information from output

        Command: GET EDID_R out

        Return: EDID_R out prm1 prm2

        Parameter prm1: block0, block1

        Parameter prm2: one block of 256 bytes edid ascii data with spaces (hex data need conversion into ASCII code)

        Example: GET EDID_R out1

        Return:

        EDID_R out1 block0 00ffffffffffff004c2d140f000e0001011c0103805932780a23ada4544d99260f474abdef80714f81c0810081809500a9c0b300010108e80030f2705a80b0588a00501d7400001e023a801871382d40582c4500501d7400001e000000fd00184b0f873c000a202020202020000000fc0053414d53554e470a20202020200177
        EDID_R out1 block1 020356f05761101f041305142021225d5e5f606566626364071603122909070715075057070183010000e2004fe305c3016e030c002000b83c2000800102030467d85dc401788003e3060d01e30f01e0e5018b849001011d80d0721c1620102c2580501d7400009e662156aa51001e30468f3300501d7400001e000000000089
        """

        return self.send(f"GET EDID_R {output}")

    def factory_reset(self):
        """Reset unit back to factory settings

        Command: RESET
        Return: RESET"""

        return self.send("RESET")

    def reboot(self):
        """Reboot the unit

        Command: REBOOT
        Return: REBOOT
        """

        return self.send("REBOOT")

    def set_ir(self, prm):
        """Sets the IR code set to be unique

        Command: SET IR_SC prm
        Return: IR_SC prm
        Parameter prm: all, mode1, mode2
        mode1 = 0x00
        mode2 = 0x4e
        Example: SET IR_SC mode1
        Return: IR_SC mode1"""

        return self.send(f"SET IR_SC {prm}")

    def get_ir(self):
        """Get the IR code status

        Command: GET IR_SC
        Return: IR_SC prm
        Parameter prm: all, mode1, mode2
        mode1 = 0x00
        mode2 = 0x4e
        Example: GET IR_SC
        Return: IR_SC mode1
        """

        return self.send("GET IR_SC")

    def get_api_list(self):
        """Get API command list

        Command: help
        Return: a list of the API commands
        """

        return self.send_long("help")

    def get_ipaddr(self):
        """Get the IP address of the unit

        Command: GET IPADDR
        Return: ipaddr xxx.xxx.xxx.xxx MASK xxx.xxx.xxx.xxx GATEWAY xxx.xxx.xxx.xxx
        Example: GET IPADDR
        Return: ipaddr 10.0.50.23 MASK 255.255.255.0 GATEWAY 10.0.50.1"""

        return self.send("GET IPADDR")

    def set_ipaddr(self, ip, subnet, gateway):
        """Sets the IP address but does not enable static

        Command: SET IPADDR xxx.xxx.xxx.xxx MASK xxx.xxx.xxx.xxx GATEWAY xxx.xxx.xxx.xxx
        Return: ipaddr xxx.xxx.xxx.xxx MASK xxx.xxx.xxx.xxx GATEWAY xxx.xxx.xxx.xxx
        Example: SET IPADDR 10.0.50.99 MASK 255.255.255.0 GATEWAY 10.0.50.1
        Return: IPADDR 10.0.50.99 MASK 255.255.255.0 GATEWAY 10.0.50.1"""

        # Format the IP address, subnet, and gateway to 'xxx.xxx.xxx.xxx'
        formatted_ip = ".".join([f"{int(octet):03}" for octet in ip.split(".")])
        formatted_subnet = ".".join([f"{int(octet):03}" for octet in subnet.split(".")])
        formatted_gateway = ".".join(
            [f"{int(octet):03}" for octet in gateway.split(".")]
        )

        command = f"SET IPADDR {formatted_ip} MASK {formatted_subnet} GATEWAY {formatted_gateway}"
        return self.send(command)

    def get_network_mode(self):
        """Get Network Mode configuration

        Command: GET NETCFG MODE
        Return: NETCFG MODE DHCP"""

        return self.send("GET NETCFG MODE")

    def set_network_mode(self, prm):
        """Set the Network Mode Configuration

        Command: SET NETCFG MODE prm
        Return: NETCFG MODE prm
        Parameter: HDCP, STATIC
        Example: SET NETCFG MODE STATIC
        Return: NETCFG MODE STATIC"""

        return self.send(f"SET NETCFG MODE {prm}")

    def set_standby(self):
        """Sets the device into standby mode

        Command: STANDBY
        Return: STANDBY!
        """

        return self.send("STANDBY")

    def set_wake(self):
        """Wakes up the device from Standby

        Command: WAKE
        Return: WAKE!
        """

        return self.send("WAKE")

    def get_standby(self):
        """Get the standby status

        Command: GET STANDBY
        Return: prm
        Parameter: STANDBY!, WAKE!
        Example: GET STANDBY
        Return: WAKE!"""

        return self.send("GET STANDBY")

    def get_input_connection(self, input):
        """Get the connections status of the video input

        Command: GET VIDIN_CONNECT in
        Return: VIDIN_CONNECT in prm
        Parameter in: in1, in2, in3, in4
        Parameter prm: Disconnected, Connected
        Example: GET VIDIN_CONNECT in1
        Return: VIDIN_CONNECT in1 Disconnected"""

        return self.send(f"GET VIDIN_CONNECT {input}")

    def get_input_signal(self, input):
        """Get the signal status of the video input

        Command: GET VIDIN_SIG in
        Return: VIDIN_SIG in prm
        Parameter in: in1, in2, in3, in4
        Parameter prm: no, valid
        Example: GET VIDIN_SIG in1
        Return: VIDIN_SIG in1 valid"""

        return self.send(f"GET VIDIN_SIG {input}")

    def get_input_video(self, input):
        """Get the Inputs video format information

        Command: GET VIDIN_FORMAT in
        Return: VIDIN_FORMAT in prm
        Parameter in: in1, in2, in3, in4
        Parameter prm: {}
        prm = {<horizontal>x<vertical>,<rate>;<HDRinfo>;<ColorSpace>,<DeepColor>}
        horizontal = An integer value representing the horizontal
        vertical = An integer value representing the vertical. May have an additional qualifier such as 'i' or 'p'
        rate = An integer value representing the refresh rate
        HDR info = none hdr / static hdr / dynamic hdr
        Color space = RGB / Ycbcr 444 / Ycbcr 422 / Ycbcr 420
        DeepColor = 8 bit / 10 bit / 12 bit / 16 bit
        Example: GET VIDIN_FORMAT in1
        Return: VIDIN_FORMAT in1 3840x2160,30;None HDR;RGB;8bit"""

        return self.send(f"GET VIDIN_FORMAT {input}")

    def get_hdcp_version(self, input):
        """Get the HDCP version on the input

        Command: GET VIDIN_HDCP in
        Return: VIDIN_HDCP in prm
        Parameter in: in1, in2, in3, in4
        Parameter prm: no hdcp, hdcp1.4, hdcp2.2
        Example: GET VIDIN_HDCP in1
        Return: VIDIN_HDCP in1 HDCP1.4"""

        return self.send(f"GET VIDIN_HDCP {input}")

    def get_output_connection(self, output):
        """Get the connection status of the output

        Command: GET VIDOUT_CONNECT output
        Return: VIDOUT_CONNECT in prm
        Parameter out: out1, out2, out3, out4
        Parameter prm: Disconnected, Connected
        Example: GET VIDOUT_CONNECT out1
        Return: VIDOUT_CONNECT out1 Connected"""

        return self.send(f"GET VIDOUT_CONNECT {output}")

    def get_output_signal(self, output):
        """Get the signal status of the video output

        Command: GET VIDOUT_SIG output
        Return: VIDOUT_SIG out prm
        Parameter out: out1, out2, out3, out4
        Parameter prm: no, valid
        Example: GET VIDOUT_SIG out1
        Return: VIDOUT_SIG out1 Valid
        """

        return self.send(f"GET VIDOUT_SIG {output}")

    def get_output_video(self, output):
        """Get the Outputs video format information

        Command: GET VIDOUT_FORMAT output
        Return: VIDOUT_FORMAT out prm
        Parameter out: out1, out2, out3, out4
        Parameter prm: {}
        prm = {<horizontal>x<vertical>,<rate>;<HDRinfo>;<ColorSpace>,<DeepColor>}
        horizontal = An integer value representing the horizontal
        vertical = An integer value representing the vertical. May have an additional qualifier such as 'i' or 'p'
        rate = An integer value representing the refresh rate
        HDR info = none hdr / static hdr / dynamic hdr
        Color space = RGB / Ycbcr 444 / Ycbcr 422 / Ycbcr 420
        DeepColor = 8 bit / 10 bit / 12 bit / 16 bit
        Example: GET VIDOUT_FORMAT out1
        Return: VIDOUT_FORMAT out1 3840x2160,60;None HDR;RGB;8bit"""

        return self.send(f"GET VIDOUT_FORMAT {output}")

    def get_output_hdcp(self, output):
        """Get the Version of HDCP on selected output

        Command: GET VIDOUT_HDCP out
        Return: VIDOUT_HDCP out prm
        Parameter out: out1, out2, out3, out4
        Parameter prm: no hdcp, hdcp1.4, hdcp2.2
        Example: GET VIDOUT_HDCP out2
        Return: VIDOUT_HDCP out2 HDCP2.2"""

        return self.send(f"GET VIDOUT_HDCP {output}")

    def get_version(self):
        """Get the current firmware version

        Command: GET VER
        Return: VER prm
        Parameter: The firmware version on the unit
        Example: GET VER
        Return: VER ARM VER V1.2.8 MCU VER V2.0.8
        """

        return self.send("GET VER")

    def get_hardware(self):
        """Get the current hardware version

        Command: GET HW_VER
        Return: HW_VER prm
        Parameter: The hardware version on the unit
        Example: GET HW_VER
        Return: HW_VER V0.1"""

        return self.send("GET HW_VER")

    def save_preset(self, prm):
        """Save up too 3 Preset Scenes

        Command: SAVE PRESET prm
        Return: PRESET prm
        Parameter: 1, 2, 3
        Example: SAVE PRESET 1
        Return: PRESET 1"""

        return self.send(f"SAVE PRESET {prm}")

    def restore_preset(self, prm):
        """Load the preset

        Command: RESTORE PRESET prm
        Return: PRESET prm
        Parameter: 1, 2, 3
        Example: RESTORE PRESET 1
        Return: PRESET 1
        """

        return self.send(f"RESTORE PRESET {prm}")

    def set_vidout_scaling(self, output, prm):
        """Set the scaling mode of the video output

        Command: SET VIDOUT_SCALE output prm
        Return: VIDOUT_SCALE out prm
        Parameter out: out1, out2, out3, out4, all
        Parameter prm: auto, manual, bypass
        auto = matches TV EDID automatically
        manual = Change the scalar output resolution
        bypass = bypass all HDMI source signal to display
        note: only on output 1 and 2
        Example: SET VIDOUT_SCALE out1 auto
        Return: VIDOUT_SCALE out1 auto"""

        return self.send(f"SET VIDOUT_SCALE {output} {prm}")

    def get_vidout_scaling(self, out):
        """Get the scaling mode of the video output

        Command: GET VIDOUT_SCALE out
        Return: VIDOUT_SCALE out prm
        Parameter out: out1, out2, out3, out4, all
        Parameter prm: auto, manual, bypass
        Example: GET VIDOUT_SCALE out1
        Return: VIDOUT_SCALE out1 auto"""

        return self.send(f"GET VIDOUT_SCALE {out}")

    def set_output_resolution(self, out, prm):
        """Set the output resolution for one or all the outputs

        Command: SET VIDOUT_RES out

        Return: VIDOUT_RES out prm

        Parameter out: out1, out2, out3, out4, all

        Parameter prm: {}

        prm =

        4096x2160@60
        4096x2160@30
        4096x2160@25
        4096x2160@24
        3840x2160@60
        3840x2160@50
        3840x2160@30
        3840x2160@25
        3840x2160@24
        1920x1200@60
        1920x1080@60
        1920x1080@50
        1280x720@60
        1280x720@50
        1680x1050@60
        1600x1200@60
        1600x900@60
        1440x900@60
        1366x768@60
        1360x768@60
        1280x1024@60
        1280x960@60
        1280x800@60
        1280x768@60
        1024x768@60
        800x600@60
        Example: SET VIDOUT_RES out1 3840x2160@60

        Return: VIDOUT_RES out1 3840x2160@60
        Note: Must set scaling to manual first"""

        return self.send(f"SET VIDOUT_RES {out} {prm}")

    def get_output_resolution(self, out):
        """Get the Output Resolution of one or all outputs

        Command: GET VIDOUT_RES out

        Return: VIDOUT_RES out prm

        Parameter out: out1, out2, out3, out4, all

        Parameter prm: {}

        prm =

        4096x2160@60
        4096x2160@30
        4096x2160@25
        4096x2160@24
        3840x2160@60
        3840x2160@50
        3840x2160@30
        3840x2160@25
        3840x2160@24
        1920x1200@60
        1920x1080@60
        1920x1080@50
        1280x720@60
        1280x720@50
        1680x1050@60
        1600x1200@60
        1600x900@60
        1440x900@60
        1366x768@60
        1360x768@60
        1280x1024@60
        1280x960@60
        1280x800@60
        1280x768@60
        1024x768@60
        800x600@60
        Example: GET VIDOUT_RES all

        Return:

        VIDOUT_RES out1 3840x2160@60
        VIDOUT_RES out2 1920x1080@60
        VIDOUT_RES out3 1920x1080@60
        VIDOUT_RES out4 1920x1080@60"""

        return self.send(f"GET VIDOUT_RES {out}")


if __name__ == "__main__":
    from time import sleep

    matrix = MX0404N301_Device("10.0.50.23")

    while True:
        matrix.set_vidmode("videowall")
        sleep(5)
        for index in range(1, 5):
            matrix.set_videowall(f"in{index}", "out1", "out2", "out3", "out4")
            sleep(3)

        matrix.set_vidmode("Matrix")
        sleep(5)
        matrix.set_switch_all("in1")
        sleep(3)
        matrix.set_switch_all("in2")
        sleep(3)
        matrix.set_switch_all("in3")
        sleep(3)
        matrix.set_switch_all("in4")
        sleep(3)

    # get_commands = [
    #     matrix.get_audio_mute("zone1"),
    #     matrix.get_cec_auto("out1"),
    #     matrix.get_cec_delay("out1"),
    #     matrix.get_edid("in1"),
    #     matrix.get_edid_all(),
    #     matrix.get_edid_output("out1"),
    #     matrix.get_hardware(),
    #     matrix.get_hdcp("in1"),
    #     matrix.get_hdcp_version("in1"),
    #     matrix.get_input_connection("in1"),
    #     matrix.get_input_signal("in1"),
    #     matrix.get_input_video("in1"),
    #     matrix.get_ipaddr(),
    #     matrix.get_ir(),
    #     matrix.get_mapping_all(),
    #     matrix.get_mapping_output("out1"),
    #     matrix.get_network_mode(),
    #     matrix.get_output_connection("out1"),
    #     matrix.get_output_hdcp("out1"),
    #     matrix.get_output_resolution("out1"),
    #     matrix.get_output_signal("out1"),
    #     matrix.get_output_video("out1"),
    #     matrix.get_standby(),
    #     matrix.get_version(),
    #     matrix.get_vidmode(),
    #     matrix.get_vidout_scaling("out1"),
    #     matrix.get_vidwall(),
    #     matrix.get_vidwall_bezel(),
    #     matrix.get_vidwall_rotation("out1"),
    #     matrix.get_api_list(),
    # ]
    # for command in get_commands:
    #     print(command)
    #     sleep(0.25)
