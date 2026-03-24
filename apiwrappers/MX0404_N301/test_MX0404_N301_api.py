"""Standalone GET-style API test for MX0404-N301.

Run this file directly from Cursor/VSCode. The device settings are intentionally
kept at the top of the file so they are visible immediately.
"""

from pathlib import Path
import sys


DEVICE_IP = "10.0.50.19"
PORT = 23
TIMEOUT = 2.0
DEBUG = False
MARKDOWN_OUTPUT = True
MARKDOWN_TABLE_COMMAND_LIMIT = 32
MARKDOWN_TABLE_RESULT_LIMIT = 56


CURRENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = CURRENT_DIR.parent.parent

if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from MX0404_N301 import MX0404N301_Device
from test_report_utils import run_get_style_tests


GET_COMMANDS = [
    {
        "method": "get_version",
        "description": "Get firmware version",
        "command": "GET VER",
        "kwargs": {},
    },
    {
        "method": "get_hardware",
        "description": "Get hardware version",
        "command": "GET HW_VER",
        "kwargs": {},
    },
    {
        "method": "get_ipaddr",
        "description": "Get device IP address",
        "command": "GET IPADDR",
        "kwargs": {},
    },
    {
        "method": "get_network_mode",
        "description": "Get network mode",
        "command": "GET NETCFG MODE",
        "kwargs": {},
    },
    {
        "method": "get_standby",
        "description": "Get standby status",
        "command": "GET STANDBY",
        "kwargs": {},
    },
    {
        "method": "get_ir",
        "description": "Get IR system code",
        "command": "GET IR_SC",
        "kwargs": {},
    },
    {
        "method": "get_mapping_output",
        "description": "Get mapped input for output 1",
        "command": "GET MP out1",
        "kwargs": {"output": "out1"},
    },
    {
        "method": "get_mapping_all",
        "description": "Get all input-output mappings",
        "command": "GET MP all",
        "kwargs": {},
    },
    {
        "method": "get_audio_switch_mode",
        "description": "Get audio switching mode for output 1",
        "command": "GET AUDIOSW_M out1",
        "kwargs": {"output": "out1"},
    },
    {
        "method": "get_audio_mute",
        "description": "Get audio mute status for zone1",
        "command": "GET AUDIO_MUTE zone1",
        "kwargs": {"output": "zone1"},
    },
    {
        "method": "get_avmute",
        "description": "Get AV mute status for output 1",
        "command": "GET AVMUTE out1",
        "kwargs": {"output": "out1"},
    },
    {
        "method": "get_cec_auto",
        "description": "Get CEC auto power status for output 1",
        "command": "GET AUTOCEC_FN out1",
        "kwargs": {"output": "out1"},
    },
    {
        "method": "get_cec_delay",
        "description": "Get CEC auto power delay for output 1",
        "command": "GET AUTOCEC_D out1",
        "kwargs": {"output": "out1"},
    },
    {
        "method": "get_hdcp",
        "description": "Get input HDCP support for input 1",
        "command": "GET HDCP_S in1",
        "kwargs": {"input": "in1"},
    },
    {
        "method": "get_output_hdcp_mode",
        "description": "Get output HDCP mode for output 1",
        "command": "GET HDCP out1",
        "kwargs": {"output": "out1"},
    },
    {
        "method": "get_edid_all",
        "description": "Get EDID selection for all inputs",
        "command": "GET EDID all",
        "kwargs": {},
    },
    {
        "method": "get_edid",
        "description": "Get EDID selection for input 1",
        "command": "GET EDID in1",
        "kwargs": {"input": "in1"},
    },
    {
        "method": "get_edid_output",
        "description": "Read EDID from output 1",
        "command": "GET EDID_R out1",
        "kwargs": {"output": "out1"},
    },
    {
        "method": "get_input_connection",
        "description": "Get connection status for input 1",
        "command": "GET VIDIN_CONNECT in1",
        "kwargs": {"input": "in1"},
    },
    {
        "method": "get_input_signal",
        "description": "Get signal status for input 1",
        "command": "GET VIDIN_SIG in1",
        "kwargs": {"input": "in1"},
    },
    {
        "method": "get_input_video",
        "description": "Get video format for input 1",
        "command": "GET VIDIN_FORMAT in1",
        "kwargs": {"input": "in1"},
    },
    {
        "method": "get_hdcp_version",
        "description": "Get HDCP version for input 1",
        "command": "GET VIDIN_HDCP in1",
        "kwargs": {"input": "in1"},
    },
    {
        "method": "get_output_connection",
        "description": "Get connection status for output 1",
        "command": "GET VIDOUT_CONNECT out1",
        "kwargs": {"output": "out1"},
    },
    {
        "method": "get_output_signal",
        "description": "Get signal status for output 1",
        "command": "GET VIDOUT_SIG out1",
        "kwargs": {"output": "out1"},
    },
    {
        "method": "get_output_video",
        "description": "Get video format for output 1",
        "command": "GET VIDOUT_FORMAT out1",
        "kwargs": {"output": "out1"},
    },
    {
        "method": "get_audio_output_format",
        "description": "Get audio format for output 1",
        "command": "GET AUDOUT_FORMAT out1",
        "kwargs": {"output": "out1"},
    },
    {
        "method": "get_output_hdcp",
        "description": "Get HDCP version for output 1",
        "command": "GET VIDOUT_HDCP out1",
        "kwargs": {"output": "out1"},
    },
    {
        "method": "get_vidout_scaling",
        "description": "Get scaling mode for output 1",
        "command": "GET VIDOUT_SCALE out1",
        "kwargs": {"out": "out1"},
    },
    {
        "method": "get_output_resolution",
        "description": "Get output resolution for output 1",
        "command": "GET VIDOUT_RES out1",
        "kwargs": {"out": "out1"},
    },
    {
        "method": "get_forced_sdr",
        "description": "Get forced SDR status for output 1",
        "command": "GET FORCED_SDR out1",
        "kwargs": {"output": "out1"},
    },
    {
        "method": "get_vidout_active",
        "description": "Get multiview activity state",
        "command": "GET VIDOUT_ACTIVE mv1",
        "kwargs": {"output_id": "mv1"},
    },
    {
        "method": "get_vidout_mode",
        "description": "Get multiview scene selection",
        "command": "GET VIDOUT_MODE mv1",
        "kwargs": {"output_id": "mv1"},
    },
    {
        "method": "get_mv_window_source",
        "description": "Get multiview source mapping",
        "command": "GET MV_WIN_SRC mv1 DUAL_VIEW",
        "kwargs": {"output_id": "mv1", "scene": "DUAL_VIEW"},
    },
    {
        "method": "get_mv_audio_switch",
        "description": "Get multiview audio routing",
        "command": "GET MV_AUDIO_SW mv1 DUAL_VIEW",
        "kwargs": {"output_id": "mv1", "scene": "DUAL_VIEW"},
    },
    {
        "method": "get_mv_window_border",
        "description": "Get multiview border state",
        "command": "GET MV_WIN_BORDER_FN mv1 DUAL_VIEW",
        "kwargs": {"output_id": "mv1", "scene": "DUAL_VIEW"},
    },
    {
        "method": "get_mv_window_border_attr",
        "description": "Get multiview border attributes",
        "command": "GET MV_WIN_BORDER_ATTR mv1 DUAL_VIEW win1",
        "kwargs": {"output_id": "mv1", "scene": "DUAL_VIEW", "window_ref": "win1"},
    },
    {
        "method": "get_vw_window_source",
        "description": "Get videowall source mapping",
        "command": "GET VW_WIN_SRC vw1 layout1",
        "kwargs": {"output_id": "vw1", "scene": "layout1"},
    },
    {
        "method": "get_api_list",
        "description": "Get the device API help output",
        "command": "help",
        "kwargs": {},
    },
    {
        "method": "get_mv_layout",
        "description": "Get legacy multiview layout",
        "command": "GET VIDOUT_MODE",
        "kwargs": {},
    },
    {
        "method": "get_mv_dual_src",
        "description": "Get legacy dual-view input sources",
        "command": "GET VIDOUT_DUAL_SRC",
        "kwargs": {},
    },
    {
        "method": "get_mv_pip_src",
        "description": "Get legacy PIP input sources",
        "command": "GET VIDOUT_PIP_SRC",
        "kwargs": {},
    },
    {
        "method": "get_mv_quad_src",
        "description": "Get legacy quad input sources",
        "command": "GET VIDOUT_QUAD_SRC",
        "kwargs": {},
    },
    {
        "method": "get_mv_master_src",
        "description": "Get legacy master-view input sources",
        "command": "GET VIDOUT_MASTER_SRC",
        "kwargs": {},
    },
    {
        "method": "get_mv_pip_smallsize",
        "description": "Get legacy PIP window size",
        "command": "GET VIDOUT_PIP_SIZE",
        "kwargs": {},
    },
    {
        "method": "get_mv_pip_smalllocation",
        "description": "Get legacy PIP window position",
        "command": "GET VIDOUT_PIP_POS",
        "kwargs": {},
    },
    {
        "method": "get_vidin_stretch",
        "description": "Get legacy input stretch mode",
        "command": "GET VIDIN_STRETCH in1",
        "kwargs": {"input": "in1"},
    },
    {
        "method": "get_audout_window",
        "description": "Get legacy audio follow window",
        "command": "GET AUDOUT_WND",
        "kwargs": {},
    },
    {
        "method": "get_videowall",
        "description": "Get legacy videowall configuration",
        "command": "GET VIDWALL",
        "kwargs": {},
    },
    {
        "method": "get_vidmode",
        "description": "Get legacy global video mode",
        "command": "GET VIDMODE",
        "kwargs": {},
    },
    {
        "method": "get_vidwall_bezel",
        "description": "Get legacy videowall bezel settings",
        "command": "GET VIDWALLBEZEL",
        "kwargs": {},
    },
    {
        "method": "get_vidwall_rotation",
        "description": "Get legacy output rotation state",
        "command": "GET VIDWALL_ROTATION out1",
        "kwargs": {"prm1": "out1"},
    },
]


def build_device_info(device):
    return [
        ("Model", "MX0404-N301"),
        ("Firmware Version", device.get_version),
        ("Hardware Version", device.get_hardware),
        ("IP Address", device.get_ipaddr),
        ("Network Mode", device.get_network_mode),
        ("Standby Status", device.get_standby),
    ]


def setup_device(_device):
    return {
        "note": "No settings altered; nothing to restore after GET-style validation."
    }


def teardown_device(_device, _saved_state):
    return None


def main():
    device = MX0404N301_Device(
        DEVICE_IP,
        port=PORT,
        timeout=TIMEOUT,
        debug=DEBUG,
    )
    return run_get_style_tests(
        device=device,
        model="MX0404-N301",
        get_commands=GET_COMMANDS,
        info_queries=build_device_info(device),
        markdown_output=MARKDOWN_OUTPUT,
        markdown_table_command_limit=MARKDOWN_TABLE_COMMAND_LIMIT,
        markdown_table_result_limit=MARKDOWN_TABLE_RESULT_LIMIT,
        setup_hook=setup_device,
        teardown_hook=teardown_device,
    )


if __name__ == "__main__":
    raise SystemExit(0 if main()["failure"] == 0 else 1)
