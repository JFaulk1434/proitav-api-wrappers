import requests
import json
from time import sleep

# Configure Kodi server settings
KODI_IP = "10.0.110.207"  # Replace with your Raspberry Pi's IP
KODI_PORT = "8080"
KODI_USER = "admin"  # Add username if set in Kodi
KODI_PASS = "Hdmi0525!"  # Add password if set in Kodi


# Function to send JSON-RPC requests to Kodi with logging
def kodi_request(method, params=None):
    url = f"http://{KODI_IP}:{KODI_PORT}/jsonrpc"
    headers = {"content-type": "application/json"}
    payload = {"jsonrpc": "2.0", "method": method, "id": 1}
    if params:
        payload["params"] = params

    print(
        f"Sending request to Kodi: {json.dumps(payload, indent=2)}"
    )  # Log the request payload

    response = requests.post(
        url, data=json.dumps(payload), headers=headers, auth=(KODI_USER, KODI_PASS)
    )

    if response.status_code == 200:
        # print("Received response from Kodi:", response.json())  # Log the response
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")  # Log any errors
        return None


# Play a media file
def play_movie(file_name):
    params = {"item": {"file": f"/home/admin/Videos/{file_name}"}}
    kodi_request("Player.Open", params)


def play_image(file_name="all"):
    """
    Plays a single image or starts a slideshow of all images in the specified directory.

    Parameters:
    file_name (str): The name of the image file to display. If set to "all",
                     a slideshow of all images in the directory will start.
    """
    # Stop any current playback to ensure a fresh start
    stop_playback()

    if file_name == "all":
        # Start a slideshow with all images in the directory
        params = {
            "item": {
                "path": "/home/admin/Videos/Images",  # Directory containing images
                "recursive": True,
            },
            "options": {
                "shuffled": False  # Shuffle images in the slideshow
            },
        }
    else:
        # Display a single image by specifying just the path
        params = {
            "item": {
                "path": f"/home/admin/Videos/Images/{file_name}"  # Specific image file
            }
        }

    # Send the request to Kodi
    response = kodi_request("Player.Open", params)
    print("Kodi response:", response)  # Print response for verification


# Pause/Play toggle
def pause_play():
    params = {"playerid": 1}
    kodi_request("Player.PlayPause", params)


def set_repeat(mode="all"):
    """
    Sets the repeat mode of the player in Kodi.

    Parameters:
    mode (str): The repeat mode to set. Options are:
        - "off": No repeat.
        - "one": Repeat the current item.
        - "all": Repeat all items.
        - "cycle": Cycle through repeat modes.
        Defaults to "all".
    """
    params = {"playerid": 1, "repeat": mode}

    # Send the request to Kodi
    response = kodi_request("Player.SetRepeat", params)
    print("Kodi response:", response)  # Print response for verification


# Skip forward or backward by a given number of seconds
def seek(seconds):
    params = {"playerid": 1, "value": {"seconds": seconds}}
    kodi_request("Player.Seek", params)


# Seek to a specific time in the video
def seek_to_time(hours, minutes, seconds):
    params = {
        "playerid": 1,
        "value": {"time": {"hours": hours, "minutes": minutes, "seconds": seconds}},
    }
    kodi_request("Player.Seek", params)


# Stop playback
def stop_playback():
    params = {"playerid": 1}
    kodi_request("Player.Stop", params)


# Restart the video by stopping and replaying the file
def restart_video():
    seek_to_time(0, 3, 0)


# Toggle captions on/off
def toggle_captions():
    # First, get the current subtitle status
    player_id = 1
    subtitle_status = kodi_request(
        "Player.GetProperties",
        {"playerid": player_id, "properties": ["subtitleenabled"]},
    )

    # If subtitleenabled is returned, toggle it
    if "result" in subtitle_status:
        current_status = subtitle_status["result"].get("subtitleenabled", False)
        # Toggle subtitles
        params = {
            "playerid": player_id,
            "subtitle": "on" if not current_status else "off",
        }
        kodi_request("Player.SetSubtitle", params)


