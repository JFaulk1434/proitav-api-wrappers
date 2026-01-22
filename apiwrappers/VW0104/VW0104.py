import logging
import socket
import telnetlib
import time


logger = logging.getLogger(__name__)


class VW0104_Device:
    def __init__(self, host, timeout=5, debug=False, max_retries=3):
        self.host = host
        self.timeout = timeout
        self.debug = debug
        self.tn = None
        self.max_retries = max_retries
        self.banner = ""
        self._silence_timeout = 0.2

    def _connect(self):
        retries = 0

        while retries < self.max_retries:
            try:
                self.tn = telnetlib.Telnet(self.host, port=23, timeout=self.timeout)
                if self.debug:
                    self.tn.set_debuglevel(2)

                # Attempt to determine if authentication is required
                initial = b""
                try:
                    initial = self.tn.read_until(b"username:", timeout=1)
                except EOFError:
                    initial = b""

                if b"username:" in initial.lower():
                    # Device expects credentials; use default admin with empty password
                    self.tn.write(b"admin\r\n")
                    self.tn.read_until(b"password:", timeout=self.timeout)
                    time.sleep(0.1)
                    self.tn.write(b"\r\n")
                else:
                    # No login required; keep welcome banner
                    self.banner = initial.decode("ascii", errors="ignore").strip()

                # Flush any remaining banner/prompt data
                time.sleep(0.1)
                extra = self.tn.read_very_eager()
                if extra:
                    banner_extra = extra.decode("ascii", errors="ignore").strip()
                    if banner_extra:
                        self.banner = (self.banner + "\n" + banner_extra).strip()

                # Send a newline to ensure the device is ready for commands
                self.tn.write(b"\r\n")
                time.sleep(0.1)
                _ = self.tn.read_very_eager()

                print("Connected to VW0104")
                return
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
            time.sleep(1)

        print(f"Failed to connect to {self.host} after {self.max_retries} attempts.")
        self.tn = None

    def send(self, command):
        if not self.tn:
            self._connect()

        if self.tn:
            try:
                self.tn.write(command.encode("ascii") + b"\r\n")
                response = self._read_response()
                return response
            except Exception as e:
                print(f"Error sending command: {e}")
                self.tn = None
                return None
        else:
            print("Connection not established, cannot send command.")
            return None

    def _read_response(self) -> str:
        """
        Read the device response until no new data is received for a short period
        or the main timeout is reached.
        """
        if not self.tn:
            return ""

        chunks = []
        end_time = time.time() + self.timeout
        last_data_time = time.time()

        while time.time() < end_time:
            try:
                data = self.tn.read_very_eager()
            except EOFError:
                break

            if data:
                chunks.append(data)
                last_data_time = time.time()
            else:
                if chunks and (time.time() - last_data_time) >= self._silence_timeout:
                    break
                time.sleep(0.05)

        response = b"".join(chunks).decode("ascii", errors="ignore").strip()
        return response

    def test_connection(self, debug=False) -> str:
        self.debug = debug
        connection_start = time.time()
        self._connect()
        connection_time = round(time.time() - connection_start, 2)

        responses = []
        message = "GET VER"
        tries = 20
        messages_start = time.time()
        for _ in range(tries):
            responses.append(self.send(message))
        messages_time = round(time.time() - messages_start, 2)

        total_time = round(connection_time + messages_time, 2)

        from collections import Counter

        response_counts = Counter(responses)
        most_common_response = response_counts.most_common(1)[0]
        correct_responses = most_common_response[1]

        if self.tn:
            self.tn.close()
            string = (
                f'Message: "{message}" | Attempts: {tries}\n'
                f"Sample Response: {responses[0]}\n"
                f"Connection Time: {connection_time}\n"
                f"Messages Time: {messages_time}\n"
                f"Total Time: {total_time}\n"
                f"Correct Responses: {correct_responses}"
            )
            return string
        else:
            return f"Failed to connect to {self.host}"

    # Audio commands
    def set_hdmi_audio_mute(self, output: str, state: str) -> str:
        valid_outputs = {"out1", "out2", "out3", "out4", "all"}
        valid_states = {"on", "off"}
        if output not in valid_outputs:
            raise ValueError(f"Output must be one of {valid_outputs}")
        if state not in valid_states:
            raise ValueError(f"State must be one of {valid_states}")
        return self.send(f"SET AVMUTE {output} {state}")

    def get_hdmi_audio_mute(self, output: str = "all") -> str:
        valid_outputs = {"out1", "out2", "out3", "out4", "all"}
        if output not in valid_outputs:
            raise ValueError(f"Output must be one of {valid_outputs}")
        return self.send(f"GET AVMUTE {output}")

    def set_audio_output_mute(self, state: str) -> str:
        valid_states = {"on", "off"}
        if state not in valid_states:
            raise ValueError(f"State must be one of {valid_states}")
        return self.send(f"SET AUDIO_MUTE {state}")

    def get_audio_output_mute(self) -> str:
        return self.send("GET AUDIO_MUTE")

    # CEC commands
    def set_cec_power(self, output: str, state: str) -> str:
        valid_outputs = {"out1", "out2", "out3", "out4", "all"}
        valid_states = {"on", "off"}
        if output not in valid_outputs:
            raise ValueError(f"Output must be one of {valid_outputs}")
        if state not in valid_states:
            raise ValueError(f"State must be one of {valid_states}")
        return self.send(f"SET CEC_PWR {output} {state}")

    def set_cec_auto_power(self, output: str, state: str) -> str:
        valid_outputs = {"out1", "out2", "out3", "out4", "all"}
        valid_states = {"on", "off"}
        if output not in valid_outputs:
            raise ValueError(f"Output must be one of {valid_outputs}")
        if state not in valid_states:
            raise ValueError(f"State must be one of {valid_states}")
        return self.send(f"SET AUTOCEC_FN {output} {state}")

    def get_cec_auto_power(self, output: str = "all") -> str:
        valid_outputs = {"out1", "out2", "out3", "out4", "all"}
        if output not in valid_outputs:
            raise ValueError(f"Output must be one of {valid_outputs}")
        return self.send(f"GET AUTOCEC_FN {output}")

    def set_cec_delay(self, output: str, delay_minutes: int) -> str:
        valid_outputs = {"out1", "out2", "out3", "out4", "all"}
        if output not in valid_outputs:
            raise ValueError(f"Output must be one of {valid_outputs}")
        if not (1 <= delay_minutes <= 30):
            raise ValueError("Delay must be between 1 and 30 minutes")
        return self.send(f"SET AUTOCEC_D {output} {delay_minutes}")

    def get_cec_delay(self, output: str = "all") -> str:
        valid_outputs = {"out1", "out2", "out3", "out4", "all"}
        if output not in valid_outputs:
            raise ValueError(f"Output must be one of {valid_outputs}")
        return self.send(f"GET AUTOCEC_D {output}")

    # HDCP commands
    def set_hdcp_support(self, input_port: str, state: str) -> str:
        valid_inputs = {"in1"}
        valid_states = {"on", "off"}
        if input_port not in valid_inputs:
            raise ValueError(f"Input port must be one of {valid_inputs}")
        if state not in valid_states:
            raise ValueError(f"State must be one of {valid_states}")
        return self.send(f"SET HDCP_S {input_port} {state}")

    def get_hdcp_support(self, input_port: str = "in1") -> str:
        valid_inputs = {"in1"}
        if input_port not in valid_inputs:
            raise ValueError(f"Input port must be one of {valid_inputs}")
        return self.send(f"GET HDCP_S {input_port}")

    # EDID commands
    def set_input_edid(self, scope: str, profile: int) -> str:
        if scope != "all":
            raise ValueError('Scope must be "all"')
        if not (1 <= profile <= 21 or profile == 99):
            raise ValueError("Profile must be between 1-21 or 99")
        return self.send(f"SET EDID {scope} {profile}")

    def get_input_edid(self, scope: str = "all") -> str:
        if scope != "all":
            raise ValueError('Scope must be "all"')
        return self.send(f"GET EDID {scope}")

    # OSD commands
    def set_osd(self, state: str) -> str:
        valid_states = {"on", "off"}
        if state not in valid_states:
            raise ValueError(f"State must be one of {valid_states}")
        return self.send(f"SET OSD {state}")

    # System commands
    def factory_reset(self) -> str:
        return self.send("RESET")

    def reboot(self) -> str:
        return self.send("REBOOT")

    def get_ip_address(self) -> str:
        return self.send("GET IPADDR")

    def set_ip_address(self, ipaddr: str, netmask: str, gateway: str) -> str:
        def is_valid_ip(ip):
            try:
                parts = ip.split(".")
                return len(parts) == 4 and all(0 <= int(part) <= 255 for part in parts)
            except (ValueError, AttributeError):
                return False

        if not all(is_valid_ip(value) for value in [ipaddr, netmask, gateway]):
            raise ValueError("Invalid IP address format")

        return self.send(f"SET IPADDR {ipaddr} MASK {netmask} GATEWAY {gateway}")

    def get_network_mode(self) -> str:
        return self.send("GET NETCFG MODE")

    def set_network_mode(self, mode: str) -> str:
        valid_modes = {"DHCP", "STATIC"}
        if mode not in valid_modes:
            raise ValueError(f"Mode must be one of {valid_modes}")
        return self.send(f"SET NETCFG MODE {mode}")

    def standby(self) -> str:
        return self.send("STANDBY")

    def wake(self) -> str:
        return self.send("WAKE")

    def get_standby_status(self) -> str:
        return self.send("GET STANDBY")

    # Update info commands
    def get_firmware_version(self) -> str:
        return self.send("GET VER")

    def get_hardware_version(self) -> str:
        return self.send("GET HW_VER")

    # Video output commands
    def set_scaler_mode(self, output: str, mode: str) -> str:
        valid_outputs = {"all"}
        valid_modes = {"auto", "manual"}
        if output not in valid_outputs:
            raise ValueError(f"Output must be one of {valid_outputs}")
        if mode not in valid_modes:
            raise ValueError(f"Mode must be one of {valid_modes}")
        return self.send(f"SET VIDOUT_SCALE {output} {mode}")

    def get_scaler_mode(self, output: str = "all") -> str:
        valid_outputs = {"all"}
        if output not in valid_outputs:
            raise ValueError(f"Output must be one of {valid_outputs}")
        return self.send(f"GET VIDOUT_SCALE {output}")

    def set_output_resolution(self, output: str, resolution: str) -> str:
        valid_outputs = {"all"}
        if output not in valid_outputs:
            raise ValueError(f"Output must be one of {valid_outputs}")
        if not resolution:
            raise ValueError("Resolution must be a non-empty string")
        return self.send(f"SET VIDOUT_RES {output} {resolution}")

    def get_output_resolution(self, output: str = "all") -> str:
        valid_outputs = {"all"}
        if output not in valid_outputs:
            raise ValueError(f"Output must be one of {valid_outputs}")
        return self.send(f"GET VIDOUT_RES {output}")

    # Video wall commands
    def set_video_wall_mode(self, mode: str) -> str:
        valid_modes = {"quick", "standard"}
        if mode not in valid_modes:
            raise ValueError(f"Mode must be one of {valid_modes}")
        return self.send(f"SET VIDWALL {mode}")

    def get_video_wall_mode(self) -> str:
        return self.send("GET VIDWALL")

    def set_quick_wall_mode(self, layout: str) -> str:
        valid_layouts = {
            "1x2",
            "1x2R",
            "1x3",
            "1x4",
            "1x4R",
            "2x1",
            "2x2",
            "2x2R",
            "SM",
            "3x1",
            "4x1",
        }
        if layout not in valid_layouts:
            raise ValueError(f"Layout must be one of {valid_layouts}")
        return self.send(f"SET VW_QUICK {layout}")

    def get_quick_wall_mode(self) -> str:
        return self.send("GET VW_QUICK")

    def test_all_get_commands(self, debug=False) -> dict:
        print("=" * 80)
        print("VW0104 DEVICE WRAPPER - COMPREHENSIVE GET COMMAND TEST")
        print("=" * 80)

        if not self.tn:
            print("Connecting to device...")
            self.debug = debug
            self._connect()
            if not self.tn:
                print("ERROR: Failed to establish connection")
                return {"success": 0, "failure": 0, "total": 0}

        get_methods = [
            (
                "get_hdmi_audio_mute",
                "Get HDMI audio mute status for specified output(s)",
                "GET AVMUTE all",
                {"output": "all"},
            ),
            (
                "get_audio_output_mute",
                "Get audio output mute status",
                "GET AUDIO_MUTE",
                {},
            ),
            (
                "get_cec_auto_power",
                "Get CEC auto power function status",
                "GET AUTOCEC_FN all",
                {"output": "all"},
            ),
            (
                "get_cec_delay",
                "Get CEC auto power delay time",
                "GET AUTOCEC_D all",
                {"output": "all"},
            ),
            (
                "get_hdcp_support",
                "Get HDCP support status for input",
                "GET HDCP_S in1",
                {"input_port": "in1"},
            ),
            (
                "get_input_edid",
                "Get input EDID status",
                "GET EDID all",
                {"scope": "all"},
            ),
            (
                "get_ip_address",
                "Retrieve IP address, subnet mask, and gateway",
                "GET IPADDR",
                {},
            ),
            (
                "get_network_mode",
                "Get network configuration mode",
                "GET NETCFG MODE",
                {},
            ),
            (
                "get_standby_status",
                "Check whether device is in standby or wake mode",
                "GET STANDBY",
                {},
            ),
            (
                "get_firmware_version",
                "Get firmware versions of internal modules",
                "GET VER",
                {},
            ),
            (
                "get_hardware_version",
                "Get hardware version",
                "GET HW_VER",
                {},
            ),
            (
                "get_scaler_mode",
                "Get current output scaler mode",
                "GET VIDOUT_SCALE all",
                {"output": "all"},
            ),
            (
                "get_output_resolution",
                "Get current output resolution",
                "GET VIDOUT_RES all",
                {"output": "all"},
            ),
            (
                "get_video_wall_mode",
                "Get current video wall mode",
                "GET VIDWALL",
                {},
            ),
            (
                "get_quick_wall_mode",
                "Get current quick video wall layout",
                "GET VW_QUICK",
                {},
            ),
        ]

        results = []
        success_count = 0
        failure_count = 0

        print(f"\nTesting {len(get_methods)} get methods...")
        print("-" * 80)

        for method_name, description, command, kwargs in get_methods:
            print(f"\n{method_name}: {description}")
            print(f"Command: {command}")
            print("-" * 60)

            try:
                method = getattr(self, method_name)
                start_time = time.time()
                result = method(**kwargs)
                execution_time = round(time.time() - start_time, 3)

                if result is not None:
                    if isinstance(result, str) and (
                        "usage:" in result.lower()
                        or "options:" in result.lower()
                        or "undefined option" in result.lower()
                    ):
                        success = False
                        failure_count += 1
                        status = "FAILED (undefined option)"
                    else:
                        success = True
                        success_count += 1
                        status = "SUCCESS"
                else:
                    success = False
                    failure_count += 1
                    status = "FAILED (no response)"

                print(f"{'=' * 80}")
                print(f"Command: {command}")
                print(f"Status: {status}")
                print(f"Response: {result}")
                print(f"{'=' * 80}")

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

        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Total Methods Tested: {len(get_methods)}")
        print(f"Successful: {success_count}")
        print(f"Failed: {failure_count}")
        success_rate = (success_count / len(get_methods) * 100) if get_methods else 0
        print(f"Success Rate: {success_rate:.1f}%")

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

            result_str = str(result["result"])
            import re

            result_str = (
                result_str.replace("\n", " ").replace("\r", " ").replace("\t", " ")
            )
            result_str = re.sub(r"\s+", " ", result_str).strip()

            if len(result_str) > 35:
                result_str = result_str[:32] + "..."

            print(
                f"{result['command']:<40} {status_short:<15} {time_str:<8} {result_str}"
            )

        summary = {
            "success": success_count,
            "failure": failure_count,
            "total": len(get_methods),
            "success_rate": round(success_rate, 1),
            "results": results,
        }

        return summary


if __name__ == "__main__":
    device = VW0104_Device("10.0.40.23", debug=False)
    test_results = device.test_all_get_commands()
    print(f"\nTest completed. Success rate: {test_results['success_rate']}%")
