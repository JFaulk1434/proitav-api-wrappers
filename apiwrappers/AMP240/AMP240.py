"""Telnet API wrapper for AMP-240-000."""

import socket
import telnetlib  # type: ignore[import-not-found]
import time
from typing import Any, Dict, Optional


class AMP240Device:
    """AMP-240-000 telnet wrapper."""

    def __init__(
        self,
        host: str,
        port: int = 23,
        timeout: float = 3.0,
        username: Optional[str] = None,
        password: Optional[str] = None,
        debug: bool = False,
        max_retries: int = 2,
    ):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.username = username
        self.password = password
        self.debug = debug
        self.max_retries = max_retries
        self.tn: Optional[telnetlib.Telnet] = None

    def connect(self) -> None:
        """Open telnet connection and handle optional auth prompts."""
        self.disconnect()
        try:
            self.tn = telnetlib.Telnet(self.host, self.port, timeout=self.timeout)
            if self.debug:
                self.tn.set_debuglevel(1)
        except (TimeoutError, socket.error) as exc:
            self.tn = None
            raise ConnectionError(
                f"Failed to connect to {self.host}:{self.port}: {exc}"
            )

        # Optional login flow (if prompts are enabled on the device).
        greeting = self._read_telnet_response(read_timeout=0.8)
        greeting_lower = greeting.lower()
        if "username" in greeting_lower and self.username:
            self.tn.write(f"{self.username}\r\n".encode("ascii"))
            greeting = self._read_telnet_response(read_timeout=0.6)
            greeting_lower = greeting.lower()
        if "password" in greeting_lower and self.password:
            self.tn.write(f"{self.password}\r\n".encode("ascii"))
            self._read_telnet_response(read_timeout=0.6)

    def disconnect(self) -> None:
        if self.tn:
            self.tn.close()
            self.tn = None

    def _ensure_connected(self) -> None:
        if self.tn is None:
            self.connect()

    def _read_telnet_response(self, read_timeout: float) -> str:
        chunks = []
        deadline = time.time() + read_timeout
        last_data_time = time.time()

        while time.time() < deadline:
            data = self.tn.read_very_eager()
            if data:
                chunks.append(data.decode("utf-8", errors="ignore"))
                last_data_time = time.time()
            elif time.time() - last_data_time > 0.2:
                break
            time.sleep(0.03)
        return "".join(chunks).strip()

    def send(self, command: str) -> str:
        """Send one API command and return response."""
        last_error = None
        for _ in range(self.max_retries):
            try:
                self._ensure_connected()
                message = f"{command.strip()}\r\n"
                if self.debug:
                    print(f"TX: {command}")
                self.tn.write(message.encode("ascii"))
                response = self._read_telnet_response(read_timeout=self.timeout)
                if self.debug:
                    print(f"RX: {response}")
                return response
            except Exception as exc:  # pragma: no cover - network/runtime behavior
                last_error = exc
                self.disconnect()
        raise RuntimeError(f"Failed to send command '{command}': {last_error}")

    # Audio DSP control
    def set_dsp_mix(self, out_port: str, in_port: str, value: str) -> str:
        return self.send(f"SET DSP_MIX {out_port} {in_port} {value}")

    def get_dsp_mix(self, out_port: str, in_port: str) -> str:
        return self.send(f"GET DSP_MIX {out_port} {in_port}")

    def set_dsp_expander(self, port: str, value: str) -> str:
        return self.send(f"SET DSP_EXP {port} {value}")

    def get_dsp_expander(self, port: str) -> str:
        return self.send(f"GET DSP_EXP {port}")

    def set_dsp_expander_property(self, field_id: str, port: str, value: str) -> str:
        return self.send(f"SET DSP_EXP_PROP {field_id} {port} {value}")

    def get_dsp_expander_property(self, field_id: str, port: str) -> str:
        return self.send(f"GET DSP_EXP_PROP {field_id} {port}")

    def set_dsp_input_hpf(self, port: str, value: str) -> str:
        return self.send(f"SET DSP_IN_HPF {port} {value}")

    def get_dsp_input_hpf(self, port: str) -> str:
        return self.send(f"GET DSP_IN_HPF {port}")

    def set_dsp_input_hpf_property(self, port: str, value: str) -> str:
        return self.send(f"SET DSP_IN_HPF_PROP {port} {value}")

    def get_dsp_input_hpf_property(self, port: str) -> str:
        return self.send(f"GET DSP_IN_HPF_PROP {port}")

    def set_dsp_output_hpf(self, port: str, value: str) -> str:
        return self.send(f"SET DSP_OUT_HPF {port} {value}")

    def get_dsp_output_hpf(self, port: str) -> str:
        return self.send(f"GET DSP_OUT_HPF {port}")

    def set_dsp_output_hpf_property(self, port: str, value: str) -> str:
        return self.send(f"SET DSP_OUT_HPF_PROP {port} {value}")

    def get_dsp_output_hpf_property(self, port: str) -> str:
        return self.send(f"GET DSP_OUT_HPF_PROP {port}")

    def set_dsp_compressor(self, port: str, value: str) -> str:
        return self.send(f"SET DSP_COMP {port} {value}")

    def get_dsp_compressor(self, port: str) -> str:
        return self.send(f"GET DSP_COMP {port}")

    def set_dsp_compressor_property(self, field_id: str, port: str, value: str) -> str:
        return self.send(f"SET DSP_COMP_PROP {field_id} {port} {value}")

    def get_dsp_compressor_property(self, field_id: str, port: str) -> str:
        return self.send(f"GET DSP_COMP_PROP {field_id} {port}")

    def set_dsp_equalizer(self, port: str, value: str) -> str:
        return self.send(f"SET DSP_EQ {port} {value}")

    def get_dsp_equalizer(self, port: str) -> str:
        return self.send(f"GET DSP_EQ {port}")

    def set_dsp_equalizer_property(
        self, field: str, port: str, band: int, value: str
    ) -> str:
        return self.send(f"SET DSP_EQ_PROP {field} {port} {band} {value}")

    def get_dsp_equalizer_property(self, field: str, port: str, band: int) -> str:
        return self.send(f"GET DSP_EQ_PROP {field} {port} {band}")

    def set_dsp_lpf(self, port: str, value: str) -> str:
        return self.send(f"SET DSP_LPF {port} {value}")

    def get_dsp_lpf(self, port: str) -> str:
        return self.send(f"GET DSP_LPF {port}")

    def set_dsp_lpf_property(self, port: str, value: str) -> str:
        return self.send(f"SET DSP_LPF_PROP {port} {value}")

    def get_dsp_lpf_property(self, port: str) -> str:
        return self.send(f"GET DSP_LPF_PROP {port}")

    def set_dsp_duck(self, port: str, value: str) -> str:
        return self.send(f"SET DSP_DUCK {port} {value}")

    def get_dsp_duck(self, port: str) -> str:
        return self.send(f"GET DSP_DUCK {port}")

    def set_dsp_duck_property(self, field_id: str, port: str, value: str) -> str:
        return self.send(f"SET DSP_DUCK_PROP {field_id} {port} {value}")

    def get_dsp_duck_property(self, field_id: str, port: str) -> str:
        return self.send(f"GET DSP_DUCK_PROP {field_id} {port}")

    def set_dsp_duck_priority(self, port: str, value: str) -> str:
        return self.send(f"SET DSP_DUCK_PRI {port} {value}")

    def get_dsp_duck_priority(self, port: str) -> str:
        return self.send(f"GET DSP_DUCK_PRI {port}")

    def set_dsp_input_mute(self, port: str, value: str) -> str:
        return self.send(f"SET DSP_AUD_GAIN_MUTE {port} {value}")

    def get_dsp_input_mute(self, port: str) -> str:
        return self.send(f"GET DSP_AUD_GAIN_MUTE {port}")

    def set_dsp_input_gain(self, port: str, value: str) -> str:
        return self.send(f"SET DSP_AUD_GAIN {port} {value}")

    def get_dsp_input_gain(self, port: str) -> str:
        return self.send(f"GET DSP_AUD_GAIN {port}")

    def set_dsp_output_mute(self, port: str, value: str) -> str:
        return self.send(f"SET DSP_AUD_VOL_MUTE {port} {value}")

    def get_dsp_output_mute(self, port: str) -> str:
        return self.send(f"GET DSP_AUD_VOL_MUTE {port}")

    def set_dsp_output_volume(self, port: str, value: str) -> str:
        return self.send(f"SET DSP_AUD_VOL {port} {value}")

    def get_dsp_output_volume(self, port: str) -> str:
        return self.send(f"GET DSP_AUD_VOL {port}")

    def get_dsp_input_meter(self, port: str) -> str:
        return self.send(f"GET DSP_IN_METER {port}")

    def get_dsp_output_meter(self, port: str) -> str:
        return self.send(f"GET DSP_OUT_METER {port}")

    def set_dsp_link_lock(self, port: str, value: str) -> str:
        return self.send(f"SET DSP_LINK_LOCK {port} {value}")

    def get_dsp_link_lock(self, port: str) -> str:
        return self.send(f"GET DSP_LINK_LOCK {port}")

    def set_dsp_delay_enabled(self, port: str, value: str) -> str:
        return self.send(f"SET DSP_DELAY_EN {port} {value}")

    def get_dsp_delay_enabled(self, port: str) -> str:
        return self.send(f"GET DSP_DELAY_EN {port}")

    def set_dsp_delay(self, port: str, value: str) -> str:
        return self.send(f"SET DSP_DELAY {port} {value}")

    def get_dsp_delay(self, port: str) -> str:
        return self.send(f"GET DSP_DELAY {port}")

    # Input & Output / LED / MIC
    def get_amp_mode(self) -> str:
        return self.send("GET AMP_MODE")

    def set_audio_input_type(self, value: str) -> str:
        return self.send(f"SET AUDIN_TYPE {value}")

    def get_audio_input_type(self) -> str:
        return self.send("GET AUDIN_TYPE")

    def set_volume_step(self, value: int) -> str:
        return self.send(f"SET VOL_LEVEL_STEP {value}")

    def get_volume_step(self) -> str:
        return self.send("GET VOL_LEVEL_STEP")

    def set_led_brightness(self, value: str) -> str:
        return self.send(f"SET LED_BRIGHTNESS {value}")

    def get_led_brightness(self) -> str:
        return self.send("GET LED_BRIGHTNESS")

    def set_mic_phantom_power(self, channel: int, value: str) -> str:
        return self.send(f"SET MIC_PHA_PWR {channel} {value}")

    def get_mic_phantom_power(self, channel: int) -> str:
        return self.send(f"GET MIC_PHA_PWR {channel}")

    # System information
    def factory_reset(self) -> str:
        return self.send("RESET")

    def reboot(self) -> str:
        return self.send("REBOOT")

    def get_ip_address(self) -> str:
        return self.send("GET IPADDR")

    def set_ip_address(self, ip: str, mask: str, gateway: str) -> str:
        return self.send(f"SET IPADDR {ip} MASK {mask} GATEWAY {gateway}")

    def set_netcfg_mode(self, value: str) -> str:
        return self.send(f"SET NETCFG MODE {value}")

    def get_netcfg_mode(self) -> str:
        return self.send("GET NETCFG MODE")

    def get_firmware_version(self) -> str:
        return self.send("GET VER")

    def get_hardware_version(self) -> str:
        return self.send("GET HW_VER")

    def get_help(self) -> str:
        return self.send("help")

    # Security
    def set_https_status(self, value: str) -> str:
        return self.send(f"SET HTTPS {value}")

    def get_https_status(self) -> str:
        return self.send("GET HTTPS")

    def set_telnets_status(self, value: str) -> str:
        return self.send(f"SET TELNETS {value}")

    def get_telnets_status(self) -> str:
        return self.send("GET TELNETS")

    def set_api_password(
        self, old_password: str, new_password: str, verify_password: str
    ) -> str:
        return self.send(f"SET API_PWD {old_password} {new_password} {verify_password}")

    def set_ssh_status(self, value: str) -> str:
        return self.send(f"SET SSH {value}")

    def get_ssh_status(self) -> str:
        return self.send("GET SSH")

    def get_device_info(self) -> Dict[str, Any]:
        """Collect quick system info for test report header."""
        info: Dict[str, Any] = {"model": "AMP-240-000"}
        for key, func in [
            ("firmware", self.get_firmware_version),
            ("hardware", self.get_hardware_version),
            ("ip_address", self.get_ip_address),
            ("netcfg_mode", self.get_netcfg_mode),
        ]:
            try:
                info[key] = func()
            except Exception as exc:
                info[key] = f"Unavailable ({exc})"
        return info

    def test_all_get_commands(self, debug: bool = False) -> Dict[str, Any]:
        """
        Test all GET/read commands and print a clean report.
        """
        if debug:
            self.debug = True

        section_sep = "~" * 80
        block_sep = "-" * 60

        print("\nAMP240 Device Wrapper API Test\n")
        print(section_sep)
        print()
        print("DEVICE INFORMATION")
        print(section_sep)
        print()

        self._ensure_connected()
        info = self.get_device_info()
        print(f"Model: {info.get('model', 'Unknown')}")
        print(f"Firmware: {info.get('firmware', 'Unknown')}")
        print(f"Hardware: {info.get('hardware', 'Unknown')}")
        print(f"IP Address: {info.get('ip_address', 'Unknown')}")
        print(f"NetCfg Mode: {info.get('netcfg_mode', 'Unknown')}")
        print()

        get_methods = [
            (
                "get_dsp_mix",
                "Get DSP matrix crosspoint state",
                "GET DSP_MIX AMP LINE1",
                ("AMP", "LINE1"),
            ),
            (
                "get_dsp_expander",
                "Get DSP expander status",
                "GET DSP_EXP LINE1",
                ("LINE1",),
            ),
            (
                "get_dsp_expander_property",
                "Get DSP expander property",
                "GET DSP_EXP_PROP Attack LINE1",
                ("Attack", "LINE1"),
            ),
            (
                "get_dsp_input_hpf",
                "Get DSP input HPF status",
                "GET DSP_IN_HPF LINE1",
                ("LINE1",),
            ),
            (
                "get_dsp_input_hpf_property",
                "Get DSP input HPF property",
                "GET DSP_IN_HPF_PROP LINE1",
                ("LINE1",),
            ),
            (
                "get_dsp_output_hpf",
                "Get DSP output HPF status",
                "GET DSP_OUT_HPF AMP",
                ("AMP",),
            ),
            (
                "get_dsp_output_hpf_property",
                "Get DSP output HPF property",
                "GET DSP_OUT_HPF_PROP AMP",
                ("AMP",),
            ),
            (
                "get_dsp_compressor",
                "Get DSP compressor status",
                "GET DSP_COMP LINE1",
                ("LINE1",),
            ),
            (
                "get_dsp_compressor_property",
                "Get DSP compressor property",
                "GET DSP_COMP_PROP Attack LINE1",
                ("Attack", "LINE1"),
            ),
            ("get_dsp_equalizer", "Get DSP EQ status", "GET DSP_EQ AMP", ("AMP",)),
            (
                "get_dsp_equalizer_property",
                "Get DSP EQ property",
                "GET DSP_EQ_PROP level AMP 1",
                ("level", "AMP", 1),
            ),
            ("get_dsp_lpf", "Get DSP LPF status", "GET DSP_LPF AMP", ("AMP",)),
            (
                "get_dsp_lpf_property",
                "Get DSP LPF property",
                "GET DSP_LPF_PROP AMP",
                ("AMP",),
            ),
            ("get_dsp_duck", "Get DSP duck status", "GET DSP_DUCK AMP", ("AMP",)),
            (
                "get_dsp_duck_property",
                "Get DSP duck property",
                "GET DSP_DUCK_PROP Attack AMP",
                ("Attack", "AMP"),
            ),
            (
                "get_dsp_duck_priority",
                "Get DSP duck master",
                "GET DSP_DUCK_PRI AMP",
                ("AMP",),
            ),
            (
                "get_dsp_input_mute",
                "Get input mute status",
                "GET DSP_AUD_GAIN_MUTE LINE1",
                ("LINE1",),
            ),
            (
                "get_dsp_input_gain",
                "Get input gain",
                "GET DSP_AUD_GAIN LINE1",
                ("LINE1",),
            ),
            (
                "get_dsp_output_mute",
                "Get output mute status",
                "GET DSP_AUD_VOL_MUTE AMP",
                ("AMP",),
            ),
            (
                "get_dsp_output_volume",
                "Get output volume",
                "GET DSP_AUD_VOL AMP",
                ("AMP",),
            ),
            (
                "get_dsp_input_meter",
                "Read input meter",
                "GET DSP_IN_METER LINE1",
                ("LINE1",),
            ),
            (
                "get_dsp_output_meter",
                "Read output meter",
                "GET DSP_OUT_METER AMP",
                ("AMP",),
            ),
            (
                "get_dsp_link_lock",
                "Get DSP link lock status",
                "GET DSP_LINK_LOCK 1",
                ("1",),
            ),
            (
                "get_dsp_delay_enabled",
                "Get DSP delay enable",
                "GET DSP_DELAY_EN AMP",
                ("AMP",),
            ),
            ("get_dsp_delay", "Get DSP delay", "GET DSP_DELAY AMP", ("AMP",)),
            ("get_amp_mode", "Get amp mode", "GET AMP_MODE", ()),
            ("get_audio_input_type", "Get audio input type", "GET AUDIN_TYPE", ()),
            ("get_volume_step", "Get volume step", "GET VOL_LEVEL_STEP", ()),
            ("get_led_brightness", "Get LED brightness", "GET LED_BRIGHTNESS", ()),
            (
                "get_mic_phantom_power",
                "Get mic phantom power",
                "GET MIC_PHA_PWR 1",
                (1,),
            ),
            ("get_ip_address", "Get IP address", "GET IPADDR", ()),
            ("get_netcfg_mode", "Get netcfg mode", "GET NETCFG MODE", ()),
            ("get_firmware_version", "Get firmware version", "GET VER", ()),
            ("get_hardware_version", "Get hardware version", "GET HW_VER", ()),
            ("get_help", "Get API list", "help", ()),
            ("get_https_status", "Get HTTPS service status", "GET HTTPS", ()),
            ("get_telnets_status", "Get TELNETS service status", "GET TELNETS", ()),
            ("get_ssh_status", "Get SSH service status", "GET SSH", ()),
        ]

        print(f"Testing {len(get_methods)} get methods...")
        results = []
        success_count = 0
        failure_count = 0

        try:
            # No settings are altered by these GET tests; no restore actions required.
            for method_name, description, command, args in get_methods:
                print(section_sep)
                print(f"{method_name}: {description}")
                print(f"Command: {command}")
                print(block_sep)

                method = getattr(self, method_name)
                start_time = time.time()
                try:
                    result = method(*args)
                    execution_time = round(time.time() - start_time, 3)
                    ok = result is not None and str(result).strip() != ""
                    status = "SUCCESS" if ok else "FAILED (empty response)"
                    if ok:
                        success_count += 1
                    else:
                        failure_count += 1
                except Exception as exc:
                    execution_time = round(time.time() - start_time, 3)
                    result = f"Exception: {exc}"
                    status = "FAILED (exception)"
                    failure_count += 1

                print(f"Status: {status}")
                print(f"Response: {result}")
                print(f"Response time: {execution_time}s")
                print(block_sep)

                results.append(
                    {
                        "method": method_name,
                        "command": command,
                        "description": description,
                        "success": status == "SUCCESS",
                        "execution_time": execution_time,
                        "result": result,
                        "status": status,
                    }
                )
        finally:
            self.disconnect()

        total = len(get_methods)
        success_rate = round((success_count / total) * 100, 1) if total else 0.0
        successful_results = [r for r in results if r["success"]]
        timing_pool = successful_results if successful_results else results

        if timing_pool:
            fastest = min(timing_pool, key=lambda x: x["execution_time"])
            slowest = max(timing_pool, key=lambda x: x["execution_time"])
            average_response_time = round(
                sum(r["execution_time"] for r in timing_pool) / len(timing_pool), 3
            )
            fastest_response_time = fastest["execution_time"]
            slowest_response_time = slowest["execution_time"]
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
        print(f"Successful: {success_count}")
        print(f"Failed: {failure_count}")
        print(f"Success rate: {success_rate}%")
        print(f"Average API response time: {average_response_time}s")
        print(f"Fastest API response time: {fastest_response_time}s")
        print(f"Fastest API call: {fastest_call}")
        print(f"Slowest API response time: {slowest_response_time}s")
        print(f"Slowest API call: {slowest_call}")

        return {
            "success": success_count,
            "failure": failure_count,
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
    amp = AMP240Device(host="10.0.30.59", debug=False)
    test_results = amp.test_all_get_commands()
    print(f"\nTest completed. Success rate: {test_results['success_rate']}%")
