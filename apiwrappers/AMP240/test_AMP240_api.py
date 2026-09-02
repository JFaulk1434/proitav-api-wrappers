#!/usr/bin/env python3
"""
AMP240 API GET-command test runner.

This script exercises all documented GET/read commands using representative
parameters and prints a report-friendly summary.
"""

import time
from AMP240 import AMP240Device


DEVICE_IP = "192.168.1.100"
PORT = 23
TIMEOUT = 3.0
USERNAME = None
PASSWORD = None
DEBUG = False


def test_all_get_commands() -> dict:
    model = "AMP240"
    section_sep = "~" * 80
    block_sep = "-" * 60

    device = AMP240Device(
        host=DEVICE_IP,
        port=PORT,
        timeout=TIMEOUT,
        username=USERNAME,
        password=PASSWORD,
        debug=DEBUG,
    )

    print(f"\n{model} Device Wrapper API Test\n")
    print(section_sep)
    print()
    print("DEVICE INFORMATION")
    print(section_sep)
    print()

    device.connect()
    info = device.get_device_info()
    print(f"Model: {info.get('model', 'Unknown')}")
    print(f"Firmware: {info.get('firmware', 'Unknown')}")
    print(f"Hardware: {info.get('hardware', 'Unknown')}")
    print(f"IP Address: {info.get('ip_address', 'Unknown')}")
    print(f"NetCfg Mode: {info.get('netcfg_mode', 'Unknown')}")
    print()

    get_commands = [
        ("get_dsp_mix", "Get DSP matrix crosspoint state", "GET DSP_MIX AMP LINE1", ("AMP", "LINE1")),
        ("get_dsp_expander", "Get DSP expander status", "GET DSP_EXP LINE1", ("LINE1",)),
        ("get_dsp_expander_property", "Get DSP expander property", "GET DSP_EXP_PROP Attack LINE1", ("Attack", "LINE1")),
        ("get_dsp_input_hpf", "Get DSP input HPF status", "GET DSP_IN_HPF LINE1", ("LINE1",)),
        ("get_dsp_input_hpf_property", "Get DSP input HPF property", "GET DSP_IN_HPF_PROP LINE1", ("LINE1",)),
        ("get_dsp_output_hpf", "Get DSP output HPF status", "GET DSP_OUT_HPF AMP", ("AMP",)),
        ("get_dsp_output_hpf_property", "Get DSP output HPF property", "GET DSP_OUT_HPF_PROP AMP", ("AMP",)),
        ("get_dsp_compressor", "Get DSP compressor status", "GET DSP_COMP LINE1", ("LINE1",)),
        ("get_dsp_compressor_property", "Get DSP compressor property", "GET DSP_COMP_PROP Attack LINE1", ("Attack", "LINE1")),
        ("get_dsp_equalizer", "Get DSP EQ status", "GET DSP_EQ AMP", ("AMP",)),
        ("get_dsp_equalizer_property", "Get DSP EQ property", "GET DSP_EQ_PROP level AMP 1", ("level", "AMP", 1)),
        ("get_dsp_lpf", "Get DSP LPF status", "GET DSP_LPF AMP", ("AMP",)),
        ("get_dsp_lpf_property", "Get DSP LPF property", "GET DSP_LPF_PROP AMP", ("AMP",)),
        ("get_dsp_duck", "Get DSP duck status", "GET DSP_DUCK AMP", ("AMP",)),
        ("get_dsp_duck_property", "Get DSP duck property", "GET DSP_DUCK_PROP Attack AMP", ("Attack", "AMP")),
        ("get_dsp_duck_priority", "Get DSP duck master", "GET DSP_DUCK_PRI AMP", ("AMP",)),
        ("get_dsp_input_mute", "Get input mute status", "GET DSP_AUD_GAIN_MUTE LINE1", ("LINE1",)),
        ("get_dsp_input_gain", "Get input gain", "GET DSP_AUD_GAIN LINE1", ("LINE1",)),
        ("get_dsp_output_mute", "Get output mute status", "GET DSP_AUD_VOL_MUTE AMP", ("AMP",)),
        ("get_dsp_output_volume", "Get output volume", "GET DSP_AUD_VOL AMP", ("AMP",)),
        ("get_dsp_input_meter", "Read input meter", "GET DSP_IN_METER LINE1", ("LINE1",)),
        ("get_dsp_output_meter", "Read output meter", "GET DSP_OUT_METER AMP", ("AMP",)),
        ("get_dsp_link_lock", "Get DSP link lock status", "GET DSP_LINK_LOCK 1", ("1",)),
        ("get_dsp_delay_enabled", "Get DSP delay enable", "GET DSP_DELAY_EN AMP", ("AMP",)),
        ("get_dsp_delay", "Get DSP delay", "GET DSP_DELAY AMP", ("AMP",)),
        ("get_amp_mode", "Get amp mode", "GET AMP_MODE", ()),
        ("get_audio_input_type", "Get audio input type", "GET AUDIN_TYPE", ()),
        ("get_volume_step", "Get volume step", "GET VOL_LEVEL_STEP", ()),
        ("get_led_brightness", "Get LED brightness", "GET LED_BRIGHTNESS", ()),
        ("get_mic_phantom_power", "Get mic phantom power", "GET MIC_PHA_PWR 1", (1,)),
        ("get_ip_address", "Get IP address", "GET IPADDR", ()),
        ("get_netcfg_mode", "Get netcfg mode", "GET NETCFG MODE", ()),
        ("get_firmware_version", "Get firmware version", "GET VER", ()),
        ("get_hardware_version", "Get hardware version", "GET HW_VER", ()),
        ("get_help", "Get API list", "help", ()),
        ("get_https_status", "Get HTTPS service status", "GET HTTPS", ()),
        ("get_telnets_status", "Get TELNETS service status", "GET TELNETS", ()),
        ("get_ssh_status", "Get SSH service status", "GET SSH", ()),
    ]

    print(f"Testing {len(get_commands)} get methods...")
    results = []
    success_count = 0
    failure_count = 0

    try:
        # No settings are altered by these GET tests; no restore actions required.
        for method_name, description, command, args in get_commands:
            print(section_sep)
            print(f"{method_name}: {description}")
            print(f"Command: {command}")
            print(block_sep)

            method = getattr(device, method_name)
            start_time = time.time()
            try:
                result = method(*args)
                elapsed = round(time.time() - start_time, 3)
                ok = result is not None and str(result).strip() != ""
                status = "SUCCESS" if ok else "FAILED (empty response)"
                if ok:
                    success_count += 1
                else:
                    failure_count += 1
            except Exception as exc:
                elapsed = round(time.time() - start_time, 3)
                result = f"Exception: {exc}"
                status = "FAILED (exception)"
                failure_count += 1

            print(f"Status: {status}")
            print(f"Response: {result}")
            print(f"Response time: {elapsed}s")
            print(block_sep)

            results.append(
                {
                    "method": method_name,
                    "command": command,
                    "status": status,
                    "success": status == "SUCCESS",
                    "response_time": elapsed,
                    "response": result,
                }
            )
    finally:
        device.disconnect()

    total = len(get_commands)
    success_rate = round((success_count / total) * 100, 1) if total else 0.0
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
    summary = test_all_get_commands()
    print(f"\nCompleted. Success rate: {summary['success_rate']}%")
