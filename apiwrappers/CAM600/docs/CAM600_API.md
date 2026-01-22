	V1.0	Austin
2024.05.10
First version

	V1.1
Austin
2024.05.28

Update some CMD

	V1.2
   Austin
2024.07.28
	Update some CMD

 
Contents
1	Introduction	3
1.1	Preparation	3
1.1.1	Setting IP Address in Your Computer	3
1.1.2	Enabling Telnet Client	3
1.2	Logging In via Command-line Interface	3
1.3	Introduction to Terminology	4
1.4	API Commands Overview	5
1.4.1	gbconfig Commands	5
1.4.2	gbcontrol Commands	6
2	Command Sets	6
2.1	gbconfig Commands	6
2.1.1	gbconfig --device-name	6
2.1.2	gbconfig --room-name	7
2.1.3	gbconfig --lan-info	7
2.1.4	gbconfig --ip-conflict	8
2.1.5	gbconfig --standby-indicator	8
2.1.6	gbconfig --camera-mode	8
2.1.7	gbconfig --camera-autocoord	9
2.1.8	gbconfig --camera-zoom	9
2.1.9	gbconfig --camera-savecoord	10
2.1.10	gbconfig --camera-loadcoord	10
2.1.11	gbconfig --reset-camera-ptz	10
2.1.12	gbconfig --camera-mirror	11
2.1.13	gbconfig --camera-powerfreq	11
2.1.14	gbconfig --camera-hd	11
2.1.15	gbconfig --camera-offtracking	12
2.1.16	gbconfig --camera-autoframing	12
2.1.17	gbconfig --camera-autoframingspeed	13
2.1.18	gbconfig --camera-speakertracking	13
2.1.19	gbconfig --camera-speakertrackingspeed	14
2.1.20	gbconfig --camera-presentertracking	14
2.1.21	gbconfig --show	15
2.1.22	gbconfig --help	16
2.2	gbcontrol Commands	17
2.2.1	gbcontrol --reboot	17
2.2.2	gbcontrol --reset-to-default	17
2.2.3	gbcontrol --device-info	17
2.2.4	gbcontrol --camera-info	18
2.2.5	gbcontrol --help	18
3	Appendix	19
4	FAQ	20
 
1	Introduction

1.1	Preparation
This section takes a third party control device windows 7 as an example. You may also use other control devices.
1.1.1	Setting IP Address in Your Computer
The detailed operation steps are omitted here.
1.1.2	Enabling Telnet Client
Before logging in to IP controller via command-line interface, make sure that Telnet Client is enabled. By default, Telnet Client is disabled in Windows OS. To turn on Telnet Client, do as follows.
1.	Choose Start > Control Panel > Programs.
2.	In Programs and Features area box, click Turn Windows features on or off. 
3.	In Windows Features dialog box, select Telnet Client check box.
 
1.2	Logging In via Command-line Interface
4.	Choose Start > Run.
5.	In the Run dialog box, enter cmd then click OK.
 
6.	Enter telnet 192.168.0.71 23 if the device's IP address is 192.168.0.71, and then press Enter.
  
7.	When the device prompts login, input admin and press Enter, then the device prompts password, just press Enter directly because the user admin has no default password. 
  
Now, the device is ready to execute the CLI API command.
1.3	Introduction to Terminology
The terminology used in API command description is listed as follows.
Terminology	Description
Device	The CAM600-000 unit being controlled.

PTZ
PTZ stands for Pan/Tilt/Zoom, which represents pan tilt movement in all directions, as well as lens zoom and zoom control.

UVC	USB Video Class, a protocol standard defined for USB video capture devices.
Camera	Main Lens
1.4	
1.4	

1.4	
1.4	

1.4	
1.4	

1.4	
1.4	

1.4	API Commands Overview
API commands of IP controller are mainly classified into the following types.
	gbconfig: manage the configurations of the device
	gbcontrol: control the device to do something
Every API command is supported by all models unless there is special comment in the context.
1.4.1	gbconfig Commands
Commands	Description
gbconfig --device-name
Configure the device’s name
gbconfig --room-name	Configure the device’s room name
gbconfig --lan-info	Configure the wired Ethernet settings
gbconfig --ip-conflict
Configure the IP conflict detection

