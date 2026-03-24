# MX0404-N301 Device Wrapper API Test

## Device Information

- **Model**: MX0404-N301
- **Firmware Version**: VER ARM VER V3.0.2 MCU VER V2.3.3
- **Hardware Version**: HW_VER V0.1
- **IP Address**: IPADDR 10.0.50.19 MASK 255.255.255.0 GATEWAY 10.0.50.1
- **Network Mode**: NETCFG MODE DHCP
- **Standby Status**: WAKE!

- **Notes**: No settings altered; nothing to restore after GET-style validation.

## Testing 51 get methods

### get_version

- **Description**: Get firmware version
- **Command**: `GET VER`
- **Status**: SUCCESS
- **Response time**: 0.160s

```text
VER ARM VER V3.0.2 MCU VER V2.3.3
```

### get_hardware

- **Description**: Get hardware version
- **Command**: `GET HW_VER`
- **Status**: SUCCESS
- **Response time**: 0.165s

```text
HW_VER V0.1
```

### get_ipaddr

- **Description**: Get device IP address
- **Command**: `GET IPADDR`
- **Status**: SUCCESS
- **Response time**: 0.167s

```text
IPADDR 10.0.50.19 MASK 255.255.255.0 GATEWAY 10.0.50.1
```

### get_network_mode

- **Description**: Get network mode
- **Command**: `GET NETCFG MODE`
- **Status**: SUCCESS
- **Response time**: 0.163s

```text
NETCFG MODE DHCP
```

### get_standby

- **Description**: Get standby status
- **Command**: `GET STANDBY`
- **Status**: SUCCESS
- **Response time**: 0.165s

```text
WAKE!
```

### get_ir

- **Description**: Get IR system code
- **Command**: `GET IR_SC`
- **Status**: SUCCESS
- **Response time**: 0.161s

```text
IR_SC all
```

### get_mapping_output

- **Description**: Get mapped input for output 1
- **Command**: `GET MP out1`
- **Status**: SUCCESS
- **Response time**: 0.162s

```text
MP in1 out1
```

### get_mapping_all

- **Description**: Get all input-output mappings
- **Command**: `GET MP all`
- **Status**: SUCCESS
- **Response time**: 0.168s

```text
MP in1 out1 MP in2 out2 MP in3 out3 MP in1 out4
```

### get_audio_switch_mode

- **Description**: Get audio switching mode for output 1
- **Command**: `GET AUDIOSW_M out1`
- **Status**: SUCCESS
- **Response time**: 0.168s

```text
AUDIOSW_M out1 followvm
```

### get_audio_mute

- **Description**: Get audio mute status for zone1
- **Command**: `GET AUDIO_MUTE zone1`
- **Status**: SUCCESS
- **Response time**: 0.162s

```text
AUDIO_MUTE zone1 off
```

### get_avmute

- **Description**: Get AV mute status for output 1
- **Command**: `GET AVMUTE out1`
- **Status**: SUCCESS
- **Response time**: 0.167s

```text
AVMUTE out1 off
```

### get_cec_auto

- **Description**: Get CEC auto power status for output 1
- **Command**: `GET AUTOCEC_FN out1`
- **Status**: SUCCESS
- **Response time**: 0.179s

```text
AUTOCEC_FN out1 off
```

### get_cec_delay

- **Description**: Get CEC auto power delay for output 1
- **Command**: `GET AUTOCEC_D out1`
- **Status**: SUCCESS
- **Response time**: 0.162s

```text
AUTOCEC_D out1 2
```

### get_hdcp

- **Description**: Get input HDCP support for input 1
- **Command**: `GET HDCP_S in1`
- **Status**: SUCCESS
- **Response time**: 0.208s

```text
HDCP_S in1 on
```

### get_output_hdcp_mode

- **Description**: Get output HDCP mode for output 1
- **Command**: `GET HDCP out1`
- **Status**: SUCCESS
- **Response time**: 0.163s

```text
HDCP out1 follow
```

### get_edid_all

- **Description**: Get EDID selection for all inputs
- **Command**: `GET EDID all`
- **Status**: SUCCESS
- **Response time**: 0.181s

```text
EDID in1 12 EDID in2 12 EDID in3 12 EDID in4 12
```

### get_edid

- **Description**: Get EDID selection for input 1
- **Command**: `GET EDID in1`
- **Status**: SUCCESS
- **Response time**: 0.163s

```text
EDID in1 12
```

### get_edid_output

- **Description**: Read EDID from output 1
- **Command**: `GET EDID_R out1`
- **Status**: SUCCESS
- **Response time**: 0.166s

