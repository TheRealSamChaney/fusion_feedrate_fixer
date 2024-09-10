# Fusion Feedrate Fixer!
## Fusion Feedrate Fixer is a Python script to fix the slow travel feedrate for Fusion 360 CAM free version

### Disclaimer!
* This version currently only works with inch units!
* This is an experimental program. I take no responsibility for any damage or harm cause by running gcode output by this script. It's solely your responsibility to review the gcode output before running it!

### How to use
* Download the main fusion_feedrate_fixer.py file
* Edit the file, and change desired_travel_feedrate to your desired travel feedrate then save. It's 300in/min be default
* Change the clearance_offset to what you have set in Fusion CAM heights tab -> Clearance Height -> Offset. It's 0.4in by default
* Move fusion_feedrate_fixer.py to your folder that contains the gcode files you want to fix
* Run it by starting cmd in that location and typing "python fusion_feedrate_fixer.py"
  * This will create a new folder called speedy and fill it with the fixed gcode files
  * That's it!