gbconfig --standby-indicator	Configure the device’s standby led indicator status
gbconfig --camera-mode	Configure the camera’s tracking mode
gbconfig --camera-autocoord	Adjust the camera’s pan and tilt
gbconfig --camera-zoom	Configure the camera’s zoom
gbconfig --camera-savecoord	Set the camera’s preset
gbconfig --camera-loadcoord	Load the camera’s preset
gbconfig --reset-camera-ptz	Restore camera’s pan/tilt/zoom to defaults
gbconfig --camera-mirror
Configure the camera’s mirror and inverted mode open or close



gbconfig --camera-powerfreq
Configure the camera’s powerline frequency

gbconfig --camera-hd	Configure the camera’s hd mode open or close















gbconfig --camera-offtracking
Configure the camera’s off tracking mode detail config
gbconfig --camera-autoframing 
Configure the camera’s auto framing tracking mode detail config

gbconfig --camera-autoframingspeed
Configure the camera’s auto framing tracking speed

gbconfig --camera-speakertracking
Configure the camera’s speaker tracking mode detail config

gbconfig --camera-speakertrackingspeed
Configure the camera’s speaker tracking speed




gbconfig --camera-presentertracking
Configure the camera’s presenter tracking mode detail config
















gbconfig --show	Query the settings of a configuration item
gbconfig --help	Show a simple guide of all command
1.4.2	gbcontrol Commands
Command	Description
gbcontrol --reboot	Reboot the device
gbcontrol --reset-to-default
Restore the device factory defaults









gbcontrol --device-info	Obtain the information about the device model and firmware version
gbcontrol --camera-info
Obtain the information about the camera main model and motor firmware version




gbcontrol --help	Show a simple guide of all command
2	2	
2	

2	
2	

2	
2	

2	
2	

2	Command Sets
2.1	gbconfig Commands
2.1.1	gbconfig --device-name
Command	gbconfig --device-name DeviceName
Response	The device name will change to DeviceName.
Description	Configure the device’s name. As the factory default, the device name is the same as the device’s model.
Note:
The device name must be 1~20 characters in length, furthermore, it must include only letters, numbers and two special character ('_' and '-').

Example:
To change the name to CAM600:
Command:
gbconfig --device-name CAM600
Response:
The device name will change to CAM600.
2.1.2	gbconfig --room-name
Command	gbconfig --room-name RoomName
Response	The room name will change to RoomName.
Description	Configure the device’s room name. As the factory default, the device name is MeetingRoom.
Note:
The device name must be 1~20 characters in length, furthermore, it must include only letters, numbers and two special character ('_' and '-').
Example:
To change the name to MeetingRoom:
Command:
gbconfig --room-name MeetingRoom
Response:
The device name will change to MeetingRoom.

2.1.3	gbconfig --lan-info
Command	gbconfig --lan-info { ipmode ipaddr netmask gateway }

Response	The settings of the wired Ethernet will changed.
Description	ipmode = { 0:dhcp | 2:static }
ipaddr netmask gateway as xx.xx.xx.xx
The device supports two modes to obtain IP settings: DHCP and static. As a prompt, the new IP address will appear on the up-left corner of the screen if the operation is successful.
As the factory default, DHCP mode is used.
Example:
To use 192.168.1.88/24 as IP address and 192.168.1.1 as default gateway:
Command:
gbconfig --lan-info 2 192.168.1.88 255.255.255.0 192.168.1.1
Response:
The IP address will change.

2.1.4	gbconfig --ip-conflict
Command	gbconfig --ip-conflict { 0:n | 1:y }

Response	The IP conflict detection is enabled or disabled.

Description	








Configure whether the IP conflict detection is enabled. The argument “1” means to enable the IP conflict detection and vice versa.
As the factory default, the IP conflict detection is enabled.

Example:
To disable IP conflict detection:
Command:
gbconfig --ip-conflict 0
Response:
The IP conflict detection is disabled.

2.1.5	gbconfig --standby-indicator
Command	gbconfig --standby-indicator { 0:whiltebreath | 2:red | 255:off }

Response	The standby indicator is on or off.

