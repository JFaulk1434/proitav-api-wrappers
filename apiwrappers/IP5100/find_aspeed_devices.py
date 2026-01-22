"Return a sorted list of all units found on the network"

import socket
import select
import struct
import subprocess
import re
import platform

VERSION = "1.0.0"
QUERY_PORT = 3333
QUERY_ADDR = "225.1.0.0"


def find_all_ip():
    """Find all IP addresses in the OS"""
    _platform = platform.system()
    ip_str = r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}"
    if _platform == "Darwin" or _platform == "Linux":
        ipconfig_process = subprocess.Popen("ifconfig", stdout=subprocess.PIPE)
        output = ipconfig_process.stdout.read()
        ip_pattern = re.compile(f"(inet {ip_str})")
        pattern = re.compile(ip_str)
        ip_list = []
        for ip_addr in re.finditer(ip_pattern, str(output)):
            ip_addr = pattern.search(ip_addr.group())
            if ip_addr.group() != "127.0.0.1":
                ip_list.append(ip_addr.group())
        return ip_list
    elif _platform == "Windows":
        ipconfig_process = subprocess.Popen("ipconfig", stdout=subprocess.PIPE)
        output = ipconfig_process.stdout.read()
        ip_pattern = re.compile(f"IPv4 .*: {ip_str}")
        pattern = re.compile(ip_str)
        ip_list = []
        for ip_addr in re.finditer(ip_pattern, str(output)):
            ip_addr = pattern.search(ip_addr.group())
            if ip_addr.group() != "127.0.0.1":
                ip_list.append(ip_addr.group())
        return ip_list
    else:
        return []


def search_nodes(query_port=QUERY_PORT, regular_expression=None, sort_key="HOSTNAME"):
    """Search all units, store them in a dictionary to avoid duplicates, and return a sorted list."""
    devices = {}
    sock_rcv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_rcv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock_rcv.bind(("0.0.0.0", query_port + 1))
    sock_rcv.setblocking(0)  # Non-blocking

    try:
        for _ in range(3):  # Number of times to send out the search
            for ip_addr in find_all_ip():
                sock_snd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock_snd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock_snd.bind((ip_addr, 0))
                try:
                    sock_snd.sendto(struct.pack("ii", 0, 0), (QUERY_ADDR, query_port))
                except socket.error as err:
                    print("send failed:", err)
                    exit(1)
                finally:
                    sock_snd.close()

            while True:
                events = select.select([sock_rcv], [], [], 0.3)
                if not events[0]:  # Timeout
                    break

                while True:
                    try:
                        data, addr = sock_rcv.recvfrom(1024)
                    except socket.error:  # No more data
                        break

                    try:
                        struct_data = struct.unpack("ii32s64s32s16s144s", data)
                        dev_name = (
                            struct_data[3]
                            .split(b"\x00")[0]
                            .decode("utf-8", errors="ignore")
                        )
                        if dev_name not in devices:
                            status = (
                                struct_data[2]
                                .split(b"\x00")[0]
                                .decode("utf-8", errors="ignore")
                                or "n/a"
                            )
                            model = (
                                struct_data[4]
                                .split(b"\x00")[0]
                                .decode("utf-8", errors="ignore")
                                or "n/a"
                            )
                            version = (
                                struct_data[5]
                                .split(b"\x00")[0]
                                .decode("utf-8", errors="ignore")
                                or "n/a"
                            )

                            device_dict = {
                                "HOSTNAME": dev_name,
                                "ADDRESS": addr[0],
                                "MODEL": model,
                                "VER": version,
                                "STATUS": status,
                            }
                            devices[dev_name] = device_dict
                    except Exception as e:
                        print(f"Error parsing packet: {e}")
                        continue
    finally:
        sock_rcv.close()

    # Sort the devices dictionary by key and return as list of values
    sorted_devices = sorted(devices.values(), key=lambda x: x[sort_key])
    return sorted_devices


# Example usage of modified function
if __name__ == "__main__":
    nodes = search_nodes()
    for node in nodes:
        print(node)
