"""API Wrapper for CAMSW100-000

Multi Camera Switcher CAMSW100-000 v2.6
Firmware version V1.3.1 or later
"""

import logging
import re
import telnetlib
import socket
import time

logger = logging.getLogger(__name__)


class CAMSW100_Device:
    def __init__(
        self,
        ip: str,
        port: int = 23,
        timeout: int = 5,
        debug: bool = False,
        verbose: bool = True,
        max_retries: int = 3,
    ):
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.debug = debug
        self.tn = None
        self.verbose = verbose
        self.max_retries = max_retries

    def connect(self) -> bool:
        """Connect to the CAMSW100 device via telnet"""
        for attempt in range(self.max_retries):
            if self.tn is None:
                try:
                    if self.verbose:
                        print(
                            f"Attempting to connect to {self.ip}:{self.port} (attempt {attempt + 1}/{self.max_retries})"
                        )

                    self.tn = telnetlib.Telnet(self.ip, self.port, timeout=self.timeout)
                    if self.debug:
                        self.tn.set_debuglevel(1)

                    # Wait for welcome message
                    self.tn.read_until(b"Welcome!", timeout=self.timeout)

                    if self.verbose:
                        print(f"Connected to {self.ip}")
                    return True

                except (socket.timeout, EOFError, ConnectionRefusedError, OSError) as e:
                    self.tn = None
                    if self.verbose:
                        print(f"Connection attempt {attempt + 1} failed: {e}")
                    if attempt == self.max_retries - 1:
                        raise ConnectionError(
                            f"Connection to {self.ip}:{self.port} failed after {self.max_retries} attempts. Last error: {e}"
                        ) from e
                    time.sleep(2)
            else:
                return True
        return False

    def send(self, message):
        """Send a command to the device and return the response"""
        try:
            if not self.connect():
                return "Failed to connect"
        except TimeoutError as e:
            if self.verbose:
                print(f"Error connecting to {self.ip}: {e}")
            return "Failed to connect"

        try:
            if self.verbose:
                print(f"Sending command: {message}")

            self.tn.write(message.encode("ascii") + b"\r\n")

            # Read response - wait a bit for the response to come back
            time.sleep(0.1)
            response = self.tn.read_very_eager()

            # Clean up the response
            cleaned_response = response.decode("ascii").strip()
            lines = cleaned_response.split("\n")
            # Remove empty lines and clean up
            cleaned_lines = [line.strip() for line in lines if line.strip()]
            finished_response = "\n".join(cleaned_lines)

            if self.verbose:
                print(f"Received response: {finished_response}")
            return finished_response

        except Exception as e:
            if self.verbose:
                print(f"Error sending command to {self.ip}: {e}")
            return "Failed to send command"

    def close(self):
        """Close the connection to the device"""
        if self.tn is not None:
            self.tn.close()
            self.tn = None
            if self.verbose:
                print(f"Closed connection to {self.ip}")

    # Device Management Methods
    def set_device_alias(self, device_name: str) -> str:
        """Set the device alias (1-31 characters, letters/numbers/'_'/'-'; must start/end with letter or number)"""
        if not 1 <= len(device_name) <= 31:
            return "Error: Device name must be 1-31 characters long"

        # Validate characters
        allowed_chars = set(
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
        )
        if not set(device_name).issubset(allowed_chars):
            return "Error: Device name can only contain letters, numbers, '_', and '-'"

        # Check if starts/ends with letter or number
        if not (device_name[0].isalnum() and device_name[-1].isalnum()):
            return "Error: Device name must start and end with a letter or number"

        return self.send(f"SET ALIAS {device_name}")

    def get_device_alias(self) -> str:
        """Retrieve the current device alias"""
        return self.send("GET ALIAS")

    def set_ip_address(
        self,
        ip_mode: str,
        ip_address: str = None,
        netmask: str = None,
        gateway: str = None,
        dns_server: str = None,
    ) -> str:
        """Set device IP configuration to DHCP or static"""
        if ip_mode.upper() == "DHCP":
            return self.send("SET IPADDR DHCP")
        elif ip_mode.upper() == "STATIC":
            if not ip_address or not netmask:
                return "Error: IP address and netmask are required for static mode"
            command = f"SET IPADDR STATIC {ip_address} {netmask}"
            if gateway:
                command += f" {gateway}"
            if dns_server:
                command += f" {dns_server}"
            return self.send(command)
        else:
            return "Error: ip_mode must be 'DHCP' or 'STATIC'"

    def get_ip_address(self) -> str:
        """Query current IP configuration"""
        return self.send("GET IPADDR")

    def get_firmware_version(self, module: str = "ALL") -> str:
        """Obtain firmware version for specified module or ALL. Modules: MAINSOC, CAMCHIP, VIDEOCHIP"""
        valid_modules = ["ALL", "MAINSOC", "CAMCHIP", "VIDEOCHIP"]
        if module.upper() not in valid_modules:
            return (
                f"Error: Invalid module. Valid modules are: {', '.join(valid_modules)}"
            )
        return self.send(f"GET VER {module.upper()}")

    def get_mac_address(self) -> str:
        """Obtain MAC address in colon-separated format"""
        return self.send("GET MACADDR")

    def reboot(self) -> str:
        """Reboot the device"""
        return self.send("REBOOT")

    def factory_reset(self) -> str:
        """Restore device to factory defaults and reboot to recovery/safe mode"""
        return self.send("RESET")

    # Input/Output Settings Methods
    def set_output_resolution(self, output: str, resolution: str) -> str:
        """Set output resolution for specified output or AUTO to follow display EDID"""
        valid_outputs = ["OUT1", "OUT2"]
        if output.upper() not in valid_outputs:
            return (
                f"Error: Invalid output. Valid outputs are: {', '.join(valid_outputs)}"
            )

        if resolution.upper() == "AUTO":
            return self.send(f"SET VIDOUT_RES {output.upper()} AUTO")
        else:
            return self.send(f"SET VIDOUT_RES {output.upper()} {resolution}")

    def get_output_resolution(self, output: str = "ALL") -> str:
        """Get output resolution(s). Response can show DISCONNECTED and optional AUTO flag"""
        valid_outputs = ["OUT1", "OUT2", "USB", "ALL"]
        if output.upper() not in valid_outputs:
            return (
                f"Error: Invalid output. Valid outputs are: {', '.join(valid_outputs)}"
            )
        return self.send(f"GET VIDOUT_RES {output.upper()}")

    def get_output_connection_status(self, output: str = "ALL") -> str:
        """Query whether outputs are connected"""
        valid_outputs = ["OUT1", "OUT2", "USB", "ALL"]
        if output.upper() not in valid_outputs:
            return (
                f"Error: Invalid output. Valid outputs are: {', '.join(valid_outputs)}"
            )
        return self.send(f"GET VIDOUT_CONNECT {output.upper()}")

    def set_hd_mode(self, mode: str) -> str:
        """Enable/disable HD mode for UVC USB output"""
        if mode.upper() not in ["ON", "OFF"]:
            return "Error: mode must be 'ON' or 'OFF'"
        return self.send(f"SET UVC_HDMODE {mode.upper()}")

    def get_hd_mode(self) -> str:
        """Get current UVC HD mode"""
        return self.send("GET UVC_HDMODE")

    def set_output_hdcp(self, output: str, mode: str) -> str:
        """Enable/disable HDCP protection on HDMI output"""
        valid_outputs = ["OUT1", "OUT2"]
        if output.upper() not in valid_outputs:
            return (
                f"Error: Invalid output. Valid outputs are: {', '.join(valid_outputs)}"
            )
        if mode.upper() not in ["ON", "OFF"]:
            return "Error: mode must be 'ON' or 'OFF'"
        return self.send(f"SET HDCP {output.upper()} {mode.upper()}")

    def get_output_hdcp(self, output: str = "ALL") -> str:
        """Get HDCP configuration for outputs"""
        valid_outputs = ["OUT1", "OUT2", "ALL"]
        if output.upper() not in valid_outputs:
            return (
                f"Error: Invalid output. Valid outputs are: {', '.join(valid_outputs)}"
            )
        return self.send(f"GET HDCP {output.upper()}")

    def get_input_connection_status(self, source: str = "ALL") -> str:
        """Query whether specified input is connected"""
        return self.send(f"GET VIDIN_CONNECT {source}")

    def get_input_signal_status(self, source: str = "ALL") -> str:
        """Query if specified source has valid signal"""
        return self.send(f"GET VIDIN_SIG {source}")

    def get_input_video_format(self, source: str = "ALL") -> str:
        """Get video format for the source"""
        return self.send(f"GET VIDIN_FORMAT {source}")

    def get_input_audio_format(self, source: str = "ALL") -> str:
        """Get audio format for the source"""
        return self.send(f"GET AUDIN_FORMAT {source}")

    # Video Switching Methods
    def set_low_latency_mode(self, mode: str) -> str:
        """Enable/disable low latency mode"""
        if mode.upper() not in ["ON", "OFF"]:
            return "Error: mode must be 'ON' or 'OFF'"
        return self.send(f"SET LOW_LATENCY_FN {mode.upper()}")

    def get_low_latency_mode(self) -> str:
        """Get low latency mode configuration"""
        return self.send("GET LOW_LATENCY_FN")

    def set_input_to_output(self, source: str, output: str = None) -> str:
        """Switch an input to an output. If OUT not specified, applies to all outputs"""
        if output:
            return self.send(f"SET SW {source} {output}")
        else:
            return self.send(f"SET SW {source}")

    def get_input_of_output(self, output: str = "ALL") -> str:
        """Get which source is displayed on an output"""
        valid_outputs = ["OUT1", "OUT2", "ALL"]
        if output.upper() not in valid_outputs:
            return (
                f"Error: Invalid output. Valid outputs are: {', '.join(valid_outputs)}"
            )
        return self.send(f"GET SW {output.upper()}")

    def set_multiview_layout(self, layout: str) -> str:
        """Set multiview layout used on OUT2"""
        return self.send(f"SET MV_LAYOUT {layout}")

    def get_multiview_layout(self) -> str:
        """Get the current multiview layout"""
        return self.send("GET MV_LAYOUT")

    def set_multiview_layout_and_sources(self, layout: str, *window_sources) -> str:
        """Set layout and assign video sources to child windows"""
        command = f"SET MV_WIN_SRC {layout}"
        for i in range(0, len(window_sources), 2):
            if i + 1 < len(window_sources):
                command += f" {window_sources[i]} {window_sources[i + 1]}"
        return self.send(command)

    def get_multiview_layout_and_sources(self) -> str:
        """Get current multiview layout and child window sources"""
        return self.send("GET MV_WIN_SRC")

    # Audio Processing Methods
    def set_dsp_audio_mixing(self, dsp_out: str, dsp_in: str, mode: str) -> str:
        """Set whether given audio input participates in mixing for the specified audio output"""
        if mode.upper() not in ["ON", "OFF"]:
            return "Error: mode must be 'ON' or 'OFF'"
        return self.send(f"SET DSP_MIX {dsp_out} {dsp_in} {mode.upper()}")

    def get_dsp_audio_mixing(self, dsp_out: str = "ALL", dsp_in: str = None) -> str:
        """Get mixing config for a given crosspoint or list inputs participating for an output"""
        if dsp_in:
            return self.send(f"GET DSP_MIX {dsp_out} {dsp_in}")
        else:
            return self.send(f"GET DSP_MIX {dsp_out}")

    def set_dsp_input_channel(self, usb_in: str = None, hdmi_in: str = None) -> str:
        """Select which physical input is routed into the DSP's USBIN or HDMIIN channel"""
        if usb_in:
            return self.send(f"SET DSP_AUD_SRC USBIN {usb_in}")
        elif hdmi_in:
            return self.send(f"SET DSP_AUD_SRC HDMIIN {hdmi_in}")
        else:
            return "Error: Must specify either usb_in or hdmi_in"

    def get_dsp_input_channel(self, channel: str = "ALL") -> str:
        """Get DSP input channel mapping"""
        valid_channels = ["USBIN", "HDMIIN", "ALL"]
        if channel.upper() not in valid_channels:
            return f"Error: Invalid channel. Valid channels are: {', '.join(valid_channels)}"
        return self.send(f"GET DSP_AUD_SRC {channel.upper()}")

    def set_dsp_input_mute(self, dsp_in: str, mode: str) -> str:
        """Mute/unmute specified DSP input channel"""
        if mode.upper() not in ["ON", "OFF"]:
            return "Error: mode must be 'ON' or 'OFF'"
        return self.send(f"SET DSP_AUD_GAIN_MUTE {dsp_in} {mode.upper()}")

    def get_dsp_input_mute(self, dsp_in: str = "ALL") -> str:
        """Get mute state for DSP input channels"""
        return self.send(f"GET DSP_AUD_GAIN_MUTE {dsp_in}")

    def set_dsp_input_gain(self, dsp_in: str, gain: int) -> str:
        """Set DSP input gain in dB range [-20, +30]"""
        if not -20 <= gain <= 30:
            return "Error: Gain must be between -20 and +30 dB"
        return self.send(f"SET DSP_AUD_GAIN {dsp_in} {gain}")

    def get_dsp_input_gain(self, dsp_in: str = "ALL") -> str:
        """Query DSP input gain(s)"""
        return self.send(f"GET DSP_AUD_GAIN {dsp_in}")

    def set_dsp_output_mute(self, dsp_out: str, mode: str) -> str:
        """Mute/unmute specified DSP output channel"""
        if mode.upper() not in ["ON", "OFF"]:
            return "Error: mode must be 'ON' or 'OFF'"
        return self.send(f"SET DSP_AUD_VOL_MUTE {dsp_out} {mode.upper()}")

    def get_dsp_output_mute(self, dsp_out: str = "ALL") -> str:
        """Get mute state for DSP outputs"""
        return self.send(f"GET DSP_AUD_VOL_MUTE {dsp_out}")

    def set_dsp_output_volume(self, dsp_out: str, volume: int) -> str:
        """Set DSP output volume in dB range [-100, 0]"""
        if not -100 <= volume <= 0:
            return "Error: Volume must be between -100 and 0 dB"
        return self.send(f"SET DSP_AUD_VOL {dsp_out} {volume}")

    def get_dsp_output_volume(self, dsp_out: str = "ALL") -> str:
        """Query DSP output volumes"""
        return self.send(f"GET DSP_AUD_VOL {dsp_out}")

    # Standby and Peripheral Control Methods
    def set_standby_mode(self, mode: str) -> str:
        """Manually set device to enter (OFF) or exit (ON) standby mode"""
        if mode.upper() not in ["ON", "OFF"]:
            return "Error: mode must be 'ON' or 'OFF'"
        return self.send(f"SET STANDBY {mode.upper()}")

    def get_standby_mode(self) -> str:
        """Query whether the device is in standby"""
        return self.send("GET STANDBY")

    def set_automatic_standby(self, mode: str) -> str:
        """Enable/disable automatic standby feature"""
        if mode.upper() not in ["ON", "OFF"]:
            return "Error: mode must be 'ON' or 'OFF'"
        return self.send(f"SET AUTO_STANDBY_FN {mode.upper()}")

    def get_automatic_standby(self) -> str:
        """Query automatic standby feature state"""
        return self.send("GET AUTO_STANDBY_FN")

    def set_automatic_standby_timeout(self, timeout: int) -> str:
        """Set automatic standby timeout in seconds (0-3600)"""
        if not 0 <= timeout <= 3600:
            return "Error: Timeout must be between 0 and 3600 seconds"
        return self.send(f"SET AUTO_STANDBY_D {timeout}")

    def get_automatic_standby_timeout(self) -> str:
        """Query automatic standby timeout value"""
        return self.send("GET AUTO_STANDBY_D")

    def set_cec_command(self, output: str, on_off: str, cec_code: str) -> str:
        """Configure stored CEC command for powering displays on/off"""
        valid_outputs = ["OUT1", "OUT2"]
        if output.upper() not in valid_outputs:
            return (
                f"Error: Invalid output. Valid outputs are: {', '.join(valid_outputs)}"
            )
        if on_off.upper() not in ["ON", "OFF"]:
            return "Error: on_off must be 'ON' or 'OFF'"
        return self.send(
            f"SET CECCMD_EDIT {output.upper()} {on_off.upper()} {cec_code}"
        )

    def get_cec_command(self, output: str = "ALL", on_off: str = None) -> str:
        """Query CEC command configuration(s)"""
        if on_off:
            return self.send(f"GET CECCMD_EDIT {output} {on_off}")
        else:
            return self.send(f"GET CECCMD_EDIT {output}")

    def set_rs232_work_mode(self, mode: str) -> str:
        """Set RS232 port work mode"""
        if mode.upper() not in ["API", "COM"]:
            return "Error: mode must be 'API' or 'COM'"
        return self.send(f"SET UART_MODE {mode.upper()}")

    def get_rs232_work_mode(self) -> str:
        """Get RS232 port work mode"""
        return self.send("GET UART_MODE")

    def set_power_on_off_via_rs232(self, mode: str) -> str:
        """Configure whether power on/off will send RS232 command in addition to CEC"""
        if mode.upper() not in ["ON", "OFF"]:
            return "Error: mode must be 'ON' or 'OFF'"
        return self.send(f"SET UARTPWR_FN {mode.upper()}")

    def get_power_on_off_via_rs232(self) -> str:
        """Query RS232 power on/off sending configuration"""
        return self.send("GET UARTPWR_FN")

    def configure_rs232_settings(
        self, baud_rate: int, parity: str, data_bit: int, stop_bit: int
    ) -> str:
        """Configure RS232 port parameters"""
        valid_baud_rates = [9600, 19200, 38400, 57600, 115200]
        if baud_rate not in valid_baud_rates:
            return f"Error: Invalid baud rate. Valid rates are: {', '.join(map(str, valid_baud_rates))}"

        valid_parity = ["NONE", "ODD", "EVEN"]
        if parity.upper() not in valid_parity:
            return (
                f"Error: Invalid parity. Valid options are: {', '.join(valid_parity)}"
            )

        if data_bit not in [7, 8]:
            return "Error: Data bit must be 7 or 8"
        if stop_bit not in [1, 2]:
            return "Error: Stop bit must be 1 or 2"

        return self.send(
            f"SET UART_CFG {baud_rate} {parity.upper()} {data_bit} {stop_bit}"
        )

    def get_rs232_settings(self) -> str:
        """Query RS232 configuration"""
        return self.send("GET UART_CFG")

    def set_rs232_baud_rate(self, baud_rate: int) -> str:
        """Set RS232 baud rate separately"""
        valid_baud_rates = [9600, 19200, 38400, 57600, 115200]
        if baud_rate not in valid_baud_rates:
            return f"Error: Invalid baud rate. Valid rates are: {', '.join(map(str, valid_baud_rates))}"
        return self.send(f"SET UART_B {baud_rate}")

    def get_rs232_baud_rate(self) -> str:
        """Get current RS232 baud rate"""
        return self.send("GET UART_B")

    def set_rs232_command(self, cmd_name: str, format_type: str, cmd_str: str) -> str:
        """Configure RS232 command string"""
        if format_type.upper() not in ["HEX", "STR"]:
            return "Error: format_type must be 'HEX' or 'STR'"
        return self.send(f"SET UART_CMD {cmd_name} {format_type.upper()} {cmd_str}")

    def delete_rs232_command(self, cmd_name: str) -> str:
        """Delete a defined RS232 command"""
        return self.send(f"SET UART_CMD_D {cmd_name}")

    def get_rs232_command(self, cmd_name: str = "ALL") -> str:
        """Query a defined RS232 command or all commands"""
        return self.send(f"GET UART_CMD {cmd_name}")

    def send_rs232_command(self, cmd_name: str) -> str:
        """Send a previously defined RS232 command"""
        return self.send(f"SET UART_CMD_S {cmd_name}")

    def send_rs232_data(self, format_type: str, cmd_str: str) -> str:
        """Send RS232 data directly"""
        if format_type.upper() not in ["HEX", "STR"]:
            return "Error: format_type must be 'HEX' or 'STR'"
        return self.send(f"SET UART_S {format_type.upper()} {cmd_str}")

    def set_send_cmd(self, mode: str, method: str = None) -> str:
        """Configure device to send CEC and/or RS232 command when powering"""
        if mode.upper() not in ["ON", "OFF"] and not mode.isdigit():
            return "Error: mode must be 'ON', 'OFF', or a command name"

        if method:
            valid_methods = ["RS232", "CEC", "ALL"]
            if method.upper() not in valid_methods:
                return f"Error: Invalid method. Valid methods are: {', '.join(valid_methods)}"
            return self.send(f"SET SEND_CMD {mode} {method.upper()}")
        else:
            return self.send(f"SET SEND_CMD {mode}")

    def send_cec_data(self, output: str, cec_code: str) -> str:
        """Send arbitrary CEC data directly"""
        valid_outputs = ["OUT1", "OUT2"]
        if output.upper() not in valid_outputs:
            return (
                f"Error: Invalid output. Valid outputs are: {', '.join(valid_outputs)}"
            )
        return self.send(f"SET CEC_CMD {output.upper()} {cec_code}")

    # NDI Input/Output Methods
    def set_ndi_rx_group_name(self, group_name: str) -> str:
        """Set the NDI RX module group name"""
        return self.send(f"SET NDI_RX_GROUP {group_name}")

    def get_ndi_rx_group_name(self) -> str:
        """Get the NDI RX group name"""
        return self.send("GET NDI_RX_GROUP")

    def set_ndi_rx_device_name(self, device_name: str) -> str:
        """Set the device name for the NDI RX module"""
        return self.send(f"SET NDI_RX_DEV_NAME {device_name}")

    def get_ndi_rx_device_name(self) -> str:
        """Get the NDI RX device name"""
        return self.send("GET NDI_RX_DEV_NAME")

    def get_ndi_device_list(self, device_type: str = "ALL") -> str:
        """Obtain list of discovered NDI devices on network"""
        valid_types = ["TX", "RX", "ALL"]
        if device_type.upper() not in valid_types:
            return (
                f"Error: Invalid device type. Valid types are: {', '.join(valid_types)}"
            )
        return self.send(f"GET NDI_SCAN_DEV_LIST {device_type.upper()}")

    def get_ndi_channel_list(self, device_name: str = "ALL") -> str:
        """Get list of channels for NDI devices"""
        return self.send(f"GET NDI_SCAN_CHN_LIST {device_name}")

    def set_ndi_video_source(
        self, decoder: int, tx_device_name: str, channel_name: str = None
    ) -> str:
        """Assign an NDI TX channel to an NDI RX decoder"""
        if not 1 <= decoder <= 4:
            return "Error: decoder must be between 1 and 4"

        if channel_name:
            return self.send(
                f"SET NDI_IN_SRC {decoder} {tx_device_name} {channel_name}"
            )
        else:
            return self.send(f"SET NDI_IN_SRC {decoder} {tx_device_name}")

    def delete_ndi_video_source(self, decoder: int) -> str:
        """Delete NDI video source assignment for specified decoder"""
        if not 1 <= decoder <= 4:
            return "Error: decoder must be between 1 and 4"
        return self.send(f"SET NDI_IN_SRC {decoder}")

    def get_ndi_video_source(self, decoder: int = "ALL") -> str:
        """Get NDI RX decoder source(s)"""
        if decoder != "ALL" and not (1 <= decoder <= 4):
            return "Error: decoder must be between 1 and 4 or 'ALL'"
        return self.send(f"GET NDI_IN_SRC {decoder}")

    def set_ndi_tx_group_name(self, group_name: str) -> str:
        """Set NDI TX group name"""
        return self.send(f"SET NDI_TX_GROUP {group_name}")

    def get_ndi_tx_group_name(self) -> str:
        """Get the NDI TX group name"""
        return self.send("GET NDI_TX_GROUP")

    def set_ndi_tx_device_name(self, device_name: str) -> str:
        """Set the device name for NDI TX module"""
        return self.send(f"SET NDI_TX_DEV_NAME {device_name}")

    def get_ndi_tx_device_name(self) -> str:
        """Get the NDI TX device name"""
        return self.send("GET NDI_TX_DEV_NAME")

    def set_ndi_tx_channel_name(self, channel_name: str) -> str:
        """Set NDI TX channel name"""
        return self.send(f"SET NDI_TX_CHN_NAME {channel_name}")

    def get_ndi_tx_channel_name(self) -> str:
        """Get NDI TX channel name"""
        return self.send("GET NDI_TX_CHN_NAME")

    def set_ndi_tx_encoding_parameter(
        self,
        stream: str,
        encode_mode: str,
        resolution: str,
        frame_rate: int,
        bit_rate_ctl: str,
        bit_rate: int,
        gop_size: int,
    ) -> str:
        """Set NDI TX encoding parameters"""
        valid_streams = ["NDI11", "NDI12"]
        if stream.upper() not in valid_streams:
            return (
                f"Error: Invalid stream. Valid streams are: {', '.join(valid_streams)}"
            )

        valid_encode_modes = ["H.264", "H.265"]
        if encode_mode not in valid_encode_modes:
            return f"Error: Invalid encode mode. Valid modes are: {', '.join(valid_encode_modes)}"

        return self.send(
            f"SET NDI_TX_VENC_CFG {stream.upper()} {encode_mode} {resolution} {frame_rate} {bit_rate_ctl} {bit_rate} {gop_size}"
        )

    def get_ndi_tx_encoding_parameter(self, stream: str = "ALL") -> str:
        """Get NDI TX encoding parameters for one or both streams"""
        valid_streams = ["NDI11", "NDI12", "ALL"]
        if stream.upper() not in valid_streams:
            return (
                f"Error: Invalid stream. Valid streams are: {', '.join(valid_streams)}"
            )
        return self.send(f"GET NDI_TX_VENC_CFG {stream.upper()}")

    def set_ndi_stream_output(self, stream: str, mode: str) -> str:
        """Enable/disable NDI TX stream output for main or preview stream"""
        valid_streams = ["NDI11", "NDI12"]
        if stream.upper() not in valid_streams:
            return (
                f"Error: Invalid stream. Valid streams are: {', '.join(valid_streams)}"
            )
        if mode.upper() not in ["ON", "OFF"]:
            return "Error: mode must be 'ON' or 'OFF'"
        return self.send(f"SET NDI_TX_STREAM_FN {stream.upper()} {mode.upper()}")

    def get_ndi_stream_output(self, stream: str = "ALL") -> str:
        """Query NDI TX stream output enable state"""
        valid_streams = ["NDI11", "NDI12", "ALL"]
        if stream.upper() not in valid_streams:
            return (
                f"Error: Invalid stream. Valid streams are: {', '.join(valid_streams)}"
            )
        return self.send(f"GET NDI_TX_STREAM_FN {stream.upper()}")

    def test_connection(self) -> bool:
        """Test the connection to the device with a simple command"""
        try:
            if not self.tn:
                self.connect()

            if self.tn:
                # Try a simple command that should work on CAMSW100
                result = self.get_device_alias()
                return result and "Error:" not in result
            return False
        except Exception as e:
            if self.verbose:
                print(f"Connection test failed: {e}")
            return False

    def test_all_get_commands(self, debug=False) -> dict:
        """Test all get commands in the CAMSW100 device wrapper"""
        print("=" * 80)
        print("CAMSW100 DEVICE WRAPPER - COMPREHENSIVE GET COMMAND TEST")
        print("=" * 80)

        # Ensure we have a connection
        if not self.tn:
            print("Connecting to device...")
            try:
                self.connect()
                if not self.tn:
                    print("ERROR: Failed to establish connection")
                    return {"success": 0, "failure": 0, "total": 0, "success_rate": 0.0}
            except Exception as e:
                print(f"ERROR: Connection failed - {e}")
                return {"success": 0, "failure": 0, "total": 0, "success_rate": 0.0}

        # Get device information for header
        print("\n" + "=" * 80)
        print("DEVICE INFORMATION")
        print("=" * 80)

        try:
            # Get device alias
            alias_response = self.get_device_alias()
            if alias_response and "Error:" not in alias_response:
                print(f"Device Alias: {alias_response.strip()}")
            else:
                print("Device Alias: Unknown")

            # Get firmware version
            fw_response = self.get_firmware_version()
            if fw_response and "Error:" not in fw_response:
                print(f"Firmware Version: {fw_response.strip()}")
            else:
                print("Firmware Version: Unknown")

            # Get MAC address
            mac_response = self.get_mac_address()
            if mac_response and "Error:" not in mac_response:
                print(f"MAC Address: {mac_response.strip()}")
            else:
                print("MAC Address: Unknown")

        except Exception as e:
            print(f"Error getting device info: {e}")
            print("Device Alias: Unknown")
            print("Firmware Version: Unknown")
            print("MAC Address: Unknown")

        print("=" * 80)

        # Define all get methods to test with their corresponding commands
        get_methods = [
            # Device Management
            ("get_device_alias", "Get current device alias", "GET ALIAS"),
            ("get_ip_address", "Get current IP configuration", "GET IPADDR"),
            ("get_firmware_version", "Get firmware version", "GET VER ALL"),
            ("get_mac_address", "Get MAC address", "GET MACADDR"),
            # Input/Output Settings
            ("get_output_resolution", "Get output resolution", "GET VIDOUT_RES ALL"),
            (
                "get_output_connection_status",
                "Get output connection status",
                "GET VIDOUT_CONNECT ALL",
            ),
            ("get_hd_mode", "Get UVC HD mode", "GET UVC_HDMODE"),
            ("get_output_hdcp", "Get HDCP configuration", "GET HDCP ALL"),
            (
                "get_input_connection_status",
                "Get input connection status",
                "GET VIDIN_CONNECT ALL",
            ),
            ("get_input_signal_status", "Get input signal status", "GET VIDIN_SIG ALL"),
            (
                "get_input_video_format",
                "Get input video format",
                "GET VIDIN_FORMAT ALL",
            ),
            (
                "get_input_audio_format",
                "Get input audio format",
                "GET AUDIN_FORMAT ALL",
            ),
            # Video Switching
            ("get_low_latency_mode", "Get low latency mode", "GET LOW_LATENCY_FN"),
            ("get_input_of_output", "Get input of output", "GET SW ALL"),
            ("get_multiview_layout", "Get multiview layout", "GET MV_LAYOUT"),
            (
                "get_multiview_layout_and_sources",
                "Get multiview layout and sources",
                "GET MV_WIN_SRC",
            ),
            # Audio Processing
            ("get_dsp_audio_mixing", "Get DSP audio mixing", "GET DSP_MIX ALL"),
            ("get_dsp_input_channel", "Get DSP input channel", "GET DSP_AUD_SRC ALL"),
            ("get_dsp_input_mute", "Get DSP input mute", "GET DSP_AUD_GAIN_MUTE ALL"),
            ("get_dsp_input_gain", "Get DSP input gain", "GET DSP_AUD_GAIN ALL"),
            ("get_dsp_output_mute", "Get DSP output mute", "GET DSP_AUD_VOL_MUTE ALL"),
            ("get_dsp_output_volume", "Get DSP output volume", "GET DSP_AUD_VOL ALL"),
            # Standby and Peripheral Control
            ("get_standby_mode", "Get standby mode", "GET STANDBY"),
            ("get_automatic_standby", "Get automatic standby", "GET AUTO_STANDBY_FN"),
            (
                "get_automatic_standby_timeout",
                "Get automatic standby timeout",
                "GET AUTO_STANDBY_D",
            ),
            ("get_cec_command", "Get CEC commands", "GET CECCMD_EDIT ALL"),
            ("get_rs232_work_mode", "Get RS232 work mode", "GET UART_MODE"),
            ("get_power_on_off_via_rs232", "Get RS232 power control", "GET UARTPWR_FN"),
            ("get_rs232_settings", "Get RS232 settings", "GET UART_CFG"),
            ("get_rs232_baud_rate", "Get RS232 baud rate", "GET UART_B"),
            ("get_rs232_command", "Get RS232 commands", "GET UART_CMD ALL"),
            # NDI Input/Output
            ("get_ndi_rx_group_name", "Get NDI RX group name", "GET NDI_RX_GROUP"),
            ("get_ndi_rx_device_name", "Get NDI RX device name", "GET NDI_RX_DEV_NAME"),
            ("get_ndi_device_list", "Get NDI device list", "GET NDI_SCAN_DEV_LIST ALL"),
            (
                "get_ndi_channel_list",
                "Get NDI channel list",
                "GET NDI_SCAN_CHN_LIST ALL",
            ),
            ("get_ndi_video_source", "Get NDI video source", "GET NDI_IN_SRC ALL"),
            ("get_ndi_tx_group_name", "Get NDI TX group name", "GET NDI_TX_GROUP"),
            ("get_ndi_tx_device_name", "Get NDI TX device name", "GET NDI_TX_DEV_NAME"),
            (
                "get_ndi_tx_channel_name",
                "Get NDI TX channel name",
                "GET NDI_TX_CHN_NAME",
            ),
            (
                "get_ndi_tx_encoding_parameter",
                "Get NDI TX encoding",
                "GET NDI_TX_VENC_CFG ALL",
            ),
            (
                "get_ndi_stream_output",
                "Get NDI stream output",
                "GET NDI_TX_STREAM_FN ALL",
            ),
        ]

        results = []
        success_count = 0
        failure_count = 0

        print(f"\nTesting {len(get_methods)} get methods...")
        print("-" * 80)

        for method_name, description, command in get_methods:
            print(f"\n{method_name}: {description}")
            print(f"Command: {command}")
            print("-" * 60)

            try:
                # Get the method object
                method = getattr(self, method_name)

                # Execute the method
                start_time = time.time()
                result = method()
                execution_time = round(time.time() - start_time, 3)

                # Determine success based on result
                if result is not None:
                    # Check if the response contains error text
                    if isinstance(result, str) and "Error:" in result:
                        success = False
                        failure_count += 1
                        status = f"FAILED ({result})"
                    else:
                        success = True
                        success_count += 1
                        status = "SUCCESS"
                else:
                    success = False
                    failure_count += 1
                    status = "FAILED (no response)"

                # Print results with command instead of function name
                print(f"{'=' * 80}")
                print(f"Command: {command}")
                print(f"Status: {status}")
                print(f"Response: {result}")
                print(f"{'=' * 80}")

                # Store result for summary
                results.append(
                    {
                        "method": method_name,
                        "command": command,
                        "description": description,
                        "success": success,
                        "execution_time": execution_time,
                        "result": result,
                        "status": status,
                    }
                )

            except Exception as e:
                failure_count += 1
                status = f"FAILED (Exception: {str(e)})"
                print(f"Status: {status}")
                print(f"Exception: {str(e)}")

                results.append(
                    {
                        "method": method_name,
                        "command": command,
                        "description": description,
                        "success": False,
                        "execution_time": 0,
                        "result": None,
                        "status": status,
                    }
                )

        # Print summary
        print("\n")
        print(f"Total Methods Tested: {len(get_methods)}")
        print(f"Successful: {success_count}")
        print(f"Failed: {failure_count}")
        print(f"Success Rate: {(success_count / len(get_methods) * 100):.1f}%")

        # Print detailed results table
        print("\n" + "-" * 80)
        print("DETAILED RESULTS")
        print("-" * 80)
        print(f"{'Command':<40} {'Status':<15} {'Time':<8} {'Result'}")
        print("-" * 80)

        for result in results:
            status_short = "✓ PASS" if result["success"] else "✗ FAIL"
            time_str = (
                f"{result['execution_time']}s"
                if result["execution_time"] > 0
                else "N/A"
            )
            # Clean up result string by removing newlines and extra whitespace
            result_str = str(result["result"]).replace("\n", " ").strip()
            # Remove multiple consecutive spaces
            result_str = re.sub(r"\s+", " ", result_str)
            # Truncate if too long
            result_str = result_str[:50] + "..." if len(result_str) > 50 else result_str
            # Use fixed-width formatting with proper spacing
            print(
                f"{result['command']:<40} {status_short:<15} {time_str:<8} {result_str}"
            )

        # Return summary for programmatic use
        summary = {
            "success": success_count,
            "failure": failure_count,
            "total": len(get_methods),
            "success_rate": round(success_count / len(get_methods) * 100, 1),
            "results": results,
        }

        return summary


if __name__ == "__main__":
    # Example usage of the test function
    camsw = CAMSW100_Device("10.0.30.92", port=23)

    try:
        # First test basic connection
        print("Testing basic connection...")
        if camsw.test_connection():
            print("✓ Basic connection test passed")

            # Run comprehensive test of all get commands
            test_results = camsw.test_all_get_commands()

            # Print final summary
            print(
                f"\nFinal Test Results: {test_results['success']}/{test_results['total']} commands passed ({test_results['success_rate']}%)"
            )
        else:
            print("✗ Basic connection test failed - cannot proceed with full test")
            print("Please check:")
            print("1. Device IP address is correct")
            print("2. Device is powered on and connected to network")
            print("3. Telnet service is running on port 23")
            print("4. No firewall blocking the connection")

    except Exception as e:
        print(f"Test failed with error: {e}")
    finally:
        # Close connection
        camsw.close()