Description	Configure how does the standby indicator came on when the device is idle. The argument “0” means the standby indicator as a white breathing light. “2” means to light the standby indicator red on. “255” means to turn off the standby-indicator.
As the factory default, the standby indicator is off.

Example:
To light the standby indicator as a white breathing light:
Command:
gbconfig --standby-indicator 0
Response:
The standby indicator will be light as a white breathing effect.



















2.1.6	gbconfig --camera-mode
Command	gbconfig --camera-mode { 0:off | 1:autoframing | 2:speakertracking | 3:presentertracking }

Response	The camera AI tracking mode feature is enabled or disabled.

Description	1. When camera tracking mode turn off, the camera pan, tilt and zoom can be control, set and load the camera preset; 
1. When change the camera tracking mode to auto framing, the camera will automatically select the appropriate scene based on the faces in the scene; 
2. When change the camera tracking mode to speaker tracking, the camera will locate the speaker based on their voice and automatically select a close-up of the speaker using facial recognition; 
3. When change the camera tracking mode to presenter tracking, the camera automatically recognizes the first speaker after startup and tracks the speaker in real-time; 
As the factory default, the camera AI tracking mode is off.
Example:
To change the camera tracking mode to auto framing:
Command:
gbconfig --camera-mode 1
Response:
The camera presenter tracking is enable, camera will automatically select the appropriate scene based on the faces in the scene.

2.1.7	gbconfig --camera-autocoord
Command	gbconfig --camera-autocoord { r | l | u | d }

Response	The camera will turn right, left, up or down.

Description	Control the camera angle adjustment.
As the factory default, camera in center position.
Note:
Only controllable when the camera AI tracking mode is turned off.
Example:
To control the camera turn left:
Command: 
gbconfig --camera-autocoord l
Response:
The camera turn left.

2.1.8	gbconfig --camera-zoom
Command	gbconfig --camera-zoom { 100 ~ phymaxzoom }

Response	The camera will zoom.

Description	Adjusting the camera zoom.
As the factory default, camera zoom is 100.
Note:
1. Only adjustable when the camera AI tracking mode is turned off.
2. The phymaxzoom can be obtained by executing “gbconfig -s camera-phymaxzoom”.

Example:
To adjust the camera to 2x zoom:
Command:
gbconfig --camera-zoom 200
Response:
The camera is zoomed in twice, and the image is enlarged.

2.1.9	gbconfig --camera-savecoord
Command	gbconfig --camera-savecoord { 1 ~ 9 }

Response	The current position information will be saved.

Description	Save the current position information of the lens as the preset position.
As the factory default, camera preset is empty.
Note:
When turning off camera AI tracking mode, preset 1 is the initial power on position. And the camera preset can be set.

Example:
To set the camera preset 1:
Command:
gbconfig --camera-savecoord 1
Response:
The camera preset 1 information will be saved.

2.1.10	gbconfig --camera-loadcoord
Command	gbconfig --camera-loadcoord { 1 ~ 9 }
Response	The selected camera preset will be loaded.
Description	The camera preset will be loaded as the current position.
As the factory default, camera preset is empty.
Note:
Only loadable when turning off camera AI tracking mode.
Example:
To load the camera preset 1:
Command: 
gbconfig --camera-loadcoord 1
Response:
The camera preset 1 information will be loaded.

2.1.11	gbconfig --reset-camera-ptz
Command	gbconfig --reset-camera-ptz
Response	The camera restore to the default initial position.
Description	Restore the camera’s angle and zoom to defaults.
Note:
Only operable when turning off camera AI tracking mode.
Example:
To restore the camera ptz:
Command:
gbconfig --reset-camera-ptz
Response:
The camera restore to the default initial position.




























2.1.12	gbconfig --camera-mirror
Command	gbconfig --camera-mirror Mirror Invert

Response	The camera image will be mirrored or inverted.

Description	Mirror = { 0: n | 1: y }
Invert = { 0: n | 1: y }
Make the camera image mirror or invert.
As the factory default, camera mirror and invert is disabled.
Example:
To make the camera mirror:
Command:
gbconfig --camera-mirror 1 0
Response:
The camera image will be mirrored.

2.1.13	gbconfig --camera-powerfreq 
Command	gbconfig --camera-powerfreq { 50:50Hz | 60:60Hz }

