#!/usr/bin/env python3
"""
MS0402_N011 API Test Script

This script tests all get commands available in the MS0402_N011 device wrapper.
It provides comprehensive testing similar to the CAM600 test format with detailed
reporting of success/failure rates and execution times.

Usage:
    python test_MS0402_N011_api.py [device_ip] [username] [password]

Example:
    python test_MS0402_N011_api.py 10.0.50.9 admin admin
"""

import sys
import time
from MS0402_N011 import MS0402N011_Device


def test_all_get_commands(
    device_ip="10.0.50.15", username="admin", password="admin", debug=False
):
    """
    Test all get commands in the MS0402_N011 device wrapper.

    Args:
        device_ip (str): IP address of the MS0402_N011 device
        username (str): Telnet username
        password (str): Telnet password
        debug (bool): Enable debug output

    Returns:
        dict: Summary of test results with success/failure counts
    """
    print("=" * 80)
    print("MS0402_N011 API TEST")
    print("=" * 80)

    # Initialize device
    device = MS0402N011_Device(
        ip=device_ip, user=username, password=password, debug=debug, verbose=False
    )

    # Test connection
    print(f"\nConnecting to device at {device_ip}...")
    connection_result = device.connect()
    if connection_result != "Connected successfully.":
        print(f"ERROR: Failed to establish connection - {connection_result}")
        return {"success": 0, "failure": 0, "total": 0, "error": connection_result}

    print("Connection established successfully!")

    # Get device information for header
    print("\n" + "=" * 80)
    print("DEVICE INFORMATION")
    print("=" * 80)

    try:
        # Get firmware versions
        print("Firmware Versions:")
        firmware_versions = [
            device.get_firmware_version("main"),
            device.get_firmware_version("arm"),
            device.get_firmware_version("usb_c_video"),
            device.get_firmware_version("hdmi"),
            device.get_firmware_version("usb_c_cc"),
            device.get_firmware_version("hdbt_3.0"),
            device.get_firmware_version("cpld"),
        ]

        for version in firmware_versions:
            print(f"  {version}")

        # Get network information
        print("\nNetwork Settings:")
        print(f"  IP Address Info: {device.get_ip_address()}")
        print(f"  NIC Status: {device.get_NIC_status()}")
        print(f"  VLAN Enable: {device.get_vlan_enable()}")

    except Exception as e:
        print(f"Error getting device info: {e}")

    print("=" * 80)

    # Define all get methods to test with their descriptions
    get_methods = [
        # Firmware and System Information
        ("get_firmware_version", "Get firmware version", "get ver {prm}"),
        ("get_api_commands", "Get available API commands", "help"),
        # Network Settings
        ("get_ip_address", "Get IP address configuration", "GET IPADDR"),
        ("get_NIC_status", "Get Network Interface Card status", "GET NIC_STATUS"),
        ("get_vlan_enable", "Get VLAN enable status", "GET VLAN_ENABLE"),
        # Video Input/Output Settings
        ("get_vidin_status", "Get video input signal status", "GET VIDIN_SIG {input}"),
        ("get_vidin_HDCP", "Get video input HDCP status", "GET VIDIN_HDCP {input}"),
        ("get_vidout_HDCP", "Get video output HDCP status", "GET HDCP {output}"),
        ("get_scaler_output", "Get scaler output status", "GET SCALER {output}"),
        # Switch Settings
        ("get_input", "Get input to output mapping", "GET SW {output}"),
        # Autoswitch Settings
        ("get_autoswitch", "Get autoswitch function status", "GET AUTOSW_FN"),
        (
            "get_autoswitch_port",
            "Get autoswitch port status",
            "GET AUTOSW_PORT {output}",
        ),
        ("get_usba_autoswitch", "Get USBA autoswitch status", "GET USBASW_FN"),
        ("get_video_autoswitch", "Get video autoswitch mode", "GET AUTOSW_MD"),
        ("get_lifo", "Get LIFO setting", "GET LIFO_SO"),
        # CEC Settings
        ("get_cec_auto", "Get CEC auto power status", "GET AUTOCEC_FN {out}"),
        ("get_cec_power_delay", "Get CEC power delay", "GET AUTOCEC_D {out}"),
        (
            "get_cec_poweron_command",
            "Get CEC power on command",
            "GET CECCMD_EDIT {out} pwron",
        ),
        (
            "get_cec_poweroff_command",
            "Get CEC power off command",
            "GET CECCMD_EDIT {out} pwroff",
        ),
        # RS232 Settings
        ("get_rs232_baud", "Get RS232 baud rate", "GET UART_B UART1"),
        ("get_rs232_autopower", "Get RS232 auto power status", "GET UARTPWR_FN UART1"),
        (
            "get_rs232_autopower_delay",
            "Get RS232 auto power delay",
            "GET UARTPWR_D UART1",
        ),
        ("get_rs232_command", "Get RS232 commands", "GET UART_CMD UART1"),
        # USB Settings
        ("get_usb_work_mode", "Get USB work mode", "GET USB_M"),
        ("get_usb_switch", "Get USB switch status", "GET USBSW"),
        ("get_usb_NIC", "Get USB NIC status", "GET USBNIC {input}"),
        ("get_usb_port_priority", "Get USB port priority", "GET USB_P {input}"),
        # Audio Settings
        ("get_audio_mute", "Get audio mute status", "GET AUD_MUTE {output}"),
        ("get_audio_switch", "Get audio switch status", "GET AUDSW"),
        # EDID Settings
        ("get_edid_mode", "Get EDID mode", "GET EDID {input}"),
        ("get_edid_output", "Get EDID output", "GET EDID_R {output}"),
        # USB-C Settings
        ("get_usbc_sst_mode", "Get USB-C SST mode", "GET USBC3_SST"),
        ("get_usbc_dp_mode", "Get USB-C DP mode", "GET USBC4_DM"),
        ("get_usbc_strategy", "Get USB-C strategy", "GET USBC4_STRA"),
        # Debug Settings
        ("get_debug_mode", "Get debug mode status", "GET LOGDBG"),
    ]

    results = []
    success_count = 0
    failure_count = 0

    print(f"\nTesting {len(get_methods)} get methods...")
    print("-" * 80)

    for method_name, description, command_template in get_methods:
        print(f"\n{method_name}: {description}")
        print(f"Command Template: {command_template}")
        print("-" * 60)

        try:
            # Get the method object
            method = getattr(device, method_name)

            # Execute the method with appropriate parameters
            start_time = time.time()

            # Handle methods that require parameters
            if method_name == "get_firmware_version":
                # Test with different parameters
                result = {
                    "main": method("main"),
                    "arm": method("arm"),
                    "usb_c_video": method("usb_c_video"),
                    "hdmi": method("hdmi"),
                    "usb_c_cc": method("usb_c_cc"),
                    "hdbt_3.0": method("hdbt_3.0"),
                    "cpld": method("cpld"),
                }
            elif method_name == "get_input":
                # Test both outputs
                result = {"OUT1": method("OUT1"), "OUT2": method("OUT2")}
            elif method_name == "get_autoswitch_port":
                # Test both outputs
                result = {"OUT1": method("OUT1"), "OUT2": method("OUT2")}
            elif method_name == "get_cec_auto":
                # Test both outputs
                result = {"OUT1": method("OUT1"), "OUT2": method("OUT2")}
            elif method_name == "get_cec_power_delay":
                # Test both outputs
                result = {"OUT1": method("OUT1"), "OUT2": method("OUT2")}
            elif method_name == "get_cec_poweron_command":
                # Test both outputs
                result = {"OUT1": method("OUT1"), "OUT2": method("OUT2")}
            elif method_name == "get_cec_poweroff_command":
                # Test both outputs
                result = {"OUT1": method("OUT1"), "OUT2": method("OUT2")}
            elif method_name == "get_vidin_status":
                # Test with ALL parameter
                result = method("ALL")
            elif method_name == "get_vidin_HDCP":
                # Test with ALL parameter
                result = method("ALL")
            elif method_name == "get_vidout_HDCP":
                # Test with ALL parameter
                result = method("ALL")
            elif method_name == "get_scaler_output":
                # Test with ALL parameter
                result = method("ALL")
            elif method_name == "get_usb_NIC":
                # Test with ALL parameter
                result = method("ALL")
            elif method_name == "get_usb_port_priority":
                # Test with ALL parameter
                result = method("ALL")
            elif method_name == "get_audio_mute":
                # Test with ALL parameter
                result = method("ALL")
            elif method_name == "get_edid_mode":
                # Test with ALL parameter
                result = method("ALL")
            elif method_name == "get_edid_output":
                # Test both outputs
                result = {"OUT1": method("OUT1"), "OUT2": method("OUT2")}
            else:
                # Methods that don't require parameters
                result = method()

            execution_time = round(time.time() - start_time, 3)

            # Determine success based on result
            if result is not None:
                # Check for error responses
                if isinstance(result, str):
                    if "error" in result.lower() or "failed" in result.lower():
                        success = False
                        failure_count += 1
                        status = "FAILED (error response)"
                    else:
                        success = True
                        success_count += 1
                        status = "SUCCESS"
                elif isinstance(result, dict):
                    # Check if any values in the dict indicate errors
                    has_error = any(
                        isinstance(v, str)
                        and ("error" in v.lower() or "failed" in v.lower())
                        for v in result.values()
                    )
                    if has_error:
                        success = False
                        failure_count += 1
                        status = "FAILED (error in response)"
                    else:
                        success = True
                        success_count += 1
                        status = "SUCCESS"
                else:
                    success = True
                    success_count += 1
                    status = "SUCCESS"
            else:
                success = False
                failure_count += 1
                status = "FAILED (no response)"

            # Print results
            print(f"{'=' * 80}")
            print(f"Command: {command_template}")
            print(f"Status: {status}")
            print(f"Response: {result}")
            print(f"Execution Time: {execution_time}s")
            print(f"{'=' * 80}")

            # Store result for summary
            results.append(
                {
                    "method": method_name,
                    "description": description,
                    "command_template": command_template,
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
                    "description": description,
                    "command_template": command_template,
                    "success": False,
                    "execution_time": 0,
                    "result": None,
                    "status": status,
                }
            )

    # Close connection
    device.close()

    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total Methods Tested: {len(get_methods)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {failure_count}")
    print(f"Success Rate: {(success_count / len(get_methods) * 100):.1f}%")

    # Print detailed results table
    print("\n" + "-" * 80)
    print("DETAILED RESULTS")
    print("-" * 80)
    print(f"{'Command':<40} {'Status':<15} {'Time':<8} {'Result'}")
    print("-" * 80)

    for result in results:
        status_short = "✓ PASS" if result["success"] else "✗ FAIL"
        time_str = (
            f"{result['execution_time']}s" if result["execution_time"] > 0 else "N/A"
        )

        # Clean up the result string for better formatting
        result_str = str(result["result"])

        # Remove all newlines, carriage returns, tabs, and other whitespace characters
        import re

        result_str = re.sub(
            r"\s+", " ", result_str
        )  # Replace any whitespace with single space

        # Strip leading/trailing whitespace
        result_str = result_str.strip()

        # Truncate to 40 characters and add ellipsis if needed (shorter to prevent wrapping)
        if len(result_str) > 40:
            result_str = result_str[:37] + "..."

        # Show the actual command being sent to the device
        command_display = result["command_template"]
        print(f"{command_display:<40} {status_short:<15} {time_str:<8} {result_str}")

    # Return summary for programmatic use
    summary = {
        "success": success_count,
        "failure": failure_count,
        "total": len(get_methods),
        "success_rate": round(success_count / len(get_methods) * 100, 1),
        "results": results,
    }

    return summary


def main():
    """Main function to run the API test."""
    # Parse command line arguments
    device_ip = "10.0.50.15"
    username = "admin"
    password = "admin"
    debug = False

    if len(sys.argv) > 1:
        device_ip = sys.argv[1]
    if len(sys.argv) > 2:
        username = sys.argv[2]
    if len(sys.argv) > 3:
        password = sys.argv[3]
    if len(sys.argv) > 4:
        debug = sys.argv[4].lower() in ["true", "1", "yes", "on"]

    print("Starting MS0402_N011 API test...")
    print(f"Device IP: {device_ip}")
    print(f"Username: {username}")
    print(f"Password: {'*' * len(password)}")
    print(f"Debug: {debug}")

    # Run the test
    test_results = test_all_get_commands(device_ip, username, password, debug)

    if "error" in test_results:
        print(f"\nTest failed to start: {test_results['error']}")
        sys.exit(1)

    print(f"\nTest completed. Success rate: {test_results['success_rate']}%")

    # Exit with appropriate code
    if test_results["success_rate"] >= 80:
        print("Test PASSED - High success rate achieved")
        sys.exit(0)
    else:
        print("Test FAILED - Low success rate")
        sys.exit(1)


if __name__ == "__main__":
    main()
