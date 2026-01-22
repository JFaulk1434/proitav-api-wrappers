import asyncio
import websockets
import requests
import json
import time
from statistics import mean


class IPD960_API:
    def __init__(self, ip_address, username="admin", password="QXRsb25h"):
        self.ip_address = ip_address
        self.base_url = f"http://{ip_address}/api/v1"
        self.ws_url = f"ws://{ip_address}/ws"
        self.username = username
        self.password = password
        self.token = None
        self.websocket = None

    async def connect(self):
        """Login and establish WebSocket connection"""
        # First get token via REST
        login_url = f"{self.base_url}/auth/login"
        payload = {"username": self.username, "password": self.password}
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        try:
            print("\nDebug - Login attempt")
            response = requests.post(login_url, json=payload, headers=headers)
            print(f"Login Response Status: {response.status_code}")
            print(f"Login Response Body: {response.text}")

            if response.status_code == 200:
                response_data = response.json()
                self.token = response_data.get("token")
                print(f"Login successful! Token: {self.token}")

                # Now establish WebSocket connection
                headers = {"Sec-WebSocket-Protocol": f"Token {self.token}"}
                self.websocket = await websockets.connect(
                    self.ws_url, extra_headers=headers
                )
                print("WebSocket connection established")
                return True
            return False
        except Exception as e:
            print(f"Connection failed: {str(e)}")
            return False

    async def set_resolution(self, resolution):
        """Set video output resolution via WebSocket"""
        if not self.websocket:
            if not await self.connect():
                return False

        command = {
            "cmd": "set",
            "path": "/video/output/timing",
            "data": {"timing": resolution},
        }

        try:
            print(f"\nDebug - Set Resolution")
            print(f"Command: {command}")

            await self.websocket.send(json.dumps(command))
            response = await self.websocket.recv()
            print(f"Response: {response}")

            response_data = json.loads(response)
            return response_data.get("code") == 0  # Assuming 0 means success
        except Exception as e:
            print(f"Set resolution failed: {str(e)}")
            if "connection is closed" in str(e):
                print("Attempting to reconnect...")
                if await self.connect():
                    return await self.set_resolution(resolution)
            return False

    async def close(self):
        """Close WebSocket connection"""
        if self.websocket:
            await self.websocket.close()


async def run_resolution_test(device_ip, cycles=10):
    device = IPD960_API(device_ip)
    success = 0
    failure = 0
    switch_times = []

    print(f"\nStarting timing test for {cycles} cycles...")
    print("Each cycle will switch between 1080p and 4K resolution")

    try:
        for i in range(cycles):
            print(f"\nCycle {i + 1}/{cycles}")

            # Test 1080p
            print("Setting to 1080p...")
            start_time = time.time()
            if await device.set_resolution("1920x1080"):
                success += 1
                switch_time = time.time() - start_time
                switch_times.append(switch_time)
                print(f"Switch completed in {switch_time:.2f} seconds")
            else:
                failure += 1
                print("Switch failed!")

            # Test 4K
            print("Setting to 4K...")
            start_time = time.time()
            if await device.set_resolution("3840x2160@60"):
                success += 1
                switch_time = time.time() - start_time
                switch_times.append(switch_time)
                print(f"Switch completed in {switch_time:.2f} seconds")
            else:
                failure += 1
                print("Switch failed!")

            # Print running statistics
            total = success + failure
            success_rate = (success / total) * 100 if total > 0 else 0
            print(
                f"Current Stats - Success: {success}, Failures: {failure}, "
                f"Success Rate: {success_rate:.2f}%"
            )

    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    finally:
        await device.close()

        # Final results
        print("\n=== Final Test Results ===")
        print(f"Total Cycles: {cycles}")
        print(f"Total Resolution Changes: {cycles * 2}")
        print(f"Successful Changes: {success}")
        print(f"Failed Changes: {failure}")
        print(f"Success Rate: {(success / (cycles * 2)) * 100:.2f}%")

        if switch_times:
            print("\n=== Timing Statistics ===")
            print(f"Fastest Switch: {min(switch_times):.2f} seconds")
            print(f"Slowest Switch: {max(switch_times):.2f} seconds")
            print(f"Average Switch: {mean(switch_times):.2f} seconds")
            print(f"Total Switches Timed: {len(switch_times)}")


if __name__ == "__main__":
    DEVICE_IP = "10.0.30.11"
    asyncio.run(run_resolution_test(DEVICE_IP, cycles=2))