Response	The new setting will be saved.

Description	Configure the camera powerline frequency. Use to anti flicker.
As the factory default, the camera powerline frequency is 50Hz.

Example:
To change the camera powerline frequency to 60Hz:
Command:
gbconfig --camera-powerfreq 60
Response:
The camera powerline frequency will change to 60Hz.

2.1.14	gbconfig --camera-hd
Command	gbconfig --camera-hd { 0: n | 1: y }

Response	The camera will change its hd mode and the device restart automatically.

Description	Configure the camera hd mode. Turn on for better image quality and turn off for better compatibility.
As the factory default, this camera hd mode is turned on.
Note:
To complete this process, your device may take a few seconds to restart.
Example:
To close hd mode:
Command:
gbconfig --camera-hd 0
Response:
The setting will be saved, and the device restart.

2.1.15	gbconfig --camera-offtracking
Command	gbconfig --camera-offtracking Effect Pip Pos

Response	The pip mode is enable or disable, overlay the panoramic lens image in the bottom right or top left corner of the main lens.
Description	Effect = { 0: immediate | 1: smooth }
Pip = { 0: n | 1: y }
Pos = { 0: lu | 1: rd }
Configure whether the pip mode of camera off tracking mode is enabled. If it is enabled, the panoramic lens image will be overlay in the bottom right corner of the main lens. Support change the panoramic lens layout.
As the factory default, pip mode is disabled.
Note:
Effect not support to configure, immediate default.

Example:
To enable pip mode:
Command:
gbconfig --camera-offtracking 0 1 1
Response:
The panoramic lens image overlay in the bottom right corner of the main lens.

2.1.16	gbconfig --camera-autoframing
Command	gbconfig --camera-autoframing Effect Pip Pos
Response	The pip mode is enable or disable, overlay the panoramic lens image in the bottom right or top left corner of the main lens.
Description	Effect = { 0: immediate | 1: smooth }
Pip = { 0: n | 1: y }
Pos = { 0: lu | 1: rd }
Configure whether the pip mode of camera auto framing tracking mode is enabled. If it is enabled, the panoramic lens image will be overlay in the bottom right corner of the main lens. Support change the panoramic lens layout.
As the factory default, pip mode is disabled.
Note:
Reserve command.
Example:
To enable pip mode:
Command:
gbconfig --camera-autoframing 0 1 1
Response:
The panoramic lens image overlay in the bottom right corner of the main lens.

2.1.17	gbconfig --camera-autoframingspeed
Command	gbconfig --camera-autoframingspeed { 0: slow | 1: normal | 2: fast }
Response	The camera rotation speed wil be changed.
Description	Configure the camera auto framing tracking speed. 
As the factory default, the camera auto framing tracking speed is fast.
Example:
To slow the camera auto framing tracking speed:
Command:
gbconfig --camera-autoframingspeed 0
Response:
The camera auto framing tracking speed will be slowed.






















































2.1.18	gbconfig --camera-speakertracking
Command	gbconfig --camera-speakertracking Effect Pip Pos Disp
Response	The pip mode is enable or disable, overlay the panoramic lens image in the bottom right or top left corner of the main lens. Close-up of the characters full frame or split screen display.
Description	Effect = { 0: immediate | 1: smooth }
Pip = { 0: n | 1: y }
Pos = { 0: lu | 1: rd }
Disp = { 0: normal | 1: gallery }
Configure whether the pip mode of camera speaker tracking mode is enabled. If it is enabled, the panoramic lens image will be overlay in the bottom right corner of the main lens. Support change the panoramic lens layout. Configure whether close-up of the characters full frame display.
As the factory default, pip mode is disabled, display mode is normal.
Note:
Effect not support to configure, immediate default.
Example:
To enable pip mode:
Command:
gbconfig --camera-speakertracking 0 1 1 0
Response:
The panoramic lens image overlay in the bottom right corner of the main lens.

2.1.19	2.1.19		2.1.19	

2.1.19	
2.1.19	

2.1.19	
2.1.19	

