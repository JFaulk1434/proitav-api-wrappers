import socket
import telnetlib
import time
from typing import Any, Dict, List, Optional

try:
    import serial  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - optional dependency for RS232 mode
    serial = None


class EX3H201Device:
    """
    EX-3H201-000 API wrapper supporting both Telnet and RS232 transports.

    The default connection type is telnet.
    """

    def __init__(
        self,
        host: str,
        port: int = 23,
        timeout: float = 3.0,
        debug: bool = False,
        connection_type: str = "telnet",
        serial_port: Optional[str] = None,
        serial_baudrate: int = 115200,
    ):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.debug = debug
        self.connection_type = connection_type.lower()
        self.serial_port = serial_port
        self.serial_baudrate = serial_baudrate

        self.tn: Optional[telnetlib.Telnet] = None
        self.ser = None

    def connect(self) -> None:
        """Open a connection using the selected transport."""
        if self.connection_type == "telnet":
            self._connect_telnet()
        elif self.connection_type == "rs232":
            self._connect_rs232()
        else:
            raise ValueError(
                "Invalid connection_type. Use 'telnet' (default) or 'rs232'."
            )

    def disconnect(self) -> None:
        """Close any active connection."""
        if self.tn:
            self.tn.close()
            self.tn = None
        if self.ser:
            self.ser.close()
            self.ser = None

    def _connect_telnet(self) -> None:
        self.disconnect()
        try:
            self.tn = telnetlib.Telnet(self.host, self.port, timeout=self.timeout)
            if self.debug:
                self.tn.set_debuglevel(1)
        except (TimeoutError, socket.error) as exc:
            self.tn = None
            raise ConnectionError(f"Telnet connection failed: {exc}") from exc

    def _connect_rs232(self) -> None:
        self.disconnect()
        if serial is None:
            raise ImportError(
                "pyserial is required for RS232 mode. Install with: pip install pyserial"
            )
        if not self.serial_port:
            raise ValueError(
                "serial_port is required when connection_type='rs232' (e.g. /dev/tty.usbserial-xxxx)"
            )
        try:
            self.ser = serial.Serial(
                port=self.serial_port,
                baudrate=self.serial_baudrate,
                bytesize=8,
                parity="N",
                stopbits=1,
                timeout=self.timeout,
            )
        except Exception as exc:
            self.ser = None
            raise ConnectionError(f"RS232 connection failed: {exc}") from exc

    def _ensure_connected(self) -> None:
        if self.connection_type == "telnet" and self.tn is None:
            self.connect()
        if self.connection_type == "rs232" and self.ser is None:
            self.connect()

    def send(self, command: str) -> str:
        """
        Send a raw device command.
        Commands are terminated with CRLF per the API doc.
        """
        self._ensure_connected()
        framed = f"{command}\r\n"
        if self.debug:
            print(f"TX ({self.connection_type}): {command}")

        if self.connection_type == "telnet":
            self.tn.write(framed.encode("ascii"))
            response = self._read_telnet_response()
        else:
            self.ser.write(framed.encode("ascii"))
            self.ser.flush()
            response = self._read_rs232_response()

        if self.debug:
            print(f"RX ({self.connection_type}): {response}")
        return response

    def _read_telnet_response(self) -> str:
        chunks: List[str] = []
        deadline = time.time() + self.timeout
        last_data_time = time.time()

        while time.time() < deadline:
            data = self.tn.read_very_eager()
            if data:
                decoded = data.decode("utf-8", errors="ignore")
                chunks.append(decoded)
                last_data_time = time.time()
            elif time.time() - last_data_time > 0.2:
                break
            time.sleep(0.03)

        return "".join(chunks).strip()

    def _read_rs232_response(self) -> str:
        chunks: List[str] = []
        deadline = time.time() + self.timeout
        last_data_time = time.time()

        while time.time() < deadline:
            data = self.ser.read(512)
            if data:
                decoded = data.decode("utf-8", errors="ignore")
                chunks.append(decoded)
                last_data_time = time.time()
            elif time.time() - last_data_time > 0.2:
                break
            time.sleep(0.03)

        return "".join(chunks).strip()

    # ----------------------------
    # System commands
    # ----------------------------
    def get_help(self) -> str:
        return self.send("help")

    def get_firmware_version(self) -> str:
        return self.send("GET VER")

    def factory_reset(self) -> str:
        return self.send("RESET")

    def reboot(self) -> str:
        return self.send("REBOOT")

    def set_ip_mode(self, mode: str) -> str:
        return self.send(f"SET IP MODE {mode}")

    def get_ip_mode(self) -> str:
        return self.send("GET IP MODE")

    def set_ip_address(self, ip: str, mask: str, gateway: str) -> str:
        return self.send(f"SET IPADDR {ip} {mask} {gateway}")

    def get_ip_address(self) -> str:
        return self.send("GET IPADDR")

    # ----------------------------
    # Video switch
    # ----------------------------
    def set_switch(self, output: str, source_input: str) -> str:
        return self.send(f"SET SW {output} {source_input}")

    def get_switch(self, output: str = "OUT1") -> str:
        return self.send(f"GET SW {output}")

    def set_auto_switching(self, state: str) -> str:
        return self.send(f"SET AUTOSW_FN {state}")

    def get_auto_switching(self) -> str:
        return self.send("GET AUTOSW_FN")

    # ----------------------------
    # RS232 passthrough config
    # ----------------------------
    def set_uart_baud(self, baudrate: int) -> str:
        return self.send(f"SET UART_B {baudrate}")

    def get_uart_baud(self) -> str:
        return self.send("GET UART_B")

    def set_uart_command(self, action: str, cmd_type: str, payload: str) -> str:
        return self.send(f"SET UART_CMD {action} {cmd_type} {payload}")

    def get_uart_commands(self) -> str:
        return self.send("GET UART_CMD")

    def send_uart_action(self, action: str) -> str:
        return self.send(f"SET UART_CMD_S {action}")

    # ----------------------------
    # Video detail info
    # ----------------------------
    def get_video_input_signal(self, source_input: str = "ALL") -> str:
        return self.send(f"GET VIDIN_SIG {source_input}")

    def get_video_input_hdcp(self, source_input: str = "ALL") -> str:
        return self.send(f"GET VIDIN_HDCP {source_input}")

    def get_output_hdcp(self, output: str = "OUT1") -> str:
        return self.send(f"GET HDCP {output}")

    def set_input_edid(self, source_input: str, edid_id: int) -> str:
        return self.send(f"SET EDID {source_input} {edid_id}")

    def get_input_edid(self, source_input: str = "ALL") -> str:
        return self.send(f"GET EDID {source_input}")

    def read_output_edid(self, output: str = "OUT1") -> str:
        return self.send(f"GET EDID_R {output}")

    def write_custom_edid(self, cedid: str, block: str, edid_ascii_data: str) -> str:
        return self.send(f"SET EDID_C {cedid} {block} {edid_ascii_data}")

    def get_custom_edid(self, cedid: str = "cedid1") -> str:
        return self.send(f"GET EDID_C {cedid}")

    # ----------------------------
    # Security
    # ----------------------------
    def set_telnet_password_required(self, state: str) -> str:
        return self.send(f"SET TELNETPW {state}")

    def get_telnet_password_required(self) -> str:
        return self.send("GET TELNETPW")

    def set_telnet_password(
        self, old_password: str, new_password: str, verify_password: str
    ) -> str:
        return self.send(f"SET TEL_PWD {old_password} {new_password} {verify_password}")

    def get_device_info(self) -> Dict[str, Any]:
        """Best-effort device info for test report headers."""
        info: Dict[str, Any] = {
            "model": "EX-3H201-000",
            "firmware": "Unknown",
            "ip_mode": "Unknown",
            "ip_address": "Unknown",
        }
        try:
            fw = self.get_firmware_version()
            if fw:
                info["firmware"] = fw.strip()
        except Exception:
            pass
        try:
            ip_mode = self.get_ip_mode()
            if ip_mode:
                info["ip_mode"] = ip_mode.strip()
        except Exception:
            pass
        try:
            ip_addr = self.get_ip_address()
            if ip_addr:
                info["ip_address"] = ip_addr.strip()
        except Exception:
            pass
        return info

    def test_all_get_commands(self) -> Dict[str, Any]:
        """
        Run all GET/read commands and print a report-style output.
        """
        section_sep = "~" * 80
        block_sep = "-" * 60

        print("\nEX-3H201-000 Device Wrapper API Test\n")
        print(section_sep)
        print()
        print("DEVICE INFORMATION")
        print(section_sep)
        print()

        self._ensure_connected()
        info = self.get_device_info()
        print(f"Model: {info.get('model', 'Unknown')}")
        print(f"Firmware: {info.get('firmware', 'Unknown')}")
        print(f"IP Mode: {info.get('ip_mode', 'Unknown')}")
        print(f"IP Address: {info.get('ip_address', 'Unknown')}")
        print(f"Transport: {self.connection_type}")

        get_methods = [
            ("get_help", "Get API command list", "help"),
            ("get_firmware_version", "Get firmware version", "GET VER"),
            ("get_ip_mode", "Get IP mode", "GET IP MODE"),
            ("get_ip_address", "Get IP address", "GET IPADDR"),
            ("get_switch", "Get which input maps to output", "GET SW OUT1"),
            ("get_auto_switching", "Get auto switching status", "GET AUTOSW_FN"),
            ("get_uart_baud", "Get RS232 baud rate", "GET UART_B"),
            ("get_uart_commands", "Get RS232 command map", "GET UART_CMD"),
            ("get_video_input_signal", "Get input signal status", "GET VIDIN_SIG ALL"),
            ("get_video_input_hdcp", "Get input HDCP status", "GET VIDIN_HDCP ALL"),
            ("get_output_hdcp", "Get output HDCP status", "GET HDCP OUT1"),
            ("get_input_edid", "Get input EDID status", "GET EDID ALL"),
            ("read_output_edid", "Read output EDID", "GET EDID_R OUT1"),
            ("get_custom_edid", "Get custom EDID", "GET EDID_C cedid1"),
            (
                "get_telnet_password_required",
                "Get telnet password requirement status",
                "GET TELNETPW",
            ),
        ]

        print(f"\nTesting {len(get_methods)} get methods...")
        success = 0
        failure = 0
        results: List[Dict[str, Any]] = []

        try:
            for method_name, description, command in get_methods:
                print(section_sep)
                print(f"{method_name}: {description}")
                print(f"Command: {command}")
                print(block_sep)

                start = time.time()
                try:
                    method = getattr(self, method_name)
                    value = method()
                    elapsed = round(time.time() - start, 3)
                    ok = value is not None and str(value).strip() != ""
                    status = "SUCCESS" if ok else "FAILED (empty response)"
                    if ok:
                        success += 1
                    else:
                        failure += 1
                except Exception as exc:
                    elapsed = round(time.time() - start, 3)
                    value = f"Exception: {exc}"
                    status = "FAILED (exception)"
                    failure += 1

                print(f"Status: {status}")
                print(f"Response: {value}")
                print(f"Response time: {elapsed}s")
                print(block_sep)

                results.append(
                    {
                        "method": method_name,
                        "command": command,
                        "status": status,
                        "success": status == "SUCCESS",
                        "response": value,
                        "response_time": elapsed,
                    }
                )
        finally:
            self.disconnect()

        total = len(get_methods)
        success_rate = round((success / total) * 100, 1) if total else 0.0
        successful_results = [r for r in results if r["success"]]
        timing_pool = successful_results if successful_results else results

        if timing_pool:
            fastest = min(timing_pool, key=lambda x: x["response_time"])
            slowest = max(timing_pool, key=lambda x: x["response_time"])
            average_response_time = round(
                sum(r["response_time"] for r in timing_pool) / len(timing_pool), 3
            )
            fastest_response_time = fastest["response_time"]
            slowest_response_time = slowest["response_time"]
            fastest_call = f"{fastest['method']} ({fastest['command']})"
            slowest_call = f"{slowest['method']} ({slowest['command']})"
        else:
            average_response_time = 0.0
            fastest_response_time = 0.0
            slowest_response_time = 0.0
            fastest_call = "N/A"
            slowest_call = "N/A"

        print("\n" + section_sep)
        print("TEST SUMMARY")
        print(section_sep)
        print(f"Total methods tested: {total}")
        print(f"Successful: {success}")
        print(f"Failed: {failure}")
        print(f"Success rate: {success_rate}%")
        print(f"Average API response time: {average_response_time}s")
        print(f"Fastest API response time: {fastest_response_time}s")
        print(f"Fastest API call: {fastest_call}")
        print(f"Slowest API response time: {slowest_response_time}s")
        print(f"Slowest API call: {slowest_call}")

        return {
            "success": success,
            "failure": failure,
            "total": total,
            "success_rate": success_rate,
            "average_response_time": average_response_time,
            "fastest_response_time": fastest_response_time,
            "fastest_call": fastest_call,
            "slowest_response_time": slowest_response_time,
            "slowest_call": slowest_call,
            "results": results,
        }


if __name__ == "__main__":
    # Default is Telnet; switch to RS232 by setting connection_type="rs232"
    # and providing serial_port.
    device = EX3H201Device(
        host="10.0.40.30",
        connection_type="telnet",
        debug=False,
        # serial_port="/dev/tty.usbserial-XXXX",  # required for RS232 mode
    )
    report = device.test_all_get_commands()
    print(f"\nTest completed. Success rate: {report['success_rate']}%")