```text
EDID_R out1 block0 00ffffffffffff004c2d140f000e0001011c0103805932780a23ada4544d99260f474abdef80714f81c0810081809500a9c0b300010108e80030f2705a80b0588a00501d7400001e023a801871382d40582c4500501d7400001e000000fd00184b0f873c000a20202020202000...
```

### get_input_connection

- **Description**: Get connection status for input 1
- **Command**: `GET VIDIN_CONNECT in1`
- **Status**: SUCCESS
- **Response time**: 0.175s

```text
VIDIN_CONNECT in1 Connected
```

### get_input_signal

- **Description**: Get signal status for input 1
- **Command**: `GET VIDIN_SIG in1`
- **Status**: SUCCESS
- **Response time**: 0.165s

```text
VIDIN_SIG in1 Valid
```

### get_input_video

- **Description**: Get video format for input 1
- **Command**: `GET VIDIN_FORMAT in1`
- **Status**: SUCCESS
- **Response time**: 0.171s

```text
VIDIN_FORMAT in1 3840x2160,59;None HDR;Ycbcr420;8bit
```

### get_hdcp_version

- **Description**: Get HDCP version for input 1
- **Command**: `GET VIDIN_HDCP in1`
- **Status**: SUCCESS
- **Response time**: 0.165s

```text
VIDIN_HDCP in1 HDCP2.2
```

### get_output_connection

- **Description**: Get connection status for output 1
- **Command**: `GET VIDOUT_CONNECT out1`
- **Status**: SUCCESS
- **Response time**: 0.166s

```text
VIDOUT_CONNECT out1 Connected
```

### get_output_signal

- **Description**: Get signal status for output 1
- **Command**: `GET VIDOUT_SIG out1`
- **Status**: SUCCESS
- **Response time**: 0.172s

```text
VIDOUT_SIG out1 Valid
```

### get_output_video

- **Description**: Get video format for output 1
- **Command**: `GET VIDOUT_FORMAT out1`
- **Status**: SUCCESS
- **Response time**: 0.165s

```text
VIDOUT_FORMAT out1 3840x2160,60;None HDR;RGB;8bit
```

### get_audio_output_format

- **Description**: Get audio format for output 1
- **Command**: `GET AUDOUT_FORMAT out1`
- **Status**: SUCCESS
- **Response time**: 0.165s

```text
AUDOUT_FORMAT out1 none;48khz
```

### get_output_hdcp

- **Description**: Get HDCP version for output 1
- **Command**: `GET VIDOUT_HDCP out1`
- **Status**: SUCCESS
- **Response time**: 0.165s

```text
VIDOUT_HDCP out1 HDCP2.2
```

### get_vidout_scaling

- **Description**: Get scaling mode for output 1
- **Command**: `GET VIDOUT_SCALE out1`
- **Status**: SUCCESS
- **Response time**: 0.167s

```text
VIDOUT_SCALE out1 auto
```

### get_output_resolution

- **Description**: Get output resolution for output 1
- **Command**: `GET VIDOUT_RES out1`
- **Status**: SUCCESS
- **Response time**: 0.174s

```text
VIDOUT_RES out1 1920x1080@60
```

### get_forced_sdr

- **Description**: Get forced SDR status for output 1
- **Command**: `GET FORCED_SDR out1`
- **Status**: SUCCESS
- **Response time**: 0.161s

```text
FORCED_SDR out1 on
```

### get_vidout_active

- **Description**: Get multiview activity state
- **Command**: `GET VIDOUT_ACTIVE mv1`
- **Status**: SUCCESS
- **Response time**: 0.165s

```text
VIDOUT_ACTIVE mv1 OFF
```

### get_vidout_mode

- **Description**: Get multiview scene selection
- **Command**: `GET VIDOUT_MODE mv1`
- **Status**: SUCCESS
- **Response time**: 0.166s

```text
VIDOUT_MODE mv1 DUAL_VIEW
```

### get_mv_window_source

- **Description**: Get multiview source mapping
- **Command**: `GET MV_WIN_SRC mv1 DUAL_VIEW`
- **Status**: SUCCESS
- **Response time**: 0.162s

```text
MV_WIN_SRC mv1 DUAL_VIEW win1 in1 win2 in2
```

### get_mv_audio_switch

- **Description**: Get multiview audio routing
- **Command**: `GET MV_AUDIO_SW mv1 DUAL_VIEW`
- **Status**: SUCCESS
- **Response time**: 0.158s

```text
MV_AUDIO_SW mv1 DUAL_VIEW WINDOW win1
```

### get_mv_window_border

