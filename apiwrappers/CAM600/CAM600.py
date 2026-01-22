import telnetlib
import socket
import time
import logging


logger = logging.getLogger(__name__)


class CAM600_Device:
    def __init__(self, host, timeout=5, debug=False, max_retries=3):
        self.host = host
        self.timeout = timeout
        self.debug = debug
        self.tn = None
        self.max_retries = max_retries

    def _connect(self):
        retries = 0

        while retries < self.max_retries:
            try:
                self.tn = telnetlib.Telnet(self.host, port=23, timeout=self.timeout)
                if self.debug:
                    self.tn.set_debuglevel(2)
                self.tn.read_until(b"username:", timeout=self.timeout)
                time.sleep(0.1)
                self.tn.write(b"admin\n")
                self.tn.read_until(b"password:", timeout=self.timeout)
                time.sleep(0.1)
                self.tn.write(b"\n")
                self.tn.read_until(b"\r\n~ # ", timeout=self.timeout)
                print("Connected to CAM600")
                return  # Successfully connected
            except TimeoutError:
                print(
                    f"Connection to {self.host} timed out. Attempt {retries + 1} of {self.max_retries}"
                )
            except socket.error as e:
                print(f"Socket error: {e}. Attempt {retries + 1} of {self.max_retries}")
            except Exception as e:
                print(
                    f"Error connecting to {self.host}: {e}. Attempt {retries + 1} of {self.max_retries}"
                )

            retries += 1
            time.sleep(1)  # Optionally wait before retrying

        print(f"Failed to connect to {self.host} after {self.max_retries} attempts.")
        self.tn = None  # Ensure tn is set to None if all attempts fail

    def send(self, command):
        if not self.tn:  # Try to connect if not connected
            self._connect()

        if self.tn:
            try:
                self.tn.write(command.encode("ascii") + b"\n")

                # For gbcontrol commands, read the entire response including the first line
                if command.startswith("gbcontrol"):
                    # Read the entire response until the prompt
                    response = (
                        self.tn.read_until(b"~ # ", timeout=self.timeout)
                        .decode("ascii")
                        .replace("~ # ", "")
                        .strip()
                    )
                else:
                    # For gbconfig commands, read the entire response until the prompt
                    # This ensures we capture all lines including the first one
                    response = (
                        self.tn.read_until(b"~ # ", timeout=self.timeout)
                        .decode("ascii")
                        .replace("~ # ", "")
                        .strip()
                    )

                return response
            except Exception as e:
                print(f"Error sending command: {e}")
                # Try to reconnect on error
                self.tn = None
                return None
        else:
            print("Connection not established, cannot send command.")
            return None

    def test_connection(self, debug=False) -> str:
        self.debug = debug
        connection_start = time.time()
        self._connect()
        connection_time = round(time.time() - connection_start, 2)

        responses = []
        message = "gbconfig -s device-name"
        tries = 20
        messages_start = time.time()
        for i in range(tries):
            responses.append(self.send(message))
        messages_time = round(time.time() - messages_start, 2)

        total_time = round(connection_time + messages_time, 2)

        from collections import Counter

        response_counts = Counter(responses)
        most_common_response = response_counts.most_common(1)[0]
        correct_responses = most_common_response[1]

        if self.tn:
            self.tn.close()
            string = f'Message: "{message}" | Attempts: {tries}\nSample Response: {responses[0]}\nConnection Time: {connection_time}\nMessages Time: {messages_time}\nTotal Time: {total_time}\nCorrect Responses: {correct_responses}'
            return string
        else:
            return f"Failed to connect to {self.host}"

    def get_device_info(self) -> dict:
        """
        Get device information using gbcontrol --device-info.
        Returns model, firmware version, and build time.

        Returns:
            dict: A dictionary containing 'model', 'firmware', and 'build_date'.
        """
        response = self.send("gbcontrol --device-info")
        if response and "undefined option" not in response:
            response_lines = response.splitlines()
            if len(response_lines) >= 3:
                return {
                    "model": response_lines[0].strip(),
                    "firmware": response_lines[1].strip(),
                    "build_date": response_lines[2].strip(),
                }
        return {"error": "Failed to get device info"}

    def get_camera_info(self) -> dict:
        """
        Get camera information using gbcontrol --camera-info.
        Returns main firmware and motor firmware versions.

        Returns:
            dict: A dictionary containing camera firmware information.
        """
        response = self.send("gbcontrol --camera-info")
        if response and "undefined option" not in response:
            response_lines = response.splitlines()
            if len(response_lines) >= 3:
                return {
                    "main": response_lines[0].strip(),
                    "motor0": response_lines[1].strip(),
                    "motor1": response_lines[2].strip(),
                }
        return {"error": "Failed to get camera info"}

    def set_device_name(self, name: str) -> str:
        """
        Set the device name.

        Args:
            name (str): Device name (1-20 characters, letters, numbers, '_', '-')

        Returns:
            str: Response from the device.
        """
        if not (1 <= len(name) <= 20):
            raise ValueError("Device name must be 1-20 characters")
        return self.send(f"gbconfig --device-name {name}")

    def set_room_name(self, name: str) -> str:
        """
        Set the room name.

        Args:
            name (str): Room name (1-20 characters, letters, numbers, '_', '-')

        Returns:
            str: Response from the device.
        """
        if not (1 <= len(name) <= 20):
            raise ValueError("Room name must be 1-20 characters")
        return self.send(f"gbconfig --room-name {name}")

    def get_device_name(self) -> str:
        """Get the current device name."""
        return self.send("gbconfig -s device-name")

    def get_room_name(self) -> str:
        """Get the current room name."""
        return self.send("gbconfig -s room-name")

    def set_ptz_direction(self, direction: str) -> str:
        """
        Set PTZ direction using gbconfig --camera-autocoord.

        Args:
            direction (str): Direction ('r' for right, 'l' for left, 'u' for up, 'd' for down).

        Returns:
            str: Response from the device.
        """
        valid_directions = {"r": "r", "l": "l", "u": "u", "d": "d"}
        if direction not in valid_directions:
            raise ValueError("Invalid direction. Use 'r', 'l', 'u', or 'd'.")

        return self.send(f"gbconfig --camera-autocoord {direction}")

    def set_ptz_reset(self) -> str:
        """Reset camera current position and zoom to defaults."""
        return self.send("gbconfig --reset-camera-ptz")

    def set_tracking_mode(self, mode: int) -> str:
        """
        Set camera tracking mode using gbconfig --camera-mode.

        Args:
            mode (int): {0: off, 1: autoframing, 2: speakertracking, 3: presentertracking}
        """
        if mode not in [0, 1, 2, 3]:
            raise ValueError("Mode must be 0, 1, 2, or 3")
        return self.send(f"gbconfig --camera-mode {mode}")

    def get_tracking_mode(self) -> str:
        """Get current tracking mode."""
        return self.send("gbconfig -s camera-mode")

    def set_zoom(self, zoom_level: int) -> str:
        """
        Set camera zoom level using gbconfig --camera-zoom.

        Args:
            zoom_level (int): Zoom level between 100 and phymaxzoom.

        Returns:
            str: Response from the device.
        """
        if zoom_level < 100:
            raise ValueError("Zoom level must be at least 100")
        return self.send(f"gbconfig --camera-zoom {zoom_level}")

    def get_zoom(self) -> str:
        """Get current zoom level."""
        return self.send("gbconfig -s camera-zoom")

    def get_max_zoom(self) -> str:
        """Get maximum physical zoom level."""
        return self.send("gbconfig -s camera-phymaxzoom")

    def preset_save(self, preset: int) -> str:
        """
        Save current position as preset.

        Args:
            preset (int): Preset number (1-9)
        """
        if not (1 <= preset <= 9):
            raise ValueError("Preset must be between 1 and 9")
        return self.send(f"gbconfig --camera-savecoord {preset}")

    def preset_call(self, preset: int) -> str:
        """
        Load preset position.

        Args:
            preset (int): Preset number (1-9)
        """
        if not (1 <= preset <= 9):
            raise ValueError("Preset must be between 1 and 9")
        return self.send(f"gbconfig --camera-loadcoord {preset}")

    def set_mirror_invert(self, mirror: int, invert: int) -> str:
        """
        Set camera mirror and invert settings.

        Args:
            mirror (int): {0: no, 1: yes}
            invert (int): {0: no, 1: yes}
        """
        if mirror not in [0, 1] or invert not in [0, 1]:
            raise ValueError("Mirror and invert must be 0 or 1")
        return self.send(f"gbconfig --camera-mirror {mirror} {invert}")

    def get_mirror_invert(self) -> str:
        """Get current mirror and invert settings."""
        return self.send("gbconfig -s camera-mirror")

    def set_powerline_freq(self, freq: int) -> str:
        """
        Set powerline frequency for anti-flicker.

        Args:
            freq (int): {50: 50Hz, 60: 60Hz}
        """
        if freq not in [50, 60]:
            raise ValueError("Frequency must be 50 or 60")
        return self.send(f"gbconfig --camera-powerfreq {freq}")

    def get_powerline_freq(self) -> str:
        """Get current powerline frequency."""
        return self.send("gbconfig -s camera-powerfreq")

    def set_hd_mode(self, mode: int) -> str:
        """
        Set HD mode.

        Args:
            mode (int): {0: off, 1: on}
        """
        if mode not in [0, 1]:
            raise ValueError("Mode must be 0 or 1")
        return self.send(f"gbconfig --camera-hd {mode}")

    def get_hd_mode(self) -> str:
        """Get current HD mode status."""
        return self.send("gbconfig -s camera-hd")

    def set_off_tracking_mode(self, effect: int, pip: int, pos: int) -> str:
        """
        Set off tracking mode configuration.

        Args:
            effect (int): {0: immediate, 1: smooth} (not configurable, defaults to immediate)
            pip (int): {0: no, 1: yes}
            pos (int): {0: lu (left upper), 1: rd (right down)}
        """
        if pip not in [0, 1] or pos not in [0, 1]:
            raise ValueError("Pip and pos must be 0 or 1")
        return self.send(f"gbconfig --camera-offtracking {effect} {pip} {pos}")

    def get_off_tracking_mode(self) -> str:
        """Get current off tracking mode configuration."""
        return self.send("gbconfig -s camera-offtracking")

    def set_auto_framing_mode(self, effect: int, pip: int, pos: int) -> str:
        """
        Set auto framing mode configuration.

        Args:
            effect (int): {0: immediate, 1: smooth} (reserved command)
            pip (int): {0: no, 1: yes}
            pos (int): {0: lu (left upper), 1: rd (right down)}
        """
        if pip not in [0, 1] or pos not in [0, 1]:
            raise ValueError("Pip and pos must be 0 or 1")
        return self.send(f"gbconfig --camera-autoframing {effect} {pip} {pos}")

    def get_auto_framing_mode(self) -> str:
        """Get current auto framing mode configuration."""
        return self.send("gbconfig -s camera-autoframing")

    def set_auto_framing_speed(self, speed: int) -> str:
        """
        Set auto framing tracking speed.

        Args:
            speed (int): {0: slow, 1: normal, 2: fast}
        """
        if speed not in [0, 1, 2]:
            raise ValueError("Speed must be 0, 1, or 2")
        return self.send(f"gbconfig --camera-autoframingspeed {speed}")

    def get_auto_framing_speed(self) -> str:
        """Get current auto framing tracking speed."""
        return self.send("gbconfig -s camera-autoframingspeed")

    def set_speaker_tracking_mode(
        self, effect: int, pip: int, pos: int, disp: int
    ) -> str:
        """
        Set speaker tracking mode configuration.

        Args:
            effect (int): {0: immediate, 1: smooth} (not configurable, defaults to immediate)
            pip (int): {0: no, 1: yes}
            pos (int): {0: lu (left upper), 1: rd (right down)}
            disp (int): {0: normal, 1: gallery}
        """
        if pip not in [0, 1] or pos not in [0, 1] or disp not in [0, 1]:
            raise ValueError("Pip, pos, and disp must be 0 or 1")
        return self.send(
            f"gbconfig --camera-speakertracking {effect} {pip} {pos} {disp}"
        )

    def get_speaker_tracking_mode(self) -> str:
        """Get current speaker tracking mode configuration."""
        return self.send("gbconfig -s camera-speakertracking")

    def set_speaker_tracking_speed(self, speed: int) -> str:
        """
        Set speaker tracking speed.

        Args:
            speed (int): {0: slow, 1: normal, 2: fast}
        """
        if speed not in [0, 1, 2]:
            raise ValueError("Speed must be 0, 1, or 2")
        return self.send(f"gbconfig --camera-speakertrackingspeed {speed}")

    def get_speaker_tracking_speed(self) -> str:
        """Get current speaker tracking speed."""
        return self.send("gbconfig -s camera-speakertrackingspeed")

    def set_presenter_tracking_mode(self, effect: int, pip: int, pos: int) -> str:
        """
        Set presenter tracking mode configuration.

        Args:
            effect (int): {0: immediate, 1: smooth} (not configurable, defaults to immediate)
            pip (int): {0: no, 1: yes}
            pos (int): {0: lu (left upper), 1: rd (right down)}
        """
        if pip not in [0, 1] or pos not in [0, 1]:
            raise ValueError("Pip and pos must be 0 or 1")
        return self.send(f"gbconfig --camera-presentertracking {effect} {pip} {pos}")

    def get_presenter_tracking_mode(self) -> str:
        """Get current presenter tracking mode configuration."""
        return self.send("gbconfig -s camera-presentertracking")

    def set_network_dhcp(self) -> str:
        """Set network to DHCP mode."""
        return self.send("gbconfig --lan-info 0 0.0.0.0 0.0.0.0 0.0.0.0")

    def set_network_static(self, ipaddr: str, netmask: str, gateway: str) -> str:
        """
        Set network to static IP mode.

        Args:
            ipaddr (str): IP address (e.g., "192.168.1.88")
            netmask (str): Netmask (e.g., "255.255.255.0")
            gateway (str): Gateway (e.g., "192.168.1.1")
        """

        def is_valid_ip(ip):
            try:
                parts = ip.split(".")
                return len(parts) == 4 and all(0 <= int(part) <= 255 for part in parts)
            except (ValueError, AttributeError):
                return False

        if not all(is_valid_ip(ip) for ip in [ipaddr, netmask, gateway]):
            raise ValueError("Invalid IP address format")

        return self.send(f"gbconfig --lan-info 2 {ipaddr} {netmask} {gateway}")

    def get_network_info(self) -> str:
        """Get current network configuration."""
        return self.send("gbconfig -s lan-info")

    def set_ip_conflict_detection(self, enabled: bool) -> str:
        """
        Set IP conflict detection.

        Args:
            enabled (bool): True to enable, False to disable
        """
        value = 1 if enabled else 0
        return self.send(f"gbconfig --ip-conflict {value}")

    def get_ip_conflict_detection(self) -> str:
        """Get current IP conflict detection status."""
        return self.send("gbconfig -s ip-conflict")

    def set_standby_indicator(self, mode: int) -> str:
        """
        Set standby indicator mode.

        Args:
            mode (int): {0: white breathing, 2: red, 255: off}
        """
        if mode not in [0, 2, 255]:
            raise ValueError("Mode must be 0, 2, or 255")
        return self.send(f"gbconfig --standby-indicator {mode}")

    def get_standby_indicator(self) -> str:
        """Get current standby indicator mode."""
        return self.send("gbconfig -s standby-indicator")

    def set_hdmi_output(self, mode: int) -> str:
        """
        Set HDMI output mode.

        Args:
            mode (int): {0: off, 1: on}
        """
        if mode not in [0, 1]:
            raise ValueError("Mode must be 0 or 1")
        return self.send(f"gbconfig --hdmi-out {mode}")

    def get_hdmi_output(self) -> str:
        """Get current HDMI output status."""
        return self.send("gbconfig -s hdmi-out")

    def reboot(self) -> str:
        """Reboot the device."""
        return self.send("gbcontrol --reboot")

    def factory_reset(self) -> str:
        """Reset device to factory defaults."""
        return self.send("gbcontrol --reset-to-default")

    def get_help(self) -> str:
        """Get help information for gbconfig commands."""
        return self.send("gbconfig --help")

    def get_control_help(self) -> str:
        """Get help information for gbcontrol commands."""
        return self.send("gbcontrol --help")

    def test_all_get_commands(self, debug=False) -> dict:
        """
        Test all get commands in the CAM600 device wrapper.

        Args:
            debug (bool): Enable debug output

        Returns:
            dict: Summary of test results with success/failure counts
        """
        print("=" * 80)
        print("CAM600 DEVICE WRAPPER - COMPREHENSIVE GET COMMAND TEST")
        print("=" * 80)

        # Ensure we have a connection
        if not self.tn:
            print("Connecting to device...")
            self._connect()
            if not self.tn:
                print("ERROR: Failed to establish connection")
                return {"success": 0, "failure": 0, "total": 0}

        # Get device information for header
        print("\n" + "=" * 80)
        print("DEVICE INFORMATION")
        print("=" * 80)

        try:
            # Get device info (model, firmware, build date)
            device_info = self.get_device_info()
            if isinstance(device_info, dict) and "error" not in device_info:
                print(f"Model: {device_info.get('model', 'Unknown')}")
                print(f"Firmware: {device_info.get('firmware', 'Unknown')}")
                print(f"Build Date: {device_info.get('build_date', 'Unknown')}")
            else:
                print("Model: Unknown")
                print("Firmware: Unknown")
                print("Build Date: Unknown")

            # Get MAC address
            mac_response = self.send("gbconfig -s mac")
            if mac_response and "undefined option" not in mac_response:
                print(f"MAC: {mac_response.strip()}")
            else:
                print("MAC: Unknown")

        except Exception as e:
            print(f"Error getting device info: {e}")
            print("Model: Unknown")
            print("Firmware: Unknown")
            print("Build Date: Unknown")
            print("MAC: Unknown")

        print("=" * 80)

        # Define all get methods to test with their corresponding commands
        get_methods = [
            (
                "get_device_info",
                "Get device information (model, firmware, build date)",
                "gbcontrol --device-info",
            ),
            (
                "get_camera_info",
                "Get camera firmware information",
                "gbcontrol --camera-info",
            ),
            ("get_device_name", "Get current device name", "gbconfig -s device-name"),
            ("get_room_name", "Get current room name", "gbconfig -s room-name"),
            (
                "get_tracking_mode",
                "Get current tracking mode",
                "gbconfig -s camera-mode",
            ),
            ("get_zoom", "Get current zoom level", "gbconfig -s camera-zoom"),
            (
                "get_max_zoom",
                "Get maximum physical zoom level",
                "gbconfig -s camera-maxzoom",
            ),
            (
                "get_mirror_invert",
                "Get current mirror and invert settings",
                "gbconfig -s camera-mirror",
            ),
            (
                "get_powerline_freq",
                "Get current powerline frequency",
                "gbconfig -s camera-powerline",
            ),
            ("get_hd_mode", "Get current HD mode status", "gbconfig -s camera-hdmode"),
            (
                "get_off_tracking_mode",
                "Get current off tracking mode configuration",
                "gbconfig -s camera-offtracking",
            ),
            (
                "get_auto_framing_mode",
                "Get current auto framing mode configuration",
                "gbconfig -s camera-autoframing",
            ),
            (
                "get_auto_framing_speed",
                "Get current auto framing tracking speed",
                "gbconfig -s camera-autoframingspeed",
            ),
            (
                "get_speaker_tracking_mode",
                "Get current speaker tracking mode configuration",
                "gbconfig -s camera-speakertracking",
            ),
            (
                "get_speaker_tracking_speed",
                "Get current speaker tracking speed",
                "gbconfig -s camera-speakertrackingspeed",
            ),
            (
                "get_presenter_tracking_mode",
                "Get current presenter tracking mode configuration",
                "gbconfig -s camera-presentertracking",
            ),
            (
                "get_network_info",
                "Get current network configuration",
                "gbconfig -s network",
            ),
            (
                "get_ip_conflict_detection",
                "Get current IP conflict detection status",
                "gbconfig -s network-ipconflict",
            ),
            (
                "get_standby_indicator",
                "Get current standby indicator mode",
                "gbconfig -s system-standby",
            ),
            (
                "get_hdmi_output",
                "Get current HDMI output status",
                "gbconfig -s hdmi-out",
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
                    # Check if the response contains help text, which indicates an undefined option
                    if isinstance(result, str) and (
                        "usage:" in result.lower()
                        or "options:" in result.lower()
                        or "undefined option" in result.lower()
                        or "gbconfig [options]" in result
                        or "gbcontrol [options]" in result
                    ):
                        success = False
                        failure_count += 1
                        status = "FAILED (undefined option)"
                    elif isinstance(result, dict) and "error" in result:
                        success = False
                        failure_count += 1
                        status = f"FAILED ({result['error']})"
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
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
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

            # Clean up the result string for better formatting
            result_str = str(result["result"])

            # Remove all newlines, carriage returns, tabs, and other whitespace characters
            import re

            # First pass: Replace specific whitespace characters with spaces
            result_str = (
                result_str.replace("\n", " ").replace("\r", " ").replace("\t", " ")
            )

            # Second pass: Use regex to clean up any remaining multiple spaces
            result_str = re.sub(r"\s+", " ", result_str)

            # Strip leading/trailing whitespace
            result_str = result_str.strip()

            # Truncate to 35 characters and add ellipsis if needed (even shorter to prevent wrapping)
            if len(result_str) > 35:
                result_str = result_str[:32] + "..."

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


# Example usage:
if __name__ == "__main__":
    cam = CAM600_Device("10.0.30.91", debug=False)

    # Test all get commands
    test_results = cam.test_all_get_commands()
    print(f"\nTest completed. Success rate: {test_results['success_rate']}%")