# Set the view mode for the video player
def set_video_view_mode(viewmode="normal"):
    """
    Sets the view mode for the currently playing video in Kodi.

    Parameters:
    viewmode (str or dict): The view mode to apply to the video. Available options include:
        - Predefined view modes (str): "normal", "zoom", "stretch4x3", "widezoom", "stretch16x9",
                                       "original", "stretch16x9nonlin", "zoom120width", "zoom110width"
        - Custom view modes (dict): {"zoom": float, "verticalshift": float} or {"pixelratio": float}

    Default is "normal".

    Example usage:
        set_video_view_mode("widezoom")  # Predefined view mode
        set_video_view_mode({"zoom": 1.6, "verticalshift": 0.5})  # Custom view mode
    """
    params = {"viewmode": viewmode}
    kodi_request("Player.SetViewMode", params)
    pause_play()
    pause_play()


def send_notification(title, message, seconds=5):
    """
    Shows a GUI notification on Kodi.

    Parameters:
    title (str): The title of the notification.
    message (str): The body message of the notification.
    seconds (int): The duration in seconds for which the notification will be visible (default is 5 seconds).
    """
    # Convert seconds to milliseconds as required by Kodi
    display_time = seconds * 1000

    # Define the parameters for the JSON-RPC call
    params = {"title": title, "message": message, "displaytime": display_time}

    # Send the request to Kodi
    response = kodi_request("GUI.ShowNotification", params)
    print("Kodi response:", response)  # Print response for verification


# Main program with CLI-based controls
if __name__ == "__main__":
    ready_player = "Ready.Player.One.mkv"
    guardians2 = "Guardians.of.the.galaxy.vol.2.mkv"
    send_notification("Message from Justin...", "I'm a badass", 5)
    print("Playing file...")

    print("Commands:")
    print(" - Type 'm1' to play Guardians 2")
    print(" - Type 'm2' to play Ready Player One")
    print(" - Type 'image' to play all images in slideshow")
    print(" - Type 'image {image_name}' to play an image file")
    print(" - Type 'p' to Pause/Play")
    print(" - Type 'f' to skip forward 60 seconds")
    print(" - Type 'b' to rewind 60 seconds")
    print(" - Type 'r' to restart the video")
    print(" - Type 'c' to toggle captions on/off")
    print(" - Type 's' to stop playback")
    print(" - Type '1' for view mode: normal")
    print(" - Type '2' for view mode: widezoom")
    print(" - Type '3' for view mode: original")
    print(" - Type 'q' to quit")

    while True:
        command = input("Enter command: ").strip().lower()
        if command == "p":
            pause_play()
        elif command == "m1":
            play_movie(guardians2)
            sleep(3)
            seek_to_time(0, 0, 45)
            set_repeat("one")
        elif command == "m2":
            play_movie(ready_player)
            sleep(3)
            seek_to_time(0, 0, 45)
            set_repeat("one")
        elif command.startswith("image"):
            # Check if an image name is provided after "image"
            parts = command.split()
            if len(parts) > 1:
                image_name = parts[1]
                play_image(image_name)  # Play specific image
            else:
                play_image("all")  # Start slideshow with all images
        elif command == "f":
            seek(60)  # Skip forward 60 seconds
        elif command == "b":
            seek(-60)  # Rewind 60 seconds
        elif command == "r":
            restart_video()  # Restart the video from the beginning
        elif command == "c":
            toggle_captions()  # Toggle captions
        elif command == "s":
            stop_playback()  # Stop playback
        elif command == "1":
            set_video_view_mode("normal")  # Set view mode to normal
        elif command == "2":
            set_video_view_mode("widezoom")  # Set view mode to widezoom
        elif command == "3":
            set_video_view_mode("original")  # Set view mode to original
        elif command == "q":
            print("Exiting...")
            break
        else:
            print("Unknown command. Please try again.")
