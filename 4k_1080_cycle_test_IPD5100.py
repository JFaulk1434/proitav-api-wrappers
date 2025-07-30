from apiwrappers.IP5100 import Decoder5100_Device
import time

device_ip = "10.0.30.19"
device_decoder = Decoder5100_Device(device_ip)
success = 0
failure = 0


def set_timing_1080p():
    global success
    global failure
    print(device_decoder.set_output_timing(8))
    time.sleep(3)
    output = device_decoder.get_video_output_info()
    if (
        output["hdmi out active"] == "true"
        and output["hdmi out resolution"] == "1920x1080"
    ):
        success += 1
    else:
        failure += 1


def set_timing_4k():
    global success
    global failure
    print(device_decoder.set_output_timing(3))
    time.sleep(3)
    output = device_decoder.get_video_output_info()
    if (
        output["hdmi out active"] == "true"
        and output["hdmi out resolution"] == "3840x2160"
    ):
        success += 1
    else:
        failure += 1


def run_timing_test(cycles=100):
    global success, failure
    print(f"\nStarting timing test for {cycles} cycles...")
    print("Each cycle will switch between 1080p and 4K resolution")

    for i in range(cycles):
        print(f"\nCycle {i + 1}/{cycles}")

        print("Setting to 1080p...")
        set_timing_1080p()
        # sleep(2)  # Additional cooldown between switches

        print("Setting to 4K...")
        set_timing_4k()
        # sleep(2)  # Additional cooldown between switches

        # Print running statistics
        total = success + failure
        success_rate = (success / total) * 100 if total > 0 else 0
        print(
            f"Current Stats - Success: {success}, Failures: {failure}, Success Rate: {success_rate:.2f}%"
        )

    # Final results
    print("\n=== Final Test Results ===")
    print(f"Total Cycles: {cycles}")
    print(f"Total Resolution Changes: {cycles * 2}")
    print(f"Successful Changes: {success}")
    print(f"Failed Changes: {failure}")
    print(f"Success Rate: {(success / (cycles * 2)) * 100:.2f}%")


if __name__ == "__main__":
    run_timing_test(50)
