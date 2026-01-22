"""API Wrapper for MX0808-1023"""

from telnetlib import Telnet
from time import sleep
import time
import json
from pprint import PrettyPrinter


class MX0808_1023:
    def __init__(self, ip_address: str, port: int = 23, debug: bool = False):
        self.tn = None
        self.ip_address = ip_address
        self.port = port
        self.debug = debug

        # Initialize structured status dictionary
        self.status = {
            "video": {
                "outputs": {}  # Maps "Output X" to input numbers
            },
            "audio": {
                "mode": None,  # 'independent' or 'follow'
                "outputs": {},  # Maps "Audio Output X" to input numbers
                "volume_levels": {},  # Maps "Output X" to volume (-100 to 0)
                "mute_states": {},  # Maps "Output X" to bool
            },
            "cec": {
                "auto_states": {},  # Maps "Output X" to bool
                "auto_delays": {},  # Maps "Output X" to delay minutes
                "commands": {},  # Maps "Output X" to {"pwron": cmd, "pwroff": cmd}
                "power_states": {},  # Maps "Output X" to bool
            },
            "hdcp": {
                "support": {},  # Maps "Input X" to bool
                "modes": {},  # Maps "Output X" to 'auto' or 'hdcp1.x'
            },
            "edid": {
                "settings": {},  # Maps "Input X" to setting number
                "data": {},  # Maps output number to {"block0": bytes, "block1": bytes}
                "read_status": {},  # Maps output number to {"block0": status, "block1": status}
                "write_status": {},  # Maps input number to {"block0": bool, "block1": bool}
            },
            "system": {"version": None, "ip_address": None},
            "presets": {
                "saved_slots": set()  # Set of used preset numbers
            },
            "resolution": {
                "outputs": {}  # Maps "Output X" to resolution string
            },
            "security": {
                "https_enabled": None,
                "telnet_tls_enabled": None,
                "last_password_change": None,
            },
        }

    def connect(self):
        """Connect to the device and store system information"""
        self.tn = Telnet(self.ip_address, self.port)
        if self.debug:
            self.tn.set_debuglevel(1)
        # Wait for and clear the welcome message
        self.tn.read_until(b"Welcome to use matrix control system!")
        self.tn.write(b"\r\n")
        # Clear any remaining data in the buffer
        self.tn.read_very_eager()

        # Update system status on connection
        self.get_version()
        self.get_ip_address()

        print("Connected to MX0808-1023")

    def disconnect(self):
        self.tn.close()
        print("Disconnected from MX0808-1023")

    def send_command(self, command: str, delay: float = 0.1):
        if self.tn is None:
            self.connect()
        # Send command with <CR><LF> line ending
        self.tn.write(command.encode("utf-8") + b"\r\n")
        sleep(delay)
        # Read and decode the response
        response = self.tn.read_very_eager().decode("utf-8").strip()
        return response

    def get_version(self):
        """Get firmware version of the device"""
        response = self.send_command("get ver")

        # Check if response is empty or invalid
        parts = response.strip().split()
        if len(parts) < 2:
            if self.debug:
                print(f"Warning: Invalid response for version: {response}")
            version = "unknown"  # Default version
        else:
            # Remove "VER " prefix and store just the version number
            version = response.replace("VER ", "").strip()

        # Update status
        self.status["system"]["version"] = version
        return version

    def get_ip_address(self):
        """Get current IP address of the device

        Returns:
            str: IP address
        """
        # Store the IP address used for connection in status
        self.status["system"]["ip_address"] = self.ip_address

        return self.ip_address

    def set_switch(self, input: int, output: int):
        """Switch input to output
        Parameters:
            input: int, 1-8 (or 0 for no input)
            output: int, 1-8
        """
        if not (0 <= input <= 8 and 1 <= output <= 8):
            raise ValueError("Input must be 0-8, Output must be 1-8")

        command = f"set sw in{input} out{output}"
        response = self.send_command(command)

        # Update status
        self.status["video"]["outputs"][f"Output {output}"] = input

        return response

    def set_switch_all(self, input: int):
        """Switch input to all outputs"""
        if not (0 <= input <= 8):
            raise ValueError("Input must be 0-8")

        command = f"set sw in{input} all"
        response = self.send_command(command)

        # Update status - all outputs now show this input
        for output in range(1, 9):
            self.status["video"]["outputs"][f"Output {output}"] = input

        return response

    def get_output_status(self, output: int):
        """Get status of output"""
        if not (1 <= output <= 8):
            raise ValueError("Output must be 1-8")

        command = f"get mp out{output}"
        response = self.send_command(command)

        # Check if response is empty or invalid
        parts = response.strip().split()
        if len(parts) < 3:
            if self.debug:
                print(f"Warning: Invalid response for output status: {response}")
            input_num = 0  # Default to no input
        else:
            # Parse "MP IN1 OUT3" format
            input_num = int(parts[1][2:])  # Extract number from "IN1"

        # Update status
        self.status["video"]["outputs"][f"Output {output}"] = input_num
        return input_num

    def get_output_all(self):
        """Get status of all outputs"""
        command = "get mp all"
        response = self.send_command(command)

        output_map = {}
        for line in response.split("\n"):
            if line.strip():
                parts = line.strip().split()
                if len(parts) >= 3:
                    try:
                        input_num = int(parts[1][2:])  # Extract number from "IN1"
                        output_num = int(parts[2][3:])  # Extract number from "OUT3"
                        output_map[f"Output {output_num}"] = input_num
                    except (ValueError, IndexError):
                        if self.debug:
                            print(
                                f"Warning: Invalid line in output status response: {line}"
                            )
                        continue

        # If no valid data was parsed, provide defaults
        if not output_map:
            if self.debug:
                print(
                    f"Warning: No valid output mappings found in response: {response}"
                )
            # Default to no input (0) for all outputs
            output_map = {f"Output {i}": 0 for i in range(1, 9)}

        # Update status
        self.status["video"]["outputs"] = output_map
        return output_map

    def set_audio_mode(self, mode: str = "follow"):
        """Set audio switch mode"""
        valid_modes = ["independent", "follow"]
        if mode.lower() not in valid_modes:
            raise ValueError("Mode must be either 'independent' or 'follow'")

        command = f"set audiosw_m {mode.lower()}"
        response = self.send_command(command)

        # Update status
        self.status["audio"]["mode"] = mode.lower()

        return response

    def get_audio_mode(self) -> str:
        response = self.send_command("get audiosw_m")

        # Check if response is empty or invalid
        parts = response.strip().split()
        if len(parts) < 2:
            if self.debug:
                print(f"Warning: Invalid response for audio mode: {response}")
            mode = "follow"  # Default to follow mode
        else:
            mode = parts[-1].lower()

        # Update status
        self.status["audio"]["mode"] = mode
        return mode

    def set_audio_switch(self, input: int, output: int | str):
        """Switch audio input to output. Automatically sets audio mode to independent."""
        # Validate input
        if not (0 <= input <= 8):
            raise ValueError("Input must be 0-8")

        # Validate output
        if isinstance(output, int) and not (1 <= output <= 4):
            raise ValueError("Output must be 1-4 or 'all'")
        elif isinstance(output, str) and output.lower() != "all":
            raise ValueError("Output string must be 'all'")

        # Ensure we're in independent mode
        current_mode = self.get_audio_mode()
        if current_mode != "independent":
            response = self.set_audio_mode("independent")
            if "ERROR" in response:
                raise ValueError("Failed to set independent audio mode")

        # Format the output parameter
        if isinstance(output, int):
            out_param = f"lineout{output}"
        else:
            out_param = output.lower()

        # Send the command
        command = f"set audiosw in{input} {out_param}"
        response = self.send_command(command)

        # Update status
        if isinstance(output, int):
            self.status["audio"]["outputs"][f"Audio Output {output}"] = input
        else:  # 'all' case
            for out_num in range(1, 5):  # Audio outputs 1-4
                self.status["audio"]["outputs"][f"Audio Output {out_num}"] = input

        return response

    def get_audio_status(self, output: int | str = "all"):
        """Get audio mapping status for specified output or all outputs"""
        # Validate output
        if isinstance(output, int) and not (1 <= output <= 4):
            raise ValueError("Output must be 1-4 or 'all'")
        elif isinstance(output, str) and output.lower() != "all":
            raise ValueError("Output string must be 'all'")

        if isinstance(output, int):
            command = f"get audiomp lineout{output}"
            response = self.send_command(command)

            # Check if response is empty or invalid
            parts = response.strip().split()
            if len(parts) < 3:
                if self.debug:
                    print(f"Warning: Invalid response for audio mapping: {response}")
                input_num = 0  # Default to no input
            else:
                # Parse "AUDIOMP IN1 LINEOUT3" format
                input_num = int(parts[1][2:])  # Extract number from "IN1"

            # Update status for this output
            self.status["audio"]["outputs"][f"Audio Output {output}"] = input_num
            return input_num

        else:  # 'all' case
            command = "get audiomp all"
            response = self.send_command(command)

            output_map = {}
            for line in response.split("\n"):
                if line.strip():
                    parts = line.strip().split()
                    if len(parts) >= 3:
                        try:
                            input_num = int(parts[1][2:])  # Extract number from "IN1"
                            output_num = int(
                                parts[2][7:]
                            )  # Extract number from "LINEOUT3"
                            output_map[f"Audio Output {output_num}"] = input_num
                        except (ValueError, IndexError):
                            if self.debug:
                                print(
                                    f"Warning: Invalid line in audio mapping response: {line}"
                                )
                            continue

            # Update status
            self.status["audio"]["outputs"].update(output_map)
            return output_map

    def set_volume(self, output: int, volume: int):
        """Set volume gain for specified audio output"""
        # Validate output
        if not (1 <= output <= 4):
            raise ValueError("Output must be 1-4")

        # Validate volume
        if not (-100 <= volume <= 0):
            raise ValueError("Volume must be between -100 and 0")

        command = f"set volgain_data lineout{output} {volume}"
        response = self.send_command(command)

        # Update status
        self.status["audio"]["volume_levels"][f"Output {output}"] = volume

        return response

    def get_volume(self, output: int):
        """Get volume gain level for specified audio output"""
        if not (1 <= output <= 4):
            raise ValueError("Output must be 1-4")

        command = f"get volgain_data lineout{output}"
        response = self.send_command(command)

        # Check if response is empty or invalid
        parts = response.strip().split()
        if len(parts) < 3:
            if self.debug:
                print(f"Warning: Invalid response for volume: {response}")
            volume = 0  # Default to 0dB
        else:
            try:
                volume = int(parts[-1])
            except ValueError:
                if self.debug:
                    print(f"Warning: Invalid volume value: {parts[-1]}")
                volume = 0

        # Update status
        self.status["audio"]["volume_levels"][f"Output {output}"] = volume
        return volume

    def set_audio_mute(self, output: int, mute: bool):
        """Set mute state for specified audio output"""
        # Validate output
        if not (1 <= output <= 4):
            raise ValueError("Output must be 1-4")

        # Convert boolean to on/off string
        mute_state = "on" if mute else "off"

        command = f"set audio_mute lineout{output} {mute_state}"
        response = self.send_command(command)

        # Update status
        self.status["audio"]["mute_states"][f"Output {output}"] = mute

        return response

    def get_audio_mute(self, output: int) -> bool:
        """Get mute state for specified audio output"""
        if not (1 <= output <= 4):
            raise ValueError("Output must be 1-4")

        command = f"get audio_mute lineout{output}"
        response = self.send_command(command)

        # Check if response is empty or invalid
        parts = response.strip().split()
        if len(parts) < 3:
            if self.debug:
                print(f"Warning: Invalid response for audio mute: {response}")
            mute_state = False  # Default to unmuted
        else:
            mute_state = parts[-1].lower() == "on"

        # Update status
        self.status["audio"]["mute_states"][f"Output {output}"] = mute_state
        return mute_state

    def set_cec_power(self, output: int | str, power: bool):
        """Set CEC power state for specified output"""
        # Validate output
        if isinstance(output, int) and not (1 <= output <= 8):
            raise ValueError("Output must be 1-8 or 'all'")
        elif isinstance(output, str) and output.lower() != "all":
            raise ValueError("Output string must be 'all'")

        # Convert boolean to on/off string
        power_state = "on" if power else "off"

        # Format output parameter
        out_param = "all" if isinstance(output, str) else f"out{output}"

        command = f"set cec_pwr {out_param} {power_state}"
        response = self.send_command(command)

        # Update status
        if isinstance(output, int):
            self.status["cec"]["power_states"][f"Output {output}"] = power
        else:  # 'all' case
            for out_num in range(1, 9):
                self.status["cec"]["power_states"][f"Output {out_num}"] = power

        return response

    def set_auto_cec(self, output: int | str, enabled: bool):
        """Set Auto CEC function state for specified output"""
        # Validate output
        if isinstance(output, int) and not (1 <= output <= 8):
            raise ValueError("Output must be 1-8 or 'all'")
        elif isinstance(output, str) and output.lower() != "all":
            raise ValueError("Output string must be 'all'")

        # Convert boolean to on/off string
        state = "on" if enabled else "off"

        # Format output parameter
        out_param = "all" if isinstance(output, str) else f"out{output}"

        command = f"set autocec_fn {out_param} {state}"
        response = self.send_command(command)

        # Update status
        if isinstance(output, int):
            self.status["cec"]["auto_states"][f"Output {output}"] = enabled
        else:  # 'all' case
            for out_num in range(1, 9):
                self.status["cec"]["auto_states"][f"Output {out_num}"] = enabled

        return response

    def get_auto_cec(self, output: int) -> bool:
        """Get Auto CEC function state for specified output"""
        # Validate output
        if not (1 <= output <= 8):
            raise ValueError("Output must be 1-8")

        command = f"get autocec_fn out{output}"
        response = self.send_command(command)

        # Check if response is empty or invalid
        parts = response.strip().split()
        if len(parts) < 3:
            # Handle error case - assume CEC is off if we can't get status
            auto_cec_state = False
            if self.debug:
                print(f"Warning: Invalid response for auto CEC status: {response}")
        else:
            # Parse "AUTOCEC_FN OUT1 on" format
            auto_cec_state = parts[-1].lower() == "on"

        # Update status
        self.status["cec"]["auto_states"][f"Output {output}"] = auto_cec_state
        return auto_cec_state

    def set_auto_cec_delay(self, output: int | str, delay: int):
        """Set Auto CEC power delay timing for specified output"""
        # Validate output
        if isinstance(output, int) and not (1 <= output <= 8):
            raise ValueError("Output must be 1-8 or 'all'")
        elif isinstance(output, str) and output.lower() != "all":
            raise ValueError("Output string must be 'all'")

        # Validate delay
        if not (0 <= delay <= 30):
            raise ValueError("Delay must be between 0 and 30 minutes")

        # Format output parameter
        out_param = "all" if isinstance(output, str) else f"out{output}"

        command = f"set autocec_d {out_param} {delay}"
        response = self.send_command(command)

        # Update status
        if isinstance(output, int):
            self.status["cec"]["auto_delays"][f"Output {output}"] = delay
        else:  # 'all' case
            for out_num in range(1, 9):
                self.status["cec"]["auto_delays"][f"Output {out_num}"] = delay

        return response

    def get_auto_cec_delay(self, output: int | str = "all"):
        """Get Auto CEC power delay timing for specified output"""
        # Validate output
        if isinstance(output, int) and not (1 <= output <= 8):
            raise ValueError("Output must be 1-8 or 'all'")
        elif isinstance(output, str) and output.lower() != "all":
            raise ValueError("Output string must be 'all'")

        if isinstance(output, int):
            command = f"get autocec_d out{output}"
            response = self.send_command(command)

            # Check if response is empty or invalid
            parts = response.strip().split()
            if len(parts) < 3:
                if self.debug:
                    print(f"Warning: Invalid response for CEC delay: {response}")
                delay = 0  # Default to no delay
            else:
                try:
                    delay = int(parts[-1])
                except ValueError:
                    if self.debug:
                        print(f"Warning: Invalid delay value: {parts[-1]}")
                    delay = 0

            # Update status
            self.status["cec"]["auto_delays"][f"Output {output}"] = delay
            return delay

        else:  # 'all' case
            command = "get autocec_d all"
            response = self.send_command(command)

            delay_map = {}
            for line in response.split("\n"):
                if line.strip():
                    parts = line.strip().split()
                    if len(parts) >= 3:
                        try:
                            output_num = int(parts[1][3:])  # Extract number from "OUT1"
                            delay = int(parts[2])
                            delay_map[f"Output {output_num}"] = delay
                        except (ValueError, IndexError):
                            if self.debug:
                                print(
                                    f"Warning: Invalid line in CEC delay response: {line}"
                                )
                            continue

            # Update status
            self.status["cec"]["auto_delays"].update(delay_map)
            return delay_map

    def set_cec_command(self, output: int | str, command_type: str, hex_string: str):
        """Set custom CEC command for power on/off events"""
        # Validate output
        if isinstance(output, int) and not (1 <= output <= 8):
            raise ValueError("Output must be 1-8 or 'all'")
        elif isinstance(output, str) and output.lower() != "all":
            raise ValueError("Output string must be 'all'")

        # Validate command type
        if command_type.lower() not in ["pwron", "pwroff"]:
            raise ValueError("Command type must be 'pwron' or 'pwroff'")

        # Validate hex string
        try:
            hex_bytes = bytes.fromhex(hex_string.replace("0x", ""))
            if len(hex_bytes) > 16:
                raise ValueError("Hex string must not exceed 16 bytes in length")
        except ValueError as e:
            raise ValueError(f"Invalid hex string: {e}")

        # Format output parameter
        out_param = "all" if isinstance(output, str) else f"out{output}"

        command = f"set ceccmd_edit {out_param} {command_type.lower()} {hex_string}"
        response = self.send_command(command)

        # Update status
        if isinstance(output, int):
            if f"Output {output}" not in self.status["cec"]["commands"]:
                self.status["cec"]["commands"][f"Output {output}"] = {}
            self.status["cec"]["commands"][f"Output {output}"][command_type.lower()] = (
                hex_string
            )
        else:  # 'all' case
            for out_num in range(1, 9):
                if f"Output {out_num}" not in self.status["cec"]["commands"]:
                    self.status["cec"]["commands"][f"Output {out_num}"] = {}
                self.status["cec"]["commands"][f"Output {out_num}"][
                    command_type.lower()
                ] = hex_string

        return response

    def get_cec_command(self, output: int | str, command_type: str):
        """Get custom CEC command for power on/off events"""
        # Validate output
        if isinstance(output, int) and not (1 <= output <= 8):
            raise ValueError("Output must be 1-8 or 'all'")
        elif isinstance(output, str) and output.lower() != "all":
            raise ValueError("Output string must be 'all'")

        # Validate command type
        if command_type.lower() not in ["pwron", "pwroff"]:
            raise ValueError("Command type must be 'pwron' or 'pwroff'")

        if isinstance(output, int):
            command = f"get ceccmd_edit out{output} {command_type.lower()}"
            response = self.send_command(command)

            # Check if response is empty or invalid
            parts = response.strip().split()
            if len(parts) < 4:
                if self.debug:
                    print(f"Warning: Invalid response for CEC command: {response}")
                hex_command = "00"  # Default to empty command
            else:
                hex_command = parts[-1]

            # Update status
            if f"Output {output}" not in self.status["cec"]["commands"]:
                self.status["cec"]["commands"][f"Output {output}"] = {}
            self.status["cec"]["commands"][f"Output {output}"][command_type.lower()] = (
                hex_command
            )
            return hex_command

        else:  # 'all' case
            command = f"get ceccmd_edit all {command_type.lower()}"
            response = self.send_command(command)

            command_map = {}
            for line in response.split("\n"):
                if line.strip():
                    parts = line.strip().split()
                    if len(parts) >= 4:
                        try:
                            output_num = int(parts[1][3:])  # Extract number from "OUT1"
                            hex_command = parts[3]
                            if (
                                f"Output {output_num}"
                                not in self.status["cec"]["commands"]
                            ):
                                self.status["cec"]["commands"][
                                    f"Output {output_num}"
                                ] = {}
                            self.status["cec"]["commands"][f"Output {output_num}"][
                                command_type.lower()
                            ] = hex_command
                            command_map[f"Output {output_num}"] = hex_command
                        except (ValueError, IndexError):
                            if self.debug:
                                print(
                                    f"Warning: Invalid line in CEC command response: {line}"
                                )
                            continue

            return command_map

    def send_cec_command(self, output: int | str, hex_string: str):
        """Send custom CEC command to specified output

        Parameters:
            output: int 1-8 for specific output, or 'all' for all outputs
            hex_string: str, hexadecimal command string (max 16 bytes)

        Returns:
            str: Response from device

        Raises:
            ValueError: If output value is invalid
            ValueError: If hex_string is invalid or too long
        """
        # Validate output
        if isinstance(output, int) and not (1 <= output <= 8):
            raise ValueError("Output must be 1-8 or 'all'")
        elif isinstance(output, str) and output.lower() != "all":
            raise ValueError("Output string must be 'all'")

        # Validate hex string
        try:
            # Try to convert to bytes to validate hex string
            hex_bytes = bytes.fromhex(hex_string.replace("0x", ""))
            if len(hex_bytes) > 16:
                raise ValueError("Hex string must not exceed 16 bytes in length")
        except ValueError as e:
            raise ValueError(f"Invalid hex string: {e}")

        # Format output parameter
        out_param = "all" if isinstance(output, str) else f"out{output}"

        command = f"set cec_cmd {out_param} {hex_string}"
        return self.send_command(command)

    def set_hdcp_support(self, input: int, enabled: bool):
        """Set HDCP support for specified input

        Parameters:
            input: int 2-8 (note: input 1 not supported)
            enabled: bool, True to enable HDCP support, False to disable

        Returns:
            str: Response from device

        Raises:
            ValueError: If input value is invalid
        """
        # Validate input (note: input 1 is not supported for HDCP)
        if not (2 <= input <= 8):
            raise ValueError("Input must be 2-8")

        # Convert boolean to on/off string
        state = "on" if enabled else "off"

        command = f"set hdcp_s in{input} {state}"
        response = self.send_command(command)

        # Update status
        self.status["hdcp"]["support"][f"Input {input}"] = enabled

        return response

    def get_hdcp_support(self, input: int) -> bool:
        """Get HDCP support status for specified input"""
        # Validate input (note: input 1 is not supported for HDCP)
        if not (2 <= input <= 8):
            raise ValueError("Input must be 2-8")

        command = f"get hdcp_s in{input}"
        response = self.send_command(command)

        # Check if response is empty or invalid
        parts = response.strip().split()
        if len(parts) < 3:
            if self.debug:
                print(f"Warning: Invalid response for HDCP support: {response}")
            hdcp_state = False  # Default to disabled
        else:
            hdcp_state = parts[-1].lower() == "on"

        # Update status
        self.status["hdcp"]["support"][f"Input {input}"] = hdcp_state
        return hdcp_state

    def set_hdcp_mode(self, output: int | str, mode: str):
        """Set HDCP mode for specified output

        Parameters:
            output: int 1-8 for specific output, or 'all' for all outputs
            mode: str, either:
                 'auto': Automatically adapt HDCP encryption based on received video
                 'hdcp1.x': Force HDCP 1.x encryption

        Returns:
            str: Response from device

        Raises:
            ValueError: If output value is invalid
            ValueError: If mode is invalid
        """
        # Validate output
        if isinstance(output, int) and not (1 <= output <= 8):
            raise ValueError("Output must be 1-8 or 'all'")
        elif isinstance(output, str) and output.lower() != "all":
            raise ValueError("Output string must be 'all'")

        # Validate mode
        valid_modes = ["auto", "hdcp1.x"]
        if mode.lower() not in valid_modes:
            raise ValueError("Mode must be either 'auto' or 'hdcp1.x'")

        # Format output parameter
        out_param = "all" if isinstance(output, str) else f"out{output}"

        command = f"set hdcp {out_param} {mode.lower()}"
        response = self.send_command(command)

        # Update status
        if isinstance(output, int):
            self.status["hdcp"]["modes"][f"Output {output}"] = mode.lower()
        else:  # 'all' case
            for out_num in range(1, 9):
                self.status["hdcp"]["modes"][f"Output {out_num}"] = mode.lower()

        return response

    def get_hdcp_mode(self, output: int | str = "all"):
        """Get HDCP mode for specified output"""
        # Validate output
        if isinstance(output, int) and not (1 <= output <= 8):
            raise ValueError("Output must be 1-8 or 'all'")
        elif isinstance(output, str) and output.lower() != "all":
            raise ValueError("Output string must be 'all'")

        if isinstance(output, int):
            command = f"get hdcp out{output}"
            response = self.send_command(command)

            # Check if response is empty or invalid
            parts = response.strip().split()
            if len(parts) < 3:
                if self.debug:
                    print(f"Warning: Invalid response for HDCP mode: {response}")
                mode = "auto"  # Default to auto mode
            else:
                mode = parts[-1].lower()

            # Update status
            self.status["hdcp"]["modes"][f"Output {output}"] = mode
            return mode

        else:  # 'all' case
            command = "get hdcp all"
            response = self.send_command(command)

            mode_map = {}
            for line in response.split("\n"):
                if line.strip():
                    parts = line.strip().split()
                    if len(parts) >= 3:
                        try:
                            output_num = int(parts[1][3:])  # Extract number from "OUT1"
                            mode = parts[2].lower()
                            mode_map[f"Output {output_num}"] = mode
                        except (ValueError, IndexError):
                            if self.debug:
                                print(
                                    f"Warning: Invalid line in HDCP mode response: {line}"
                                )
                            continue

            # Update status
            self.status["hdcp"]["modes"].update(mode_map)
            return mode_map

    def set_edid(self, input: int, edid_setting: int):
        """Set EDID for specified input

        Parameters:
            input: int 1-8 for specific input
            edid_setting: int 1-30, where:
                1-8: Copy from HDMI output 1-8
                9: Fixed 4K60 2.0CH PCM Audio with HDR
                10: Fixed 4K60 2.0CH PCM Audio with SDR
                11: Fixed 4K30 2.0CH PCM Audio with HDR
                12: Fixed 4K30 2.0CH PCM Audio with SDR
                13: Fixed 1080p@60Hz 2.0CH PCM Audio with HDR
                14: Fixed 1080p@60Hz 2.0CH PCM Audio with SDR
                15-30: Additional EDID settings if available

        Returns:
            str: Response from device

        Raises:
            ValueError: If input or edid_setting values are invalid
        """
        # Validate input
        if not (1 <= input <= 8):
            raise ValueError("Input must be 1-8")

        # Validate EDID setting
        if not (1 <= edid_setting <= 30):
            raise ValueError("EDID setting must be 1-30")

        command = f"set edid in{input} {edid_setting}"
        return self.send_command(command)

    def get_edid(self) -> dict:
        """Get EDID settings for all inputs"""
        command = "get edid all"
        response = self.send_command(command)

        edid_map = {}
        for line in response.split("\n"):
            if line.strip():
                parts = line.strip().split()
                if len(parts) >= 3:
                    try:
                        input_num = int(parts[1][2:])  # Extract number from "IN1"
                        edid_setting = int(parts[2])
                        edid_map[f"Input {input_num}"] = edid_setting
                    except (ValueError, IndexError):
                        if self.debug:
                            print(f"Warning: Invalid line in EDID response: {line}")
                        continue

        # If no valid data was parsed, provide defaults
        if not edid_map:
            if self.debug:
                print(f"Warning: No valid EDID settings found in response: {response}")
            # Default to Auto EDID for all inputs
            edid_map = {f"Input {i}": 0 for i in range(1, 9)}

        # Update status - store in edid section
        self.status["edid"]["settings"] = edid_map
        return edid_map

    def get_edid_input(self, input: int) -> int:
        """Get EDID setting for specified input

        Parameters:
            input: int 1-8 for specific input

        Returns:
            int: EDID setting number, where:
                1-8: Copy from HDMI output 1-8
                9: Fixed 4K60 2.0CH PCM Audio with HDR
                10: Fixed 4K60 2.0CH PCM Audio with SDR
                11: Fixed 4K30 2.0CH PCM Audio with HDR
                12: Fixed 4K30 2.0CH PCM Audio with SDR
                13: Fixed 1080p@60Hz 2.0CH PCM Audio with HDR
                14: Fixed 1080p@60Hz 2.0CH PCM Audio with SDR
                15-30: Additional EDID settings if available

        Raises:
            ValueError: If input value is invalid
        """
        # Validate input
        if not (1 <= input <= 8):
            raise ValueError("Input must be 1-8")

        command = f"get edid in{input}"
        response = self.send_command(command)

        # Parse "EDID IN1 5" format
        edid_setting = int(response.split()[-1])

        # Update status
        if "edid_settings" not in self.status:
            self.status["edid_settings"] = {}
        self.status["edid_settings"][f"Input {input}"] = edid_setting

        return edid_setting

    def write_edid(self, input: int, block: str, edid_data: bytes) -> bool:
        """Write custom EDID data to specified input

        Parameters:
            input: int 1-8 for specific input
            block: str, either 'block0' or 'block1'
            edid_data: bytes, exactly 256 bytes of EDID data

        Returns:
            bool: True if write was successful, False if checksum error

        Raises:
            ValueError: If input value is invalid
            ValueError: If block is invalid
            ValueError: If EDID data is not exactly 256 bytes
        """
        # Validate input
        if not (1 <= input <= 8):
            raise ValueError("Input must be 1-8")

        # Validate block
        if block.lower() not in ["block0", "block1"]:
            raise ValueError("Block must be 'block0' or 'block1'")

        # Validate EDID data length
        if len(edid_data) != 256:
            raise ValueError("EDID data must be exactly 256 bytes")

        # Convert bytes to space-separated ASCII hex string
        hex_str = " ".join(f"{b:02X}" for b in edid_data)

        command = f"set edid_w in{input} {block.lower()} {hex_str}"
        response = self.send_command(command)

        # Check if write was successful
        success = response.split()[-1].lower() == "ok"

        # Update status
        if "edid_write_status" not in self.status:
            self.status["edid_write_status"] = {}
        if input not in self.status["edid_write_status"]:
            self.status["edid_write_status"][input] = {}
        self.status["edid_write_status"][input][block.lower()] = success

        return success

    def read_edid(self, output: int, block: str) -> bytes | None:
        """Read EDID data from specified output"""
        # Validate output
        if not (1 <= output <= 8):
            raise ValueError("Output must be 1-8")

        # Validate block
        if block.lower() not in ["block0", "block1"]:
            raise ValueError("Block must be 'block0' or 'block1'")

        command = f"get edid_r out{output}"
        response = self.send_command(command)

        # Initialize status dictionaries
        if str(output) not in self.status["edid"]["read_status"]:
            self.status["edid"]["read_status"][str(output)] = {}
        if str(output) not in self.status["edid"]["data"]:
            self.status["edid"]["data"][str(output)] = {}

        # Handle unconnected outputs
        if "UNCONNECT" in response:
            self.status["edid"]["read_status"][str(output)][block.lower()] = "unconnect"
            return None

        # Parse EDID data from response
        blocks = {}
        current_data = ""

        for line in response.split("\n"):
            if not line.strip():
                continue

            if line.startswith("EDID_R"):
                parts = line.strip().split()
                if len(parts) >= 4:
                    current_block = parts[2].lower()  # BLOCK0 or BLOCK1
                    # Concatenate all parts after the block identifier
                    current_data = "".join(parts[3:])
                    blocks[current_block] = current_data

        try:
            # Get the requested block's data
            if block.lower() not in blocks:
                if self.debug:
                    print(f"Warning: Requested block {block} not found in EDID data")
                self.status["edid"]["read_status"][str(output)][block.lower()] = "error"
                return None

            edid_data = blocks[block.lower()]

            # Convert hex string to bytes
            hex_pairs = [edid_data[i : i + 2] for i in range(0, len(edid_data), 2)]
            edid_bytes = bytes(int(pair, 16) for pair in hex_pairs)

            if len(edid_bytes) == 128:  # Valid EDID block size
                self.status["edid"]["read_status"][str(output)][block.lower()] = "ok"
                # Store as hex string instead of bytes for better serialization
                self.status["edid"]["data"][str(output)][block.lower()] = (
                    edid_bytes.hex()
                )
                if self.debug:
                    print(f"Successfully read EDID {block} from output {output}")
                return edid_bytes
            else:
                if self.debug:
                    print(
                        f"Warning: Invalid EDID data length for output {output}: {len(edid_bytes)}"
                    )
                self.status["edid"]["read_status"][str(output)][block.lower()] = "error"
                return None

        except (ValueError, IndexError) as e:
            if self.debug:
                print(f"Warning: Error parsing EDID data for output {output}: {e}")
            self.status["edid"]["read_status"][str(output)][block.lower()] = "error"
            return None

    def reset(self):
        """Reset the device to factory defaults

        Returns:
            str: Response from device

        Note:
            This will reset all settings to factory defaults.
            The connection will likely be dropped and need to be re-established.
        """
        response = self.send_command("reset")

        # Clear the status dictionary since device is reset
        self.status = {"version": None, "audio_mode": None, "outputs": {}}

        # Close the connection as it will likely be dropped
        if self.tn:
            self.disconnect()

        return response

    def reboot(self):
        """Reboot the device

        Returns:
            str: Response from device

        Note:
            This will cause the device to restart.
            The connection will be dropped and need to be re-established.
        """
        response = self.send_command("reboot")

        # Close the connection as device will reboot
        if self.tn:
            self.disconnect()

        return response

    def save_preset(self, preset_number: int):
        """Save current device configuration as a preset scene

        Parameters:
            preset_number: int 1-6 for preset slot

        Returns:
            str: Response from device

        Raises:
            ValueError: If preset_number is invalid

        Note:
            This saves the current configuration of all settings
            (routing, audio, EDID, etc.) to the specified preset slot.
        """
        # Validate preset number
        if not (1 <= preset_number <= 6):
            raise ValueError("Preset number must be 1-6")

        command = f"save preset {preset_number}"
        response = self.send_command(command)

        # Update status
        if "presets" not in self.status:
            self.status["presets"] = set()
        self.status["presets"].add(preset_number)

        return response

    def restore_preset(self, preset_number: int):
        """Restore device configuration from a preset scene

        Parameters:
            preset_number: int 1-6 for preset slot

        Returns:
            str: Response from device

        Raises:
            ValueError: If preset_number is invalid

        Note:
            This restores all settings (routing, audio, EDID, etc.)
            from the specified preset slot. The status dictionary
            will be cleared as device state may change significantly.
        """
        # Validate preset number
        if not (1 <= preset_number <= 6):
            raise ValueError("Preset number must be 1-6")

        command = f"restore preset {preset_number}"
        response = self.send_command(command)

        # Clear status dictionary since device state will change
        # Keep only the presets set and version information
        presets = self.status.get("presets", set())
        version = self.status.get("version")
        self.status = {"version": version, "presets": presets, "outputs": {}}

        return response

    def set_output_resolution(self, output: int, resolution: str):
        """Set video output resolution for specified output

        Parameters:
            output: int 1-8 for specific output
            resolution: str, one of:
                'AUTO'
                '3840x2160@60'
                '3840x2160@50'
                '3840x2160@30'
                '3840x2160@25'
                '3840x2160@24'
                '1920x1200@60'
                '1920x1080@60'
                '1920x1080@50'
                '1680x1050@60'
                '1600x1200@60'
                '1600x900@60'
                '1440x900@60'
                '1366x768@60'
                '1360x768@60'
                '1280x1024@60'
                '1280x960@60'
                '1280x800@60'
                '1280x768@60'
                '1280x720@60'
                '1280x720@50'
                '1024x768@60'
                '800x600@60'

        Returns:
            str: Response from device

        Raises:
            ValueError: If output value is invalid
            ValueError: If resolution is invalid
            RuntimeError: If scaler is not in manual mode
        """
        # Validate output
        if not (1 <= output <= 8):
            raise ValueError("Output must be 1-8")

        # List of valid resolutions
        valid_resolutions = {
            "AUTO",
            "3840x2160@60",
            "3840x2160@50",
            "3840x2160@30",
            "3840x2160@25",
            "3840x2160@24",
            "1920x1200@60",
            "1920x1080@60",
            "1920x1080@50",
            "1680x1050@60",
            "1600x1200@60",
            "1600x900@60",
            "1440x900@60",
            "1366x768@60",
            "1360x768@60",
            "1280x1024@60",
            "1280x960@60",
            "1280x800@60",
            "1280x768@60",
            "1280x720@60",
            "1280x720@50",
            "1024x768@60",
            "800x600@60",
        }

        # Validate resolution
        if resolution.upper() not in valid_resolutions:
            raise ValueError(
                f"Invalid resolution. Must be one of: {', '.join(sorted(valid_resolutions))}"
            )

        command = f"set vidout_res out{output} {resolution.upper()}"
        response = self.send_command(command)

        # Check if command was rejected due to scaler mode
        if "ERROR" in response:
            raise RuntimeError(
                "Failed to set resolution. Ensure scaler is in manual mode."
            )

        # Update status
        self.status["resolution"]["outputs"][f"Output {output}"] = resolution.upper()

        return response

    def get_output_resolution(self, output: int) -> str:
        """Get current video output resolution for specified output"""
        # Validate output
        if not (1 <= output <= 8):
            raise ValueError("Output must be 1-8")

        command = f"get vidout_res out{output}"
        response = self.send_command(command)

        # Check if response is empty or invalid
        parts = response.strip().split()
        if len(parts) < 3:
            if self.debug:
                print(f"Warning: Invalid response for resolution: {response}")
            resolution = "AUTO"  # Default to auto resolution
        else:
            resolution = parts[-1].upper()

        # Check if command was rejected due to scaler mode
        if "ERROR" in response:
            raise RuntimeError(
                "Failed to get resolution. Ensure scaler is in manual mode."
            )

        # Update status
        self.status["resolution"]["outputs"][f"Output {output}"] = resolution
        return resolution

    def set_https(self, enabled: bool):
        """Enable or disable HTTPS for web interface

        Parameters:
            enabled: bool, True to enable HTTPS, False to disable

        Returns:
            str: Response from device

        Note:
            Changes to HTTPS settings may require device reboot
            to take effect.
        """
        # Convert boolean to on/off string
        state = "on" if enabled else "off"

        command = f"set https {state}"
        response = self.send_command(command)

        # Update status
        self.status["security"]["https_enabled"] = enabled

        return response

    def get_https(self) -> bool:
        """Get current HTTPS status for web interface"""
        response = self.send_command("get https")

        # Check if response is empty or invalid
        parts = response.strip().split()
        if len(parts) < 2:
            if self.debug:
                print(f"Warning: Invalid response for HTTPS status: {response}")
            https_enabled = False  # Default to disabled
        else:
            https_enabled = parts[-1].lower() == "on"

        # Update status
        self.status["security"]["https_enabled"] = https_enabled
        return https_enabled

    def set_telnet_tls(self, enabled: bool):
        """Enable or disable Telnet-TLS (secure telnet)

        Parameters:
            enabled: bool, True to enable Telnet-TLS, False to use standard Telnet

        Returns:
            str: Response from device

        Note:
            Changes to Telnet-TLS settings may require device reboot
            and reconnection with appropriate security settings.
            When enabled, connections must use TLS encryption.
        """
        # Convert boolean to on/off string
        state = "on" if enabled else "off"

        command = f"set telnets {state}"
        response = self.send_command(command)

        # Update status
        self.status["security"]["telnet_tls_enabled"] = enabled

        return response

    def get_telnet_tls(self) -> bool:
        """Get current Telnet-TLS status"""
        response = self.send_command("get telnets")

        # Check if response is empty or invalid
        parts = response.strip().split()
        if len(parts) < 2:
            if self.debug:
                print(f"Warning: Invalid response for Telnet-TLS status: {response}")
            tls_enabled = False  # Default to disabled
        else:
            tls_enabled = parts[-1].lower() == "on"

        # Update status
        self.status["security"]["telnet_tls_enabled"] = tls_enabled
        return tls_enabled

    def set_telnet_password(self, old_password: str, new_password: str) -> bool:
        """Change the Telnet/Telnet-TLS password

        Parameters:
            old_password: str, current password (4-16 alphanumeric chars)
            new_password: str, new password (4-16 alphanumeric chars)

        Returns:
            bool: True if password change successful, False if failed

        Raises:
            ValueError: If password length or characters are invalid

        Note:
            Passwords must be 4-16 characters long and contain only
            alphanumeric characters (A-Z, a-z, 0-9).
        """
        # Validate old password
        if not (4 <= len(old_password) <= 16):
            raise ValueError("Old password must be 4-16 characters long")
        if not old_password.isalnum():
            raise ValueError("Old password must contain only alphanumeric characters")

        # Validate new password
        if not (4 <= len(new_password) <= 16):
            raise ValueError("New password must be 4-16 characters long")
        if not new_password.isalnum():
            raise ValueError("New password must contain only alphanumeric characters")

        command = f"set tel_pwd {old_password} {new_password} {new_password}"
        response = self.send_command(command)

        # Parse "TEL_PWD 1" format for success
        success = response.split()[-1] == "1"

        # Update status
        self.status["security"]["last_password_change"] = {
            "success": success,
            "timestamp": time.time(),
        }

        return success

    def get_cec_power(self, output: int | str = "all") -> bool | dict:
        """Get CEC power state for specified output"""
        # Validate output
        if isinstance(output, int) and not (1 <= output <= 8):
            raise ValueError("Output must be 1-8 or 'all'")
        elif isinstance(output, str) and output.lower() != "all":
            raise ValueError("Output string must be 'all'")

        # Initialize power_states if it doesn't exist
        if "power_states" not in self.status["cec"]:
            self.status["cec"]["power_states"] = {}

        # Format and send command
        if isinstance(output, int):
            command = f"get cec_pwr out{output}"
            response = self.send_command(command)

            # Check if response is empty or invalid
            parts = response.strip().split()
            if len(parts) < 3:
                if self.debug:
                    print(f"Warning: Invalid response for CEC power: {response}")
                power_state = False  # Default to off
            else:
                power_state = parts[-1].lower() == "on"

            # Update status for this output
            self.status["cec"]["power_states"][f"Output {output}"] = power_state
            return power_state

        else:  # 'all' case
            command = "get cec_pwr all"
            response = self.send_command(command)

            power_map = {}
            for line in response.split("\n"):
                if line.strip():
                    parts = line.strip().split()
                    if len(parts) >= 3:
                        try:
                            output_num = int(parts[1][3:])  # Extract number from "OUT1"
                            power_state = parts[2].lower() == "on"
                            power_map[f"Output {output_num}"] = power_state
                        except (ValueError, IndexError):
                            if self.debug:
                                print(
                                    f"Warning: Invalid line in CEC power response: {line}"
                                )
                            continue

            # Update status with all power states
            self.status["cec"]["power_states"] = power_map

            # If no valid data was parsed, provide defaults
            if not power_map:
                if self.debug:
                    print(
                        f"Warning: No valid CEC power states found in response: {response}"
                    )
                # Default to off for all outputs
                power_map = {f"Output {i}": False for i in range(1, 9)}
                self.status["cec"]["power_states"] = power_map

            return power_map

    def get_presets(self) -> set:
        """Get list of saved preset slots

        Returns:
            set: Set of integers representing saved preset slots (1-6)
        """
        command = "get preset"
        response = self.send_command(command)

        saved_slots = set()
        for line in response.split("\n"):
            if line.strip():
                parts = line.strip().split()
                if len(parts) >= 2:
                    try:
                        preset_num = int(parts[1])
                        if 1 <= preset_num <= 6:
                            saved_slots.add(preset_num)
                    except ValueError:
                        if self.debug:
                            print(f"Warning: Invalid preset number in response: {line}")
                        continue

        # Update status
        self.status["presets"]["saved_slots"] = saved_slots
        return saved_slots


