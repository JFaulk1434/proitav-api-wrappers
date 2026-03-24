"""Standalone GET-style API test for MX0808-1022.

Run this file directly from Cursor/VSCode. The device settings are intentionally
kept at the top of the file so they are visible immediately.
"""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys


DEVICE_IP = "10.0.50.19"
PORT = 23
TIMEOUT = 2.0
DEBUG = False
MARKDOWN_OUTPUT = True


CURRENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = CURRENT_DIR.parent.parent
WRAPPER_PATH = CURRENT_DIR / "MX0808-1022.py"

if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from test_report_utils import run_get_style_tests


def load_wrapper_class():
    """Load the wrapper module from the local file path."""
    spec = spec_from_file_location("MX0808-1022_module", WRAPPER_PATH)
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return getattr(module, "MX0808_1022_Device")


WRAPPER_CLASS = load_wrapper_class()


GET_COMMANDS = [
    {
        "method": "get_version",
        "description": "Get firmware version",
        "command": "GET VER",
        "kwargs": {},
    },
    {
        "method": "get_ipaddr",
        "description": "Get device IP address",
        "command": "GET IPADDR",
        "kwargs": {},
    },
    {
        "method": "get_standby",
        "description": "Get standby state",
        "command": "GET STANDBY",
        "kwargs": {},
    },
    {
        "method": "get_ir_mode",
        "description": "Get IR system code mode",
        "command": "GET IR_SC",
        "kwargs": {},
    },
    {
        "method": "get_mapping",
        "description": "Get routed input for HDMI output 1",
        "command": "GET MP hdmiout1",
        "kwargs": {"output": 1},
    },
    {
        "method": "get_mapping_all",
        "description": "Get routed inputs for all HDMI outputs",
        "command": "GET MP all",
        "kwargs": {},
    },
    {
        "method": "get_audio_mapping",
        "description": "Get analog audio source for audio output 1",
        "command": "GET AUDIOMP audioout1",
        "kwargs": {"output": 1},
    },
    {
        "method": "get_cec_auto",
        "description": "Get automatic CEC power state for HDMI output 1",
        "command": "GET AUTOCEC_FN hdmiout1",
        "kwargs": {"output": 1},
    },
    {
        "method": "get_cec_delay",
        "description": "Get automatic CEC power delay for HDMI output 1",
        "command": "GET AUTOCEC_D hdmiout1",
        "kwargs": {"output": 1},
    },
    {
        "method": "get_cec_command",
        "description": "Get stored CEC power-on command for HDMI output 1",
        "command": "GET CECCMD_EDIT hdmiout1 pwron",
        "kwargs": {"output": 1, "command_type": "pwron"},
    },
    {
        "method": "get_hdcp_support",
        "description": "Get HDCP support state for HDMI input 1",
        "command": "GET HDCP_S hdmiin1",
        "kwargs": {"input_number": 1},
    },
    {
        "method": "get_edid_all",
        "description": "Get EDID preset assignments for all inputs",
        "command": "GET EDID all",
        "kwargs": {},
    },
    {
        "method": "get_edid",
        "description": "Get EDID preset assignment for HDMI input 1",
        "command": "GET EDID hdmiin1",
        "kwargs": {"input_number": 1},
    },
    {
        "method": "read_edid",
        "description": "Read EDID blocks from HDMI output 1",
        "command": "GET EDID_R hdmiout1",
        "kwargs": {"output": 1},
    },
    {
        "method": "get_output_hdcp_mode",
        "description": "Get output HDCP mode for HDMI output 1",
        "command": "GET HDCP hdmiout1",
        "kwargs": {"output": 1},
    },
    {
        "method": "get_input_connection",
        "description": "Get physical connection state for input 1",
        "command": "GET VIDIN_CONNECT in1",
        "kwargs": {"input_number": 1},
    },
    {
        "method": "get_input_signal",
        "description": "Get signal detect state for input 1",
        "command": "GET VIDIN_SIG in1",
        "kwargs": {"input_number": 1},
    },
    {
        "method": "get_input_video",
        "description": "Get video format for input 1",
        "command": "GET VIDIN_FORMAT in1",
        "kwargs": {"input_number": 1},
    },
    {
        "method": "get_input_audio",
        "description": "Get audio format for input 1",
        "command": "GET AUDIN_FORMAT in1",
        "kwargs": {"input_number": 1},
    },
    {
        "method": "get_input_hdcp",
        "description": "Get HDCP version for input 1",
        "command": "GET VIDIN_HDCP in1",
        "kwargs": {"input_number": 1},
    },
    {
        "method": "get_output_connection",
        "description": "Get physical connection state for output 1",
        "command": "GET VIDOUT_CONNECT out1",
        "kwargs": {"output": 1},
    },
    {
        "method": "get_output_signal",
        "description": "Get signal detect state for output 1",
        "command": "GET VIDOUT_SIG out1",
        "kwargs": {"output": 1},
    },
    {
        "method": "get_output_video",
        "description": "Get video format for output 1",
        "command": "GET VIDOUT_FORMAT out1",
        "kwargs": {"output": 1},
    },
    {
        "method": "get_output_audio",
        "description": "Get audio format for output 1",
        "command": "GET AUDOUT_FORMAT out1",
        "kwargs": {"output": 1},
    },
    {
        "method": "get_output_hdcp",
        "description": "Get HDCP version for output 1",
        "command": "GET VIDOUT_HDCP out1",
        "kwargs": {"output": 1},
    },
    {
        "method": "get_api_list",
        "description": "Get the device API help output",
        "command": "help",
        "kwargs": {},
    },
]


def build_device_info(device):
    """Return report header fields for this device."""
    return [
        ("Model", "MX0808-1022"),
        ("Firmware Version", device.get_version),
        ("IP Address", device.get_ipaddr),
        ("Standby State", device.get_standby),
        ("IR Mode", device.get_ir_mode),
    ]


def setup_device(_device):
    """Save state here if any read-style command requires a temporary change."""
    return {"note": "No settings altered; nothing to restore after GET-style validation."}


def teardown_device(_device, _saved_state):
    """Restore any saved device state here."""
    return None


def main():
    device = WRAPPER_CLASS(
        DEVICE_IP,
        port=PORT,
        timeout=TIMEOUT,
        debug=DEBUG,
    )
    return run_get_style_tests(
        device=device,
        model="MX0808-1022",
        get_commands=GET_COMMANDS,
        info_queries=build_device_info(device),
        markdown_output=MARKDOWN_OUTPUT,
        setup_hook=setup_device,
        teardown_hook=teardown_device,
    )


if __name__ == "__main__":
    raise SystemExit(0 if main()["failure"] == 0 else 1)
