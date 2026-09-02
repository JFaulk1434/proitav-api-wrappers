"""Standalone GET-style API test for Vanco EVOIP encoder/decoder devices."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import socket
import sys
import time


CURRENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = CURRENT_DIR.parent.parent

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from test_report_utils import run_get_style_tests  # noqa: E402


# Local run defaults (SC010-style): edit these, then run file directly.
DEFAULT_HOST = "10.0.30.42"
DEFAULT_PORT = 24
DEFAULT_TIMEOUT = 4.0
DEFAULT_ROLE = "tx"  # tx | rx | both
DEFAULT_USERNAME = "root"
DEFAULT_PASSWORD: str | None = None
DEFAULT_DEBUG = False
DEFAULT_MARKDOWN = False


class EVOIPDevice:
    """Minimal telnet client exposing GET-style EVOIP methods for validation."""

    def __init__(
        self,
        host: str,
        *,
        port: int = 23,
        timeout: float = 4.0,
        debug: bool = False,
        username: str | None = None,
        password: str | None = None,
        prompt: str = "/ #",
    ) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self.debug = debug
        self.username = username
        self.password = password
        self.prompt = prompt
        self.sock: socket.socket | None = None

    def connect(self) -> bool:
        """Open telnet session and perform optional login."""
        try:
            self.sock = socket.create_connection((self.host, self.port), self.timeout)
            self.sock.settimeout(self.timeout)
            banner = self._read_until_prompt(timeout_override=1.0)
            self._maybe_login(banner)
            return True
        except Exception:
            self.sock = None
            return False

    def _maybe_login(self, initial: str) -> None:
        """Best-effort login for devices that prompt for credentials."""
        if not self.sock:
            return

        if not self.username and not self.password:
            return

        login_text = initial
        if "login:" in login_text.lower() and self.username:
            self._send_line(self.username)
            time.sleep(0.2)
            login_text += self._read_until_prompt(timeout_override=1.0)

        if "password:" in login_text.lower() and self.password is not None:
            self._send_line(self.password)
            time.sleep(0.2)
            self._read_until_prompt(timeout_override=1.0)

    def disconnect(self) -> None:
        if self.sock:
            self.sock.close()
            self.sock = None

    @staticmethod
    def _handle_telnet_negotiation(chunk: bytes) -> tuple[bytes, list[bytes]]:
        """Strip telnet negotiation bytes and return required replies."""
        iac = 255
        do = 253
        dont = 254
        will = 251
        wont = 252
        sb = 250
        se = 240

        out = bytearray()
        replies: list[bytes] = []
        i = 0
        while i < len(chunk):
            b = chunk[i]
            if b != iac:
                out.append(b)
                i += 1
                continue

            if i + 1 >= len(chunk):
                break
            cmd = chunk[i + 1]

            if cmd == iac:
                out.append(iac)
                i += 2
                continue

            if cmd in (do, dont, will, wont):
                if i + 2 >= len(chunk):
                    break
                opt = chunk[i + 2]
                if cmd == do:
                    replies.append(bytes([iac, wont, opt]))
                elif cmd == will:
                    replies.append(bytes([iac, dont, opt]))
                i += 3
                continue

            if cmd == sb:
                i += 2
                while i + 1 < len(chunk):
                    if chunk[i] == iac and chunk[i + 1] == se:
                        i += 2
                        break
                    i += 1
                continue

            i += 2

        return bytes(out), replies

    def _send_line(self, line: str) -> None:
        if not self.sock:
            raise RuntimeError("Device is not connected.")
        payload = (line + "\n").encode("ascii", errors="ignore")
        self.sock.sendall(payload)
        if self.debug:
            print(f"TX: {line}")

    def _read_until_prompt(self, timeout_override: float | None = None) -> str:
        if not self.sock:
            return ""

        deadline = time.time() + (
            timeout_override if timeout_override is not None else self.timeout
        )
        collected = bytearray()
        prompt_bytes = self.prompt.encode("ascii")

        while time.time() < deadline:
            try:
                chunk = self.sock.recv(4096)
            except socket.timeout:
                break

            if not chunk:
                break

            cleaned, replies = self._handle_telnet_negotiation(chunk)
            for reply in replies:
                self.sock.sendall(reply)
            collected.extend(cleaned)

            if prompt_bytes in collected:
                break

        text = collected.decode("utf-8", errors="ignore")
        if self.debug and text.strip():
            print(f"RX: {text.strip()}")
        return text

    def _run(self, command: str) -> str:
        """Execute one command and return cleaned output text."""
        if not self.sock:
            raise RuntimeError("Device is not connected.")

        self._send_line(command)
        text = self._read_until_prompt()

        lines = [line.rstrip() for line in text.splitlines() if line.strip()]
        cleaned: list[str] = []
        for line in lines:
            line_no_prompt = line.replace(self.prompt, "").strip()
            if not line_no_prompt:
                continue
            if line_no_prompt == command.strip():
                continue
            cleaned.append(line_no_prompt)

        if not cleaned:
            return ""

        return re.sub(r"\s+", " ", " | ".join(cleaned)).strip()

    # Shared command(s)
    def get_firmware_version(self) -> str:
        return self._run("cat /etc/version")

    # TX command(s)
    def get_hdcp_enabled(self) -> str:
        return self._run("gbconfig --show --hdcp-enable")

    # RX command(s)
    def get_source_select(self) -> str:
        return self._run("gbconfig --show --source-select")

    def get_audio_source_select(self) -> str:
        return self._run("gbconfig --show --asource-select")

    def get_serial_source_select(self) -> str:
        return self._run("gbconfig --show --ssource-select")

    def get_video_source_select(self) -> str:
        return self._run("gbconfig --show --vsource-select")

    def get_output_color_space(self) -> str:
        return self._run("gbparam g fource_output_color_space")

    def get_no_source_close_screen(self) -> str:
        return self._run("gbparam g no_source_close_screen")

    def get_display_edid(self) -> str:
        return self._run("cat /var/tmpfs/monitor_info")


def build_get_commands(device_role: str) -> list[dict[str, object]]:
    """Build role-aware command list for encoder/decoder validation."""
    commands: list[dict[str, object]] = [
        {
            "method": "get_firmware_version",
            "description": "Get firmware and build version",
            "command": "cat /etc/version",
            "kwargs": {},
        },
    ]

    if device_role in {"tx", "both"}:
        commands.append(
            {
                "method": "get_hdcp_enabled",
                "description": "Get TX HDCP enable state",
                "command": "gbconfig --show --hdcp-enable",
                "kwargs": {},
            }
        )

    if device_role in {"rx", "both"}:
        commands.extend(
            [
                {
                    "method": "get_source_select",
                    "description": "Get whole source mapping to RX",
                    "command": "gbconfig --show --source-select",
                    "kwargs": {},
                },
                {
                    "method": "get_audio_source_select",
                    "description": "Get audio source mapping to RX",
                    "command": "gbconfig --show --asource-select",
                    "kwargs": {},
                },
                {
                    "method": "get_serial_source_select",
                    "description": "Get RS232 source mapping to RX",
                    "command": "gbconfig --show --ssource-select",
                    "kwargs": {},
                },
                {
                    "method": "get_video_source_select",
                    "description": "Get video source mapping to RX",
                    "command": "gbconfig --show --vsource-select",
                    "kwargs": {},
                },
                {
                    "method": "get_output_color_space",
                    "description": "Get forced output color space",
                    "command": "gbparam g fource_output_color_space",
                    "kwargs": {},
                },
                {
                    "method": "get_no_source_close_screen",
                    "description": "Get no-source screen close behavior",
                    "command": "gbparam g no_source_close_screen",
                    "kwargs": {},
                },
                {
                    "method": "get_display_edid",
                    "description": "Get display EDID from RX HDMI output",
                    "command": "cat /var/tmpfs/monitor_info",
                    "kwargs": {},
                },
            ]
        )

    return commands


def setup_device(_device: EVOIPDevice) -> dict[str, str]:
    return {
        "note": "Read-only GET validation; no device settings changed and no restore required."
    }


def teardown_device(_device: EVOIPDevice, _saved_state: object) -> None:
    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run GET-style EVOIP encoder/decoder API validation."
    )
    parser.add_argument("host", nargs="?", default=DEFAULT_HOST, help="Device host/IP")
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"Telnet port (default: {DEFAULT_PORT})",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help=f"Telnet read timeout in seconds (default: {DEFAULT_TIMEOUT})",
    )
    parser.add_argument(
        "--role",
        choices=["tx", "rx", "both"],
        default=DEFAULT_ROLE,
        help=f"Device role to choose GET command set (default: {DEFAULT_ROLE})",
    )
    parser.add_argument(
        "--username",
        default=DEFAULT_USERNAME,
        help=f"Optional telnet username (default: {DEFAULT_USERNAME})",
    )
    parser.add_argument(
        "--password",
        default=DEFAULT_PASSWORD,
        help="Optional telnet password",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=DEFAULT_DEBUG,
        help="Enable telnet debug output",
    )
    parser.add_argument(
        "--markdown",
        action="store_true",
        default=DEFAULT_MARKDOWN,
        help="Print markdown-formatted report output",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    device = EVOIPDevice(
        args.host,
        port=args.port,
        timeout=args.timeout,
        debug=args.debug,
        username=args.username,
        password=args.password,
    )

    get_commands = build_get_commands(args.role)
    info_queries = [
        ("Model", f"Vanco EVOIP ({args.role.upper()})"),
        ("Host", args.host),
        ("Port", str(args.port)),
        ("Firmware Version", "See get_firmware_version result below"),
    ]

    summary = run_get_style_tests(
        device=device,
        model="Vanco EVOIPRXG/EVOIPTXG",
        get_commands=get_commands,
        info_queries=info_queries,
        markdown_output=args.markdown,
        setup_hook=setup_device,
        teardown_hook=teardown_device,
    )

    print(f"\nTest completed. Success rate: {summary['success_rate']}%")
    return 0 if summary["failure"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