def test_device(mx):
    """Test all device functions and return status"""
    # Get Video status
    mx.get_output_all()

    # Get Audio status
    mx.get_audio_mode()
    mx.get_audio_status("all")
    for output in range(1, 5):  # Audio outputs 1-4
        mx.get_volume(output)
        mx.get_audio_mute(output)

    # Get CEC status
    for output in range(1, 9):  # Outputs 1-8
        mx.get_auto_cec(output)
        mx.get_auto_cec_delay(output)
        mx.get_cec_command(output, "pwron")
        mx.get_cec_command(output, "pwroff")
    # Add CEC power status query
    mx.get_cec_power("all")

    # Get HDCP status
    for input in range(2, 9):  # Inputs 2-8 (input 1 not supported)
        mx.get_hdcp_support(input)
    mx.get_hdcp_mode("all")

    # Get EDID status
    mx.get_edid()  # Get EDID settings
    # Try to read EDID data from connected outputs
    for output in range(1, 9):
        for block in ["block0", "block1"]:
            mx.read_edid(output, block)

    # Get Resolution status
    for output in range(1, 9):  # Outputs 1-8
        mx.get_output_resolution(output)

    # Get Security status
    mx.get_https()
    mx.get_telnet_tls()

    # Get Presets
    mx.get_presets()

    print("\nDevice Status:")
    print("=" * 50)

    # Create a copy of the status dict for display
    status_copy = mx.status.copy()

    # Format EDID data more compactly
    if "edid" in status_copy and "data" in status_copy["edid"]:
        for output in status_copy["edid"]["data"]:
            for block in list(status_copy["edid"]["data"][output].keys()):
                if isinstance(status_copy["edid"]["data"][output][block], str):
                    hex_str = status_copy["edid"]["data"][output][block]
                    status_copy["edid"]["data"][output][block] = (
                        f"{hex_str[:32]}...{hex_str[-32:]}"
                    )

    # Define sections that should be single-line
    single_line = [
        ("audio", "volume_levels"),
        ("audio", "mute_states"),
        ("audio", "outputs"),
        ("system", None),
        ("security", None),
        ("presets", None),
        ("hdcp", "support"),
    ]

    # Define sections that should be compacted but multi-line
    compact_multi = [
        ("video", "outputs"),
        ("cec", "auto_states"),
        ("cec", "auto_delays"),
        ("cec", "commands"),
        ("cec", "power_states"),
        ("hdcp", "modes"),
        ("resolution", "outputs"),
        ("edid", "settings"),
        ("edid", "read_status"),
    ]

    # Format single-line sections
    for section, subsection in single_line:
        if section in status_copy:
            if subsection and subsection in status_copy[section]:
                status_copy[section][subsection] = dict(
                    sorted(
                        status_copy[section][subsection].items(),
                        key=lambda x: int(x[0].split()[-1])
                        if x[0].split()[-1].isdigit()
                        else x[0],
                    )
                )
            elif not subsection:
                status_copy[section] = dict(sorted(status_copy[section].items()))

    # Format compact multi-line sections
    for section, subsection in compact_multi:
        if section in status_copy and subsection in status_copy[section]:
            status_copy[section][subsection] = dict(
                sorted(
                    status_copy[section][subsection].items(),
                    key=lambda x: int(x[0].split()[-1])
                    if x[0].split()[-1].isdigit()
                    else x[0],
                )
            )

    # Convert sets to lists and format output
    status_copy = json.loads(json.dumps(status_copy, default=list))

    # Custom PP formatter with specific width and compact settings
    pp = PrettyPrinter(indent=2, width=100, sort_dicts=False, compact=True)
    pp.pprint(status_copy)


