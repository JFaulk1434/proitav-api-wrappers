import socket


class BrightSign:
    """For BrightSign Players focused on UDP commands to select video files"""

    def __init__(self, name, ip, commands, port=5000):
        self.name = name
        self.ip = ip
        self.port = port
        self.commands = commands
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.is_movie = False
        self.last_command = None

    def __str__(self) -> str:
        return f"{self.name} - {self.ip}"

    def message(self, message):
        # Encode message and send to BrightSign
        self.socket.sendto(message.encode("ascii"), (self.ip, self.port))
        if message == "movie":
            self.is_movie = True
        else:
            self.is_movie = False

    def send_command(self, command):
        # Select Movie to play
        self.message("home")
        self.message(command)

        self.last_command = command

    def reboot(self):
        # Reboots player
        self.message("home")
        self.message("reboot")
        return f"Rebooting BrightSign {self.name}@{self.ip}"

    def restart_movie(self):
        """Restarts the movies"""
        self.message("home")
        self.message("movie")
        return f"Restarting movie on {self.name}@{self.ip}"
