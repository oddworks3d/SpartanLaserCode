# Spartan Laser Software
Code repository for the software running on the Spartan Laser.
Created using micropython

The software features the ability to adjust various settings using the Pi Pico and buttons on the Spartan Laser.
on power off, It remembers the current `state` and servo positions of the Spartan Laser for when you next power it on. 
it features pretty flickering lights! 

# Installation

### Get thonny
To get the code onto the pico, you first need to download and install Thonny: https://thonny.org (It has builds for Windows, Mac and Linux)

### Flash micropython to Pi Pico
Once installed, head to Run in the top menu bar, then Select Interpreter, then in the dropdown that asks you what interpreter you want to use, select `MicroPython (Raspberry Pi Pico)`

Near the bottom, hit `install or update firmware` and follow the on screen instructions to flash MicroPython to the pico.

### Copy files to the Pi Pico
Download the latest release from https://github.com/oddworks3d/SpartanLaserSoftware/releases and extract it.

Inside should be three files: main.py,ssd1306.py, and config

Inside Thonny, open up main.py, then hit the `Restart / stop backend` button (red one) at the top of Thonny (This will connect Thonny to your Pi Pico)
Now save the file main.py to the pi pico by hitting File -> Save -> Raspberry Pi Pico and saving it in the root directory.

Repeat the same steps for the other files, all going into the root directory of the Pico 

The Spartan Laser code is now installed on your Pi Pico and ready to go!


# Settings Menu
To enter the settings menu, hold down the `open / close` button while powering the pico on.
The settings menu has three top level options of
- Servo Settings
- Light Settings
- Misc Settings

#### Servo Settings
In servo settings, you can adjust the start and end position of the servo, whether or not it's inverted (do not adjust this), the speed and the pin. 
The only thing you should need to change in here is the start and end values (and pins if you wish).

#### Light Settings
In light settings, you can adjust the pin, length of the neopixel strip, and whether the light flickers or not.

#### Misc Settings
In Misc Settings, you can adjust the barrel LED pin and the vibration motor pin.

# Calibrate Servo Endstops
if the servo starts and ends incorrectly, use the follow steps to adjust their start and end positions.
- Enter the settings menu by holding down the `open / close` button while powering the pico on
- Pull the trigger to enter the servo settings
- use the `cooldown` button and `open / close` buttons to navigate to the servo you want to adjust and pull the trigger
- navigate to either the start or end position and pull the trigger to adjust the start / end position (WARNING you can only adjust one servo at a time, when you adjust the start / end position, the servo will jump to the position you are currently adjusting!!)
- Once you're done, pull the trigger to back out of adjusting the position
- To exit, navigate to back and pull the trigger, then navigate to back again and pull the trigger, and finally navigate to Save And Exit and pull the trigger to save the settings and restart the pico.

You must hit save and exit for your settings to be saved.