- **Description**: Get multiview border state
- **Command**: `GET MV_WIN_BORDER_FN mv1 DUAL_VIEW`
- **Status**: SUCCESS
- **Response time**: 0.165s

```text
MV_WIN_BORDER_FN mv1 DUAL_VIEW win1 OFF win2 OFF
```

### get_mv_window_border_attr

- **Description**: Get multiview border attributes
- **Command**: `GET MV_WIN_BORDER_ATTR mv1 DUAL_VIEW win1`
- **Status**: SKIPPED (no response)
- **Response time**: 0.159s

```text
(no data)
```

### get_vw_window_source

- **Description**: Get videowall source mapping
- **Command**: `GET VW_WIN_SRC vw1 layout1`
- **Status**: SKIPPED (no response)
- **Response time**: 0.158s

```text
(no data)
```

### get_api_list

- **Description**: Get the device API help output
- **Command**: `help`
- **Status**: SUCCESS
- **Response time**: 2.010s

```text
Welcome to the matrix control system [00] SET SW in out[CR/LF] Switch input for output [01] SET SW in all[CR/LF] Switch indicated input for all outputs [02] GET MP out[CR/LF] Get which input mapping to the indicate output [03] GET MP all...
```

### get_mv_layout

- **Description**: Get legacy multiview layout
- **Command**: `GET VIDOUT_MODE`
- **Status**: SUCCESS
- **Response time**: 0.165s

```text
VIDOUT_MODE 1
```

### get_mv_dual_src

- **Description**: Get legacy dual-view input sources
- **Command**: `GET VIDOUT_DUAL_SRC`
- **Status**: SUCCESS
- **Response time**: 0.163s

```text
VIDOUT_DUAL_SRC in1 in2
```

### get_mv_pip_src

- **Description**: Get legacy PIP input sources
- **Command**: `GET VIDOUT_PIP_SRC`
- **Status**: SUCCESS
- **Response time**: 0.160s

```text
VIDOUT_PIP_SRC in1 in2
```

### get_mv_quad_src

- **Description**: Get legacy quad input sources
- **Command**: `GET VIDOUT_QUAD_SRC`
- **Status**: SUCCESS
- **Response time**: 0.160s

```text
VIDOUT_QUAD_SRC in1 in2 in3 in4
```

### get_mv_master_src

- **Description**: Get legacy master-view input sources
- **Command**: `GET VIDOUT_MASTER_SRC`
- **Status**: SUCCESS
- **Response time**: 0.161s

```text
VIDOUT_MASTER_SRC in1 in2 in3 in4
```

### get_mv_pip_smallsize

- **Description**: Get legacy PIP window size
- **Command**: `GET VIDOUT_PIP_SIZE`
- **Status**: SUCCESS
- **Response time**: 0.163s

```text
VIDOUT_PIP_SIZE 2
```

### get_mv_pip_smalllocation

- **Description**: Get legacy PIP window position
- **Command**: `GET VIDOUT_PIP_POS`
- **Status**: SUCCESS
- **Response time**: 0.163s

```text
VIDOUT_PIP_POS 3
```

### get_vidin_stretch

- **Description**: Get legacy input stretch mode
- **Command**: `GET VIDIN_STRETCH in1`
- **Status**: SUCCESS
- **Response time**: 0.164s

```text
VIDIN_STRETCH in1 origin
```

### get_audout_window

- **Description**: Get legacy audio follow window
- **Command**: `GET AUDOUT_WND`
- **Status**: SUCCESS
- **Response time**: 0.163s

```text
AUDOUT_WND in1
```

### get_videowall

- **Description**: Get legacy videowall configuration
- **Command**: `GET VIDWALL`
- **Status**: SUCCESS
- **Response time**: 0.158s

```text
VIDWALL in1 out1 out2 out3 out4
```

### get_vidmode

- **Description**: Get legacy global video mode
- **Command**: `GET VIDMODE`
- **Status**: SUCCESS
- **Response time**: 0.159s

```text
VIDMODE Matrix
```

### get_vidwall_bezel

- **Description**: Get legacy videowall bezel settings
- **Command**: `GET VIDWALLBEZEL`
- **Status**: SUCCESS
- **Response time**: 0.163s

```text
VIDWALLBEZEL 0 0 0 0
```

### get_vidwall_rotation

- **Description**: Get legacy output rotation state
- **Command**: `GET VIDWALL_ROTATION out1`
- **Status**: SUCCESS
- **Response time**: 0.165s

```text
VIDWALL_ROTATION out1 disable
```

## Summary

- **Total methods tested**: 51
- **Successful**: 49
- **Failed**: 0
- **Skipped**: 2
- **Success rate**: 96.1%