2.1.19	gbconfig --camera-speakertrackingspeed
Command	gbconfig --camera-speakertrackingspeed { 0: slow | 1: normal | 2: fast }
Response	The camera rotation speed wil be changed.
Description	Configure the camera speaker tracking speed. 
As the factory default, the camera speaker tracking speed is fast.
Example:
To slow the camera speaker tracking speed:
Command:
gbconfig --camera-speakertrackingspeed 0
Response:
The camera speaker tracking speed will be slowed.

2.1.20	2.1.20		2.1.20	

2.1.20	
2.1.20	

2.1.20	
2.1.20	

2.1.20	gbconfig --camera-presentertracking
Command	gbconfig --camera-presentertracking Effect Pip Pos
Response	The pip mode is enable or disable, overlay the panoramic lens image in the bottom right or top left corner of the main lens.
Description	Effect = { 0: immediate | 1: smooth }
Pip = { 0: n | 1: y }
Pos = { 0: lu | 1: rd }
Configure whether the pip mode of camera presenter tracking mode is enabled. If it is enabled, the panoramic lens image will be overlay in the bottom right corner of the main lens. Support change the panoramic lens layout.
As the factory default, pip mode is disabled.
Note:
Effect not support to configure, immediate default.
Example:
To enable pip mode:
Command:
gbconfig --camera-presentertracking 0 1 1
Response:
The panoramic lens image overlay in the bottom right corner of the main lens.



















2.1.21	gbconfig --show
Command	gbconfig { --show | -s } { device-name | lan-info | camera-mode | camera-hd…}

Response	The current settings of the designated configuration item.
Description	Query the settings of a configuration item. Mostly, this command can be use to query the settings of every item configured by a gbconfig command. For some configuration items, such as lan-info, it will return the actual state information too.
Example 1:
To query the device name with the factory default:
Command:
gbconfig -s device-name
Response:
CAM600-000

Example 2:
To query wired Ethernet settings and state:
Command:
gbconfig -s lan-info
Response:
	If DHCP mode works:
0 192.168.0.56 255.255.240.0 192.168.2.1
The contents following “dhcp” are state information whose format is IPAddress NetMask Gateway.
	If DHCP mode failed:
no reply | invalid param
If Static mode works:
2 192.168.1.88 255.255.255.0 192.168.1.1
The contents following “static” are static settings whose format is the same as the command gbconfig --lan-info.

Example 3:
To query configuration of the camera mirror and invert:
Command:
gbconfig -s camera-mirror
Response:
0 0
The response has two fields, the first one is the configuration of camera mirror and the second one is the configuration of camera invert.

2.1.22	gbconfig --help
Command	gbconfig { --help | -h }
Response	A simple description of the all commands is shown.
Description		Show a simple guide of all commands

2.2	gbcontrol Commands
2.2.1	gbcontrol --reboot
Command	gbcontrol --reboot
Response	The device will reboot.
Description	Reboot the device manually
Example:
Command:
gbcontrol --reboot
Response:
The device start to reboot.

2.2.2	gbcontrol --reset-to-default
Command		gbcontrol --reset-to-default 

Response	The device configuration will restore to factory defaults and restart.

Description		This command make the device restore its factory defaults.
Example:
Command:
gbcontrol --reset-to-default 
Response:
The device will start to restore all factory defaults.




























2.2.3	gbcontrol --device-info
Command		gbcontrol --device-info
Response		The device prints its model, firmware version and build time.

Description	Obtain the information about the device model, firmware version and build time.
Example:
Command:
gbcontrol --device-info
Response:
		CAM600-000
		V1.0.11
		2024-04-29 20:06:50

2.2.4	gbcontrol --camera-info
Command	gbcontrol --camera-info

Response	The device prints firmware version of camera and motor module.

Description	Obtain the information about the camera and motor module firmware version .

Example:
Command:
gbcontrol --camera-info
Response:
		Main:V0.1.12
		Motor0:YMODEM-V3.97
		Motor1:YMODEM-V3.97










2.2.5	gbcontrol --help
Command	gbcontrol { --help | -h }
Response	A simple description of the all commands is shown.
Description		Show a simple guide of all commands

3	3	
3	

3	
3	

3	3	
3	

3	
3	

3	3	
3	

3	
3	

3	3	Appendix
[To be added]
4	FAQ
[To be added]
