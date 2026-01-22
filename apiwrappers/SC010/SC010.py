import telnetlib
import socket
import time
import logging
import json
from typing import List, Dict, Union


logger = logging.getLogger(__name__)


class SC010_Device:
    def __init__(self, host, timeout=5, debug=False, max_retries=3):
        self.host = host
        self.port = 23
        self.timeout = timeout
        self.debug = debug
        self.tn = None
        self.max_retries = max_retries

    def _connect(self):
        retries = 0

        while retries < self.max_retries:
            try:
                self.tn = telnetlib.Telnet(
                    self.host, port=self.port, timeout=self.timeout
                )
                if self.debug:
                    self.tn.set_debuglevel(2)
                self.tn.read_until(b"welcome to use hdip system.", timeout=self.timeout)
                if self.debug:
                    print(f"Connected to SC010 at {self.host}")
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
                # Flush any pending responses
                self.tn.read_very_eager()

                # Send command
                self.tn.write(command.encode("ascii") + b"\n")

                # Read response until double CRLF (SC010 protocol)
                response = (
                    self.tn.read_until(b"\r\n\r\n", timeout=self.timeout)
                    .decode("ascii")
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

    def _strip_prefix(self, response):
        """Strips everything before the first [ or { character."""
        start_bracket = response.find("[")
        start_brace = response.find("{")
        start = min(
            start_bracket if start_bracket != -1 else float("inf"),
            start_brace if start_brace != -1 else float("inf"),
        )
        if start != float("inf"):
            return response[start:]
        return response

    def _parse_json_response(self, response):
        """Parse JSON response, handling prefixes."""
        try:
            cleaned = self._strip_prefix(response)
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decoding error: {e}, response: {response}")
            return {}

    # Device Commands (from sc010_device.yml)

    def device_info(self, *hostnames) -> Union[Dict, List[Dict]]:
        """
        Get device information.

        Args:
            *hostnames: Optional hostname(s) to query. If none provided, returns info for all devices.

        Returns:
            dict or list: Device information as JSON. If multiple hostnames, returns list of dicts.
        """
        if hostnames:
            command = f"device info {' '.join(hostnames)}"
        else:
            command = "device info"

        response = self.send(command)
        if response:
            return self._parse_json_response(response)
        return {}

    def device_reboot(self, *hostnames) -> str:
        """
        Reboot device(s).

        Args:
            *hostnames: One or more hostnames to reboot.

        Returns:
            str: Confirmation response from the device.
        """
        if not hostnames:
            raise ValueError("At least one hostname must be provided")

        command = f"device reboot {' '.join(hostnames)}"
        return self.send(command)

    def device_restorefactory(self, *hostnames) -> str:
        """
        Factory reset device(s).

        Args:
            *hostnames: One or more hostnames to factory reset.

        Returns:
            str: Confirmation response from the device.
        """
        if not hostnames:
            raise ValueError("At least one hostname must be provided")

        command = f"device restorefactory {' '.join(hostnames)}"
        return self.send(command)

    def device_alias_set(self, hostname: str, alias: str) -> str:
        """
        Assign alias to device.

        Args:
            hostname: Device hostname.
            alias: Alias to assign.

        Returns:
            str: Confirmation response from the device.
        """
        command = f"device alias set {hostname} {alias}"
        return self.send(command)

    def device_alias_get(self, hostname: str) -> str:
        """
        Get device alias.

        Args:
            hostname: Device hostname.

        Returns:
            str: Device alias, or "NULL" if not set.
        """
        command = f"device alias get {hostname}"
        response = self.send(command)
        if response:
            # Parse alias from response (format may vary)
            return response.strip()
        return None

    # Additional helper methods for compatibility with existing code

    def get_version(self) -> dict:
        """Get API and system version information."""
        response = self.send("config get version")
        if response:
            data_lines = response.strip().split("\n")
            data_dict = {}
            for line in data_lines:
                if ": " in line:
                    key, value = line.split(": ", 1)
                    data_dict[key.strip()] = value.strip()
            return data_dict
        return {}

    def get_system_info(self) -> dict:
        """Get system information."""
        response = self.send("config get system info")
        if response:
            return self._parse_json_response(response)
        return {}

    def get_devicelist(self) -> list:
        """Get all online device names."""
        command = "config get devicelist"
        response = self.send(command)
        if response:
            cleaned_str = response.replace("devicelist is ", "").strip()
            device_list = cleaned_str.split(" ")
            return [d for d in device_list if d]  # Filter empty strings
        return []

    def get_device_name(self, device=None):
        """Obtains device name or its alias."""
        if device is None:
            command = "config get name"
        else:
            command = f"config get name {device}"
        return self.send(command)

    def get_device_info(self, *hostnames) -> dict:
        """Obtains device working parameters in real time."""
        command = "config get device info "
        for hostname in hostnames:
            command += hostname + " "
        response = self.send(command)
        if response:
            return self._parse_json_response(response)
        return {}

    def get_device_status(self, *hostnames) -> dict:
        """Obtains device status in real time."""
        command = "config get device status "
        for hostname in hostnames:
            command += hostname + " "
        response = self.send(command)
        if response:
            return self._parse_json_response(response)
        return {}

    def get_device_json(self) -> list:
        """Obtains all device information and returns a list of dictionaries."""
        response = self.send("config get devicejsonstring")
        if response:
            return self._parse_json_response(response)
        return []

    def get_scene_json(self) -> dict:
        """Obtains all scene information."""
        command = "config get scenejsonstring"
        response = self.send(command)
        if response:
            return self._parse_json_response(response)
        return {}

    def get_ipsettings(self, lan=1):
        """Get network settings for LAN(AV) or LAN(C) and return as a dictionary."""
        if lan == 1:
            command = "config get ipsetting"
            port = "LAN(AV)"
        else:
            command = "config get ipsetting2"
            port = "LAN(C)"

        response = self.send(command)
        if not response:
            return {}

        # Remove the "config get ipsetting" or "config get ipsetting2" part from the response
        if lan == 1:
            response = response.replace("ipsetting is:", "").strip()
        else:
            response = response.replace("ipsetting2 is:", "").strip()

        # Split the response into parts and parse into a dictionary
        settings_dict = {"port": port}
        parts = response.split(" ")
        for i in range(0, len(parts), 2):
            if i + 1 < len(parts):
                key = parts[i]
                value = parts[i + 1]
                settings_dict[key] = value

        return settings_dict

    def get_matrix(self):
        """Obtains TX played by RX in matrix."""
        command = "matrix get"
        return self.send(command)

    def get_vw(self):
        """Get video wall."""
        return self.send("vw get")

    def disconnect(self):
        """Safely closes the Telnet connection if it exists."""
        if self.tn is not None:
            try:
                self.tn.close()
            except Exception as e:
                print(f"Error closing Telnet connection: {e}")
            finally:
                self.tn = None

    def test_connection(self, debug=False) -> str:
        """Test connection to the device."""
        self.debug = debug
        connection_start = time.time()
        self._connect()
        connection_time = round(time.time() - connection_start, 2)

        responses = []
        message = "config get version"
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

    def test_all_get_commands(self, debug=False) -> dict:
        """
        Test all get commands in the SC010 device wrapper.

        Args:
            debug (bool): Enable debug output

        Returns:
            dict: Summary of test results with success/failure counts
        """
        print("=" * 80)
        print("SC010 DEVICE WRAPPER - COMPREHENSIVE GET COMMAND TEST")
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
            # Get version info
            version_info = self.get_version()
            if version_info:
                print(f"API Version: {version_info.get('API version', 'Unknown')}")
                print(
                    f"System Version: {version_info.get('System version', 'Unknown')}"
                )
            else:
                print("API Version: Unknown")
                print("System Version: Unknown")

            # Get system info
            system_info = self.get_system_info()
            if system_info:
                print(f"System Info: {json.dumps(system_info, indent=2)}")
            else:
                print("System Info: Unknown")

        except Exception as e:
            print(f"Error getting device info: {e}")
            print("API Version: Unknown")
            print("System Version: Unknown")

        print("=" * 80)

        # Define all get methods to test with their corresponding commands
        get_methods = [
            (
                "get_version",
                "Get API and system version information",
                "config get version",
            ),
            (
                "get_system_info",
                "Get system information",
                "config get system info",
            ),
            (
                "get_devicelist",
                "Get all online device names",
                "config get devicelist",
            ),
            (
                "get_device_name",
                "Get device name or alias (no parameters)",
                "config get name",
            ),
            (
                "get_device_info",
                "Get device working parameters (requires hostname - will test with first device if available)",
                "config get device info",
            ),
            (
                "get_device_status",
                "Get device status (requires hostname - will test with first device if available)",
                "config get device status",
            ),
            (
                "get_device_json",
                "Get all device information as JSON",
                "config get devicejsonstring",
            ),
            (
                "get_scene_json",
                "Get all scene information",
                "config get scenejsonstring",
            ),
            (
                "get_ipsettings",
                "Get network settings for LAN(AV)",
                "config get ipsetting",
            ),
            (
                "get_matrix",
                "Get TX played by RX in matrix",
                "matrix get",
            ),
            (
                "get_vw",
                "Get video wall information",
                "vw get",
            ),
            (
                "device_info",
                "Get device information (device command)",
                "device info",
            ),
        ]

        results = []
        success_count = 0
        failure_count = 0

        # Get device list for testing device-specific commands
        device_list = []
        try:
            device_list = self.get_devicelist()
        except Exception as e:
            print(f"Warning: Could not get device list: {e}")

        print(f"\nTesting {len(get_methods)} get methods...")
        print("-" * 80)

        for method_name, description, command in get_methods:
            print(f"\n{method_name}: {description}")
            print(f"Command: {command}")
            print("-" * 60)

            try:
                # Get the method object
                method = getattr(self, method_name)

                # Handle methods that require hostname parameters
                if method_name in ["get_device_info", "get_device_status"]:
                    if device_list and len(device_list) > 0:
                        # Use first device for testing
                        test_hostname = device_list[0]
                        command = f"{command} {test_hostname}"
                        start_time = time.time()
                        result = method(test_hostname)
                        execution_time = round(time.time() - start_time, 3)
                    else:
                        # No devices available, skip test
                        failure_count += 1
                        status = "SKIPPED (no devices available)"
                        print(f"Status: {status}")
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
                        continue
                elif method_name == "get_device_name":
                    # Test without parameters
                    start_time = time.time()
                    result = method()
                    execution_time = round(time.time() - start_time, 3)
                elif method_name == "get_ipsettings":
                    # Test with default parameter
                    start_time = time.time()
                    result = method(1)
                    execution_time = round(time.time() - start_time, 3)
                else:
                    # Execute the method
                    start_time = time.time()
                    result = method()
                    execution_time = round(time.time() - start_time, 3)

                # Determine success based on result
                if result is not None:
                    # Check if the response indicates an error
                    if isinstance(result, str) and (
                        "error" in result.lower()
                        or "undefined" in result.lower()
                        or "invalid" in result.lower()
                    ):
                        success = False
                        failure_count += 1
                        status = "FAILED (error in response)"
                    elif isinstance(result, (dict, list)) and len(result) == 0:
                        # Empty dict/list might be valid, but could indicate an issue
                        success = True  # Assume success for empty results
                        success_count += 1
                        status = "SUCCESS (empty result)"
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
        if len(get_methods) > 0:
            print(f"Success Rate: {(success_count / len(get_methods) * 100):.1f}%")
        else:
            print("Success Rate: N/A")

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

            # Truncate to 35 characters and add ellipsis if needed
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
            "success_rate": round(success_count / len(get_methods) * 100, 1)
            if len(get_methods) > 0
            else 0,
            "results": results,
        }

        return summary


# Example usage:
if __name__ == "__main__":
    device = SC010_Device("10.0.30.8", debug=False)

    # Test all get commands
    test_results = device.test_all_get_commands()
    print(f"\nTest completed. Success rate: {test_results['success_rate']}%")

    # Example device commands
    # device.device_info("hostname1", "hostname2")
    # device.device_alias_set("hostname1", "alias1")
    # alias = device.device_alias_get("hostname1")
    # device.device_reboot("hostname1")

    device.disconnect()
