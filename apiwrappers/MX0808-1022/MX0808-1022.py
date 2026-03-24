"""Python wrapper for MX0808-1022."""

from telnetlib import Telnet
import select
import time


class MX0808_1022_Device:
    """Wrapper for the MX0808-1022 matrix switcher."""

    INPUT_PREFIX = "hdmiin"
    OUTPUT_PREFIX = "hdmiout"
    AUDIO_OUTPUT_PREFIX = "audioout"
    INPUT_RANGE = range(1, 9)
    OUTPUT_RANGE = range(1, 9)
    IR_MODES = {"all", "mode1", "mode2"}
    CEC_COMMAND_TYPES = {"pwron", "pwroff"}
    HDCP_MODES = {"follow", "hdcp1.4", "hdcp2.2", "off"}

    def __init__(self, ip, port=23, timeout=2.0, debug=False):
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.debug = debug
        self.tn = None

    def _clean_response(self, response: str) -> str:
        """Normalize telnet responses by removing prompts and blank lines."""
        cleaned_lines = []
        for line in response.replace("\r", "").split("\n"):
            stripped = line.strip()
            if not stripped or stripped == ">":
                continue
            if stripped.startswith(">"):
                stripped = stripped[1:].strip()
            if stripped:
                cleaned_lines.append(stripped)
        return "\n".join(cleaned_lines)

    def _drain_socket(self):
        """Clear unread telnet output before sending a new command."""
        if self.tn is None or self.tn.get_socket() is None:
            return

        while True:
            ready, _, _ = select.select([self.tn.get_socket()], [], [], 0)
            if not ready:
                break
            if not self.tn.read_very_eager():
                break

    def _read_until_idle(self, timeout=None, idle_window=0.15) -> str:
        """Read until the telnet socket becomes idle."""
        timeout = self.timeout if timeout is None else timeout
        start_time = time.time()
        last_data_time = None
        response_data = b""

        while (time.time() - start_time) < timeout:
            wait_time = idle_window if last_data_time is not None else 0.1
            ready, _, _ = select.select([self.tn.get_socket()], [], [], wait_time)
            if ready:
                data = self.tn.read_very_eager()
                if data:
                    response_data += data
                    last_data_time = time.time()
                    continue
            if last_data_time is not None and (time.time() - last_data_time) >= idle_window:
                break

        return self._clean_response(response_data.decode(errors="replace"))

    def _normalize_io(self, value, *, prefix: str, valid_range, allow_all=False, allow_zero=False) -> str:
        """Normalize integer or vendor token parameters into API command tokens."""
        if isinstance(value, int):
            if allow_zero and value == 0:
                return f"{prefix}0"
            if value not in valid_range:
                range_label = f"{min(valid_range)}-{max(valid_range)}"
                if allow_zero:
                    range_label = f"0 or {range_label}"
                raise ValueError(f"Value must be {range_label}.")
            return f"{prefix}{value}"

        text = str(value).strip().lower()
        if allow_all and text == "all":
            return "all"
        if allow_zero and text == f"{prefix}0":
            return text
        valid_tokens = {f"{prefix}{number}" for number in valid_range}
        if text not in valid_tokens:
            raise ValueError(f"Unsupported value '{value}'.")
        return text

    def _normalize_on_off(self, state) -> str:
        """Convert booleans or text into on/off tokens."""
        if isinstance(state, bool):
            return "on" if state else "off"
        text = str(state).strip().lower()
        if text not in {"on", "off"}:
            raise ValueError("State must be 'on' or 'off'.")
        return text

    def _normalize_audio_source(self, source) -> str:
        """Normalize the MX0808-1022 audio source selector."""
        text = str(source).strip().lower()
        if text not in {"hdmi", "arc"}:
            raise ValueError("Audio source must be 'hdmi' or 'arc'.")
        return text

    def _normalize_cec_command_type(self, command_type) -> str:
        """Normalize CEC command type."""
        text = str(command_type).strip().lower()
        if text not in self.CEC_COMMAND_TYPES:
            raise ValueError("Command type must be 'pwron' or 'pwroff'.")
        return text

    def _normalize_ir_mode(self, mode) -> str:
        """Normalize IR mode token."""
        text = str(mode).strip().lower()
        if text not in self.IR_MODES:
            raise ValueError("IR mode must be one of: all, mode1, mode2.")
        return text

    def _normalize_hdcp_mode(self, mode) -> str:
        """Normalize output HDCP mode token."""
        text = str(mode).strip().lower()
        if text not in self.HDCP_MODES:
            raise ValueError("HDCP mode must be one of: follow, hdcp1.4, hdcp2.2, off.")
        return text

    def _normalize_edid_block(self, block) -> str:
        """Normalize EDID block name."""
        text = str(block).strip().lower()
        if text not in {"block0", "block1"}:
            raise ValueError("EDID block must be 'block0' or 'block1'.")
        return text

    def _normalize_hex_payload(self, payload) -> str:
        """Normalize a hex payload for CEC or EDID commands."""
        if isinstance(payload, bytes):
            tokens = [f"{byte:02X}" for byte in payload]
        else:
            cleaned = str(payload).replace(",", " ").replace("0x", " ").replace("0X", " ")
            tokens = [token for token in cleaned.split() if token]
        if not tokens:
            raise ValueError("Hex payload cannot be empty.")
        normalized = []
        for token in tokens:
            if len(token) != 2:
                raise ValueError("Hex payload must use two-character byte tokens.")
            int(token, 16)
            normalized.append(token.upper())
        return " ".join(normalized)

    def connect(self):
        """Open the telnet session."""
        if self.tn is None:
            self.tn = Telnet()
            if self.debug:
                self.tn.set_debuglevel(1)

        try:
            self.tn.open(self.ip, self.port, timeout=self.timeout)
            self.tn.read_until(b">", timeout=self.timeout)
            return True
        except Exception as exc:
            print(f"Failed to connect to {self.ip}: {exc}")
            self.tn = None
            return False

    def ensure_connection(self):
        """Connect if the session is not already open."""
        if self.tn is None or self.tn.get_socket() is None:
            return self.connect()
        return True

    def send(self, message: str, timeout=None) -> str:
        """Send one command and return the cleaned response."""
        if not self.ensure_connection():
            return "Failed to establish connection"

        try:
            self._drain_socket()
            self.tn.write(f"{message}\n".encode())
            return self._read_until_idle(timeout=timeout)
        except Exception as exc:
            print(f"Failed to send command '{message}' to {self.ip}: {exc}")
            self.disconnect()
            return "Failed to send command"

    def send_long(self, message: str, timeout: float = 4.0) -> str:
        """Send a command that can return a longer multi-line response."""
        return self.send(message, timeout=timeout)

    def disconnect(self):
        """Close the telnet session."""
        if self.tn is not None:
            try:
                self.tn.close()
            except Exception as exc:
                print(f"Error closing Telnet connection: {exc}")
            finally:
                self.tn = None

    def set_switch(self, input_source, output):
        """Route one HDMI input to one HDMI output."""
        in_token = self._normalize_io(
            input_source,
            prefix=self.INPUT_PREFIX,
            valid_range=self.INPUT_RANGE,
            allow_zero=True,
        )
        out_token = self._normalize_io(
            output,
            prefix=self.OUTPUT_PREFIX,
            valid_range=self.OUTPUT_RANGE,
        )
        return self.send(f"SET SW {in_token} {out_token}")

    def set_switch_all(self, input_source):
        """Route one HDMI input to all HDMI outputs."""
        in_token = self._normalize_io(
            input_source,
            prefix=self.INPUT_PREFIX,
            valid_range=self.INPUT_RANGE,
            allow_zero=True,
        )
        return self.send(f"SET SW {in_token} all")

    def get_mapping(self, output):
        """Get the routed input for one HDMI output."""
        out_token = self._normalize_io(
            output,
            prefix=self.OUTPUT_PREFIX,
            valid_range=self.OUTPUT_RANGE,
        )
        return self.send(f"GET MP {out_token}")

    def get_mapping_all(self):
        """Get routed input mappings for all HDMI outputs."""
        return self.send("GET MP all")

    def set_audio_switch(self, source, output):
        """Select the HDMI or ARC audio source for one analog audio output."""
        source_token = self._normalize_audio_source(source)
        out_token = self._normalize_io(
            output,
            prefix=self.AUDIO_OUTPUT_PREFIX,
            valid_range=self.OUTPUT_RANGE,
        )
        return self.send(f"SET AUDIOSW {source_token} {out_token}")

    def get_audio_mapping(self, output):
        """Get the HDMI or ARC source mapped to one analog audio output."""
        out_token = self._normalize_io(
            output,
            prefix=self.AUDIO_OUTPUT_PREFIX,
            valid_range=self.OUTPUT_RANGE,
        )
        return self.send(f"GET AUDIOMP {out_token}")

    def set_cec_power(self, output, state):
        """Send a CEC power command to one or all HDMI outputs."""
        out_token = self._normalize_io(
            output,
            prefix=self.OUTPUT_PREFIX,
            valid_range=self.OUTPUT_RANGE,
            allow_all=True,
        )
        state_token = self._normalize_on_off(state)
        return self.send(f"SET CEC_PWR {out_token} {state_token}")

    def set_cec_auto(self, output, state):
        """Enable or disable automatic CEC power handling."""
        out_token = self._normalize_io(
            output,
            prefix=self.OUTPUT_PREFIX,
            valid_range=self.OUTPUT_RANGE,
        )
        state_token = self._normalize_on_off(state)
        return self.send(f"SET AUTOCEC_FN {out_token} {state_token}")

    def get_cec_auto(self, output):
        """Get the automatic CEC power state for one HDMI output."""
        out_token = self._normalize_io(
            output,
            prefix=self.OUTPUT_PREFIX,
            valid_range=self.OUTPUT_RANGE,
        )
        return self.send(f"GET AUTOCEC_FN {out_token}")

    def set_cec_delay(self, output, minutes: int):
        """Set the automatic CEC power-off delay in minutes."""
        out_token = self._normalize_io(
            output,
            prefix=self.OUTPUT_PREFIX,
            valid_range=self.OUTPUT_RANGE,
        )
        if not isinstance(minutes, int) or not 0 <= minutes <= 30:
            raise ValueError("CEC delay must be an integer between 0 and 30.")
        return self.send(f"SET AUTOCEC_D {out_token} {minutes}")

    def get_cec_delay(self, output):
        """Get the automatic CEC power-off delay for one HDMI output."""
        out_token = self._normalize_io(
            output,
            prefix=self.OUTPUT_PREFIX,
            valid_range=self.OUTPUT_RANGE,
        )
        return self.send(f"GET AUTOCEC_D {out_token}")

    def set_cec_command(self, output, command_type, hex_payload):
        """Store a custom power-on or power-off CEC command."""
        out_token = self._normalize_io(
            output,
            prefix=self.OUTPUT_PREFIX,
            valid_range=self.OUTPUT_RANGE,
        )
        command_token = self._normalize_cec_command_type(command_type)
        payload = self._normalize_hex_payload(hex_payload)
        return self.send(f"SET CECCMD_EDIT {out_token} {command_token} {payload}")

    def get_cec_command(self, output, command_type):
        """Read a stored custom power-on or power-off CEC command."""
        out_token = self._normalize_io(
            output,
            prefix=self.OUTPUT_PREFIX,
            valid_range=self.OUTPUT_RANGE,
        )
        command_token = self._normalize_cec_command_type(command_type)
        return self.send(f"GET CECCMD_EDIT {out_token} {command_token}")

    def send_cec_command(self, output, hex_payload):
        """Send a direct CEC command to one HDMI output."""
        out_token = self._normalize_io(
            output,
            prefix=self.OUTPUT_PREFIX,
            valid_range=self.OUTPUT_RANGE,
        )
        payload = self._normalize_hex_payload(hex_payload)
        return self.send(f"SET CEC_CMD {out_token} {payload}")

    def set_hdcp_support(self, input_number, state):
        """Enable or disable input HDCP support."""
        in_token = self._normalize_io(
            input_number,
            prefix=self.INPUT_PREFIX,
            valid_range=self.INPUT_RANGE,
        )
        state_token = self._normalize_on_off(state)
        return self.send(f"SET HDCP_S {in_token} {state_token}")

    def get_hdcp_support(self, input_number):
        """Get the input HDCP support state."""
        in_token = self._normalize_io(
            input_number,
            prefix=self.INPUT_PREFIX,
            valid_range=self.INPUT_RANGE,
        )
        return self.send(f"GET HDCP_S {in_token}")

    def set_edid(self, input_number, profile: int):
        """Assign an EDID preset to one HDMI input."""
        in_token = self._normalize_io(
            input_number,
            prefix=self.INPUT_PREFIX,
            valid_range=self.INPUT_RANGE,
        )
        if not isinstance(profile, int) or not 1 <= profile <= 27:
            raise ValueError("EDID profile must be an integer between 1 and 27.")
        return self.send(f"SET EDID {in_token} {profile}")

    def get_edid_all(self):
        """Get EDID preset assignments for all inputs."""
        return self.send("GET EDID all")

    def get_edid(self, input_number):
        """Get the EDID preset assigned to one HDMI input."""
        in_token = self._normalize_io(
            input_number,
            prefix=self.INPUT_PREFIX,
            valid_range=self.INPUT_RANGE,
        )
        return self.send(f"GET EDID {in_token}")

    def write_edid(self, input_number, block, hex_payload):
        """Write EDID data to one HDMI input block."""
        in_token = self._normalize_io(
            input_number,
            prefix=self.INPUT_PREFIX,
            valid_range=self.INPUT_RANGE,
        )
        block_token = self._normalize_edid_block(block)
        payload = self._normalize_hex_payload(hex_payload)
        return self.send(f"SET EDID_W {in_token} {block_token} {payload}")

    def read_edid(self, output):
        """Read both EDID blocks from one HDMI output."""
        out_token = self._normalize_io(
            output,
            prefix=self.OUTPUT_PREFIX,
            valid_range=self.OUTPUT_RANGE,
        )
        return self.send_long(f"GET EDID_R {out_token}", timeout=max(self.timeout, 3.0))

    def factory_reset(self):
        """Reset the device to factory defaults."""
        return self.send("RESET")

    def reboot(self):
        """Reboot the device."""
        return self.send("REBOOT")

    def set_ir_mode(self, mode):
        """Set the IR system code mode."""
        return self.send(f"SET IR_SC {self._normalize_ir_mode(mode)}")

    def get_ir_mode(self):
        """Get the IR system code mode."""
        return self.send("GET IR_SC")

    def get_api_list(self):
        """Get the device help output."""
        return self.send_long("help", timeout=max(self.timeout, 4.0))

    def get_ipaddr(self):
        """Get the device IP address."""
        return self.send("GET IPADDR")

    def standby(self):
        """Put the device into standby."""
        return self.send("STANDBY")

    def wake(self):
        """Wake the device from standby."""
        return self.send("WAKE")

    def get_standby(self):
        """Get standby or wake status."""
        return self.send("GET STANDBY")

    def get_version(self):
        """Get the firmware version."""
        return self.send("GET VER")

    def save_preset(self, slot: int):
        """Save a preset scene."""
        if not isinstance(slot, int) or slot not in {1, 2, 3}:
            raise ValueError("Preset slot must be 1, 2, or 3.")
        return self.send(f"SAVE PRESET {slot}")

    def restore_preset(self, slot: int):
        """Restore a preset scene."""
        if not isinstance(slot, int) or slot not in {1, 2, 3}:
            raise ValueError("Preset slot must be 1, 2, or 3.")
        return self.send(f"RESTORE PRESET {slot}")

    def set_output_hdcp_mode(self, output, mode):
        """Set output HDCP handling for one output or all outputs."""
        out_token = self._normalize_io(
            output,
            prefix=self.OUTPUT_PREFIX,
            valid_range=self.OUTPUT_RANGE,
            allow_all=True,
        )
        mode_token = self._normalize_hdcp_mode(mode)
        return self.send(f"SET HDCP {out_token} {mode_token}")

    def get_output_hdcp_mode(self, output):
        """Get output HDCP handling for one output or all outputs."""
        out_token = self._normalize_io(
            output,
            prefix=self.OUTPUT_PREFIX,
            valid_range=self.OUTPUT_RANGE,
            allow_all=True,
        )
        return self.send(f"GET HDCP {out_token}")

    def get_input_connection(self, input_number):
        """Get the physical connection state of one video input."""
        in_token = self._normalize_io(
            input_number,
            prefix="in",
            valid_range=self.INPUT_RANGE,
        )
        return self.send(f"GET VIDIN_CONNECT {in_token}")

    def get_input_signal(self, input_number):
        """Get signal detect state for one video input."""
        in_token = self._normalize_io(
            input_number,
            prefix="in",
            valid_range=self.INPUT_RANGE,
        )
        return self.send(f"GET VIDIN_SIG {in_token}")

    def get_input_video(self, input_number):
        """Get video format details for one input."""
        in_token = self._normalize_io(
            input_number,
            prefix="in",
            valid_range=self.INPUT_RANGE,
        )
        return self.send(f"GET VIDIN_FORMAT {in_token}")

    def get_input_audio(self, input_number):
        """Get audio format details for one input."""
        in_token = self._normalize_io(
            input_number,
            prefix="in",
            valid_range=self.INPUT_RANGE,
        )
        return self.send(f"GET AUDIN_FORMAT {in_token}")

    def get_input_hdcp(self, input_number):
        """Get HDCP version detected on one input."""
        in_token = self._normalize_io(
            input_number,
            prefix="in",
            valid_range=self.INPUT_RANGE,
        )
        return self.send(f"GET VIDIN_HDCP {in_token}")

    def get_output_connection(self, output):
        """Get the physical connection state of one video output."""
        out_token = self._normalize_io(
            output,
            prefix="out",
            valid_range=self.OUTPUT_RANGE,
        )
        return self.send(f"GET VIDOUT_CONNECT {out_token}")

    def get_output_signal(self, output):
        """Get signal detect state for one video output."""
        out_token = self._normalize_io(
            output,
            prefix="out",
            valid_range=self.OUTPUT_RANGE,
        )
        return self.send(f"GET VIDOUT_SIG {out_token}")

    def get_output_video(self, output):
        """Get video format details for one output."""
        out_token = self._normalize_io(
            output,
            prefix="out",
            valid_range=self.OUTPUT_RANGE,
        )
        return self.send(f"GET VIDOUT_FORMAT {out_token}")

    def get_output_audio(self, output):
        """Get audio format details for one output."""
        out_token = self._normalize_io(
            output,
            prefix="out",
            valid_range=self.OUTPUT_RANGE,
        )
        return self.send(f"GET AUDOUT_FORMAT {out_token}")

    def get_output_hdcp(self, output):
        """Get HDCP version detected on one output."""
        out_token = self._normalize_io(
            output,
            prefix="out",
            valid_range=self.OUTPUT_RANGE,
        )
        return self.send(f"GET VIDOUT_HDCP {out_token}")


def main():
    print("This wrapper is intended to be imported by the standalone test script.")


if __name__ == "__main__":
    main()