## Detailed Results

| Command                                     | Status                |   Time | Result                                                                                                                                                                                                                                           |
| ------------------------------------------- | --------------------- | -----: | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `GET VER`                                   | SUCCESS               | 0.160s | VER ARM VER V3.0.2 MCU VER V2.3.3                                                                                                                                                                                                                |
| `GET HW_VER`                                | SUCCESS               | 0.165s | HW_VER V0.1                                                                                                                                                                                                                                      |
| `GET IPADDR`                                | SUCCESS               | 0.167s | IPADDR 10.0.50.19 MASK 255.255.255.0 GATEWAY 10.0.50.1                                                                                                                                                                                           |
| `GET NETCFG MODE`                           | SUCCESS               | 0.163s | NETCFG MODE DHCP                                                                                                                                                                                                                                 |
| `GET STANDBY`                               | SUCCESS               | 0.165s | WAKE!                                                                                                                                                                                                                                            |
| `GET IR_SC`                                 | SUCCESS               | 0.161s | IR_SC all                                                                                                                                                                                                                                        |
| `GET MP out1`                               | SUCCESS               | 0.162s | MP in1 out1                                                                                                                                                                                                                                      |
| `GET MP all`                                | SUCCESS               | 0.168s | MP in1 out1 MP in2 out2 MP in3 out3 MP in1 out4                                                                                                                                                                                                  |
| `GET AUDIOSW_M out1`                        | SUCCESS               | 0.168s | AUDIOSW_M out1 followvm                                                                                                                                                                                                                          |
| `GET AUDIO_MUTE zone1`                      | SUCCESS               | 0.162s | AUDIO_MUTE zone1 off                                                                                                                                                                                                                             |
| `GET AVMUTE out1`                           | SUCCESS               | 0.167s | AVMUTE out1 off                                                                                                                                                                                                                                  |
| `GET AUTOCEC_FN out1`                       | SUCCESS               | 0.179s | AUTOCEC_FN out1 off                                                                                                                                                                                                                              |
| `GET AUTOCEC_D out1`                        | SUCCESS               | 0.162s | AUTOCEC_D out1 2                                                                                                                                                                                                                                 |
| `GET HDCP_S in1`                            | SUCCESS               | 0.208s | HDCP_S in1 on                                                                                                                                                                                                                                    |
| `GET HDCP out1`                             | SUCCESS               | 0.163s | HDCP out1 follow                                                                                                                                                                                                                                 |
| `GET EDID all`                              | SUCCESS               | 0.181s | EDID in1 12 EDID in2 12 EDID in3 12 EDID in4 12                                                                                                                                                                                                  |
| `GET EDID in1`                              | SUCCESS               | 0.163s | EDID in1 12                                                                                                                                                                                                                                      |
| `GET EDID_R out1`                           | SUCCESS               | 0.166s | EDID_R out1 block0 00ffffffffffff004c2d140f000e0001011c0103805932780a23ada4544d99260f474abdef80714f81c0810081809500a9c0b300010108e80030f2705a80b0588a00501d7400001e023a801871382d40582c4500501d7400001e000000fd00184b0f873c000a20202020202000... |
| `GET VIDIN_CONNECT in1`                     | SUCCESS               | 0.175s | VIDIN_CONNECT in1 Connected                                                                                                                                                                                                                      |
| `GET VIDIN_SIG in1`                         | SUCCESS               | 0.165s | VIDIN_SIG in1 Valid                                                                                                                                                                                                                              |
| `GET VIDIN_FORMAT in1`                      | SUCCESS               | 0.171s | VIDIN_FORMAT in1 3840x2160,59;None HDR;Ycbcr420;8bit                                                                                                                                                                                             |
| `GET VIDIN_HDCP in1`                        | SUCCESS               | 0.165s | VIDIN_HDCP in1 HDCP2.2                                                                                                                                                                                                                           |
| `GET VIDOUT_CONNECT out1`                   | SUCCESS               | 0.166s | VIDOUT_CONNECT out1 Connected                                                                                                                                                                                                                    |
| `GET VIDOUT_SIG out1`                       | SUCCESS               | 0.172s | VIDOUT_SIG out1 Valid                                                                                                                                                                                                                            |
| `GET VIDOUT_FORMAT out1`                    | SUCCESS               | 0.165s | VIDOUT_FORMAT out1 3840x2160,60;None HDR;RGB;8bit                                                                                                                                                                                                |
| `GET AUDOUT_FORMAT out1`                    | SUCCESS               | 0.165s | AUDOUT_FORMAT out1 none;48khz                                                                                                                                                                                                                    |
| `GET VIDOUT_HDCP out1`                      | SUCCESS               | 0.165s | VIDOUT_HDCP out1 HDCP2.2                                                                                                                                                                                                                         |
| `GET VIDOUT_SCALE out1`                     | SUCCESS               | 0.167s | VIDOUT_SCALE out1 auto                                                                                                                                                                                                                           |
| `GET VIDOUT_RES out1`                       | SUCCESS               | 0.174s | VIDOUT_RES out1 1920x1080@60                                                                                                                                                                                                                     |
| `GET FORCED_SDR out1`                       | SUCCESS               | 0.161s | FORCED_SDR out1 on                                                                                                                                                                                                                               |
| `GET VIDOUT_ACTIVE mv1`                     | SUCCESS               | 0.165s | VIDOUT_ACTIVE mv1 OFF                                                                                                                                                                                                                            |
| `GET VIDOUT_MODE mv1`                       | SUCCESS               | 0.166s | VIDOUT_MODE mv1 DUAL_VIEW                                                                                                                                                                                                                        |
| `GET MV_WIN_SRC mv1 DUAL_VIEW`              | SUCCESS               | 0.162s | MV_WIN_SRC mv1 DUAL_VIEW win1 in1 win2 in2                                                                                                                                                                                                       |
| `GET MV_AUDIO_SW mv1 DUAL_VIEW`             | SUCCESS               | 0.158s | MV_AUDIO_SW mv1 DUAL_VIEW WINDOW win1                                                                                                                                                                                                            |
| `GET MV_WIN_BORDER_FN mv1 DUAL_VIEW`        | SUCCESS               | 0.165s | MV_WIN_BORDER_FN mv1 DUAL_VIEW win1 OFF win2 OFF                                                                                                                                                                                                 |
| `GET MV_WIN_BORDER_ATTR mv1 DUAL_VIEW win1` | SKIPPED (no response) | 0.159s | (no data)                                                                                                                                                                                                                                        |
| `GET VW_WIN_SRC vw1 layout1`                | SKIPPED (no response) | 0.158s | (no data)                                                                                                                                                                                                                                        |
| `help`                                      | SUCCESS               | 2.010s | Welcome to the matrix control system [00] SET SW in out[CR/LF] Switch input for output [01] SET SW in all[CR/LF] Switch indicated input for all outputs [02] GET MP out[CR/LF] Get which input mapping to the indicate output [03] GET MP all... |
| `GET VIDOUT_MODE`                           | SUCCESS               | 0.165s | VIDOUT_MODE 1                                                                                                                                                                                                                                    |
| `GET VIDOUT_DUAL_SRC`                       | SUCCESS               | 0.163s | VIDOUT_DUAL_SRC in1 in2                                                                                                                                                                                                                          |
| `GET VIDOUT_PIP_SRC`                        | SUCCESS               | 0.160s | VIDOUT_PIP_SRC in1 in2                                                                                                                                                                                                                           |
| `GET VIDOUT_QUAD_SRC`                       | SUCCESS               | 0.160s | VIDOUT_QUAD_SRC in1 in2 in3 in4                                                                                                                                                                                                                  |
| `GET VIDOUT_MASTER_SRC`                     | SUCCESS               | 0.161s | VIDOUT_MASTER_SRC in1 in2 in3 in4                                                                                                                                                                                                                |
| `GET VIDOUT_PIP_SIZE`                       | SUCCESS               | 0.163s | VIDOUT_PIP_SIZE 2                                                                                                                                                                                                                                |
| `GET VIDOUT_PIP_POS`                        | SUCCESS               | 0.163s | VIDOUT_PIP_POS 3                                                                                                                                                                                                                                 |
| `GET VIDIN_STRETCH in1`                     | SUCCESS               | 0.164s | VIDIN_STRETCH in1 origin                                                                                                                                                                                                                         |
| `GET AUDOUT_WND`                            | SUCCESS               | 0.163s | AUDOUT_WND in1                                                                                                                                                                                                                                   |
| `GET VIDWALL`                               | SUCCESS               | 0.158s | VIDWALL in1 out1 out2 out3 out4                                                                                                                                                                                                                  |
| `GET VIDMODE`                               | SUCCESS               | 0.159s | VIDMODE Matrix                                                                                                                                                                                                                                   |
| `GET VIDWALLBEZEL`                          | SUCCESS               | 0.163s | VIDWALLBEZEL 0 0 0 0                                                                                                                                                                                                                             |
| `GET VIDWALL_ROTATION out1`                 | SUCCESS               | 0.165s | VIDWALL_ROTATION out1 disable                                                                                                                                                                                                                    |