def print_all_get_commands(mx):
    """Print responses from all get commands"""
    print("\nTesting all get commands:")
    print("=" * 50)

    # Video
    print("\nVideo:")
    print("get mp all:", mx.get_output_all())

    # Audio
    print("\nAudio:")
    print("get audiosw_m:", mx.get_audio_mode())
    print("get audiomp all:", mx.get_audio_status("all"))
    for output in range(1, 5):  # Audio outputs 1-4
        print(f"get volgain_data lineout{output}:", mx.get_volume(output))
        print(f"get audio_mute lineout{output}:", mx.get_audio_mute(output))

    # CEC
    print("\nCEC:")
    for output in range(1, 9):  # Outputs 1-8
        print(f"get autocec_fn out{output}:", mx.get_auto_cec(output))
        print(f"get autocec_d out{output}:", mx.get_auto_cec_delay(output))
        print(
            f"get ceccmd_edit out{output} pwron:", mx.get_cec_command(output, "pwron")
        )
        print(
            f"get ceccmd_edit out{output} pwroff:", mx.get_cec_command(output, "pwroff")
        )
    print("get cec_pwr all:", mx.get_cec_power("all"))

    # HDCP
    print("\nHDCP:")
    for input_num in range(2, 9):  # Inputs 2-8
        print(f"get hdcp_in{input_num}:", mx.get_hdcp_support(input_num))
    print("get hdcp_mode all:", mx.get_hdcp_mode("all"))

    # EDID
    print("\nEDID:")
    print("get edid:", mx.get_edid())
    # Try to read EDID data from connected outputs
    for output in range(1, 9):
        for block in ["block0", "block1"]:
            print(f"get edid_data out{output} {block}:", mx.read_edid(output, block))

    # Resolution
    print("\nResolution:")
    for output in range(1, 9):  # Outputs 1-8
        print(f"get vidout_res out{output}:", mx.get_output_resolution(output))

    # Security
    print("\nSecurity:")
    print("get https:", mx.get_https())
    print("get telnets:", mx.get_telnet_tls())


if __name__ == "__main__":
    IP = "10.0.50.6"
    mx = MX0808_1023(IP)
    print_all_get_commands(mx)
