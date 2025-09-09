import os
import re

def set_line_feedrate(line, feedrate):
    # print(f"In set_line_feedrate and line is {line}, feedrate: {feedrate}")
    stripped_line = line.strip()
    new_feedrate_line = stripped_line
    if 'F' in line:
        line_before_F = stripped_line.split('F')[0]
        new_feedrate_line = f'{line_before_F} F{str(feedrate)}\n'
        print(f"In set_line_feedrate, F in line and line_before_F: {line_before_F}, new_feedrate_line: {new_feedrate_line.strip()}")
    else:
        new_feedrate_line = f'{stripped_line} F{str(feedrate)}\n'
        print(f"In set_line_feedrate, NO F in line, new_feedrate_line: {new_feedrate_line.strip()}")
        
    print(f"setting feedrate line {new_feedrate_line.strip()}")
    return new_feedrate_line
        
def get_z_value(line):
    # Split by spaces to get the different sections then isolate the one with the Z value
    for part in line.split(): # Assuming space before and after Z number part, seems safe
        if part.startswith('Z'):
            z_string = part[1:] # Assuming Z is the only character before numbers start
            # print(f'In get_z_value, part was {part} and z_string is {z_string}')
            break
    z_value = float(z_string)
    # print(f'In get_z_value, z_value was {z_value}')
    return z_value

def get_highest_z_value(lines):
    z_max = 0
    for line in lines:
        if 'G1' in line:
            if 'Z' in line:
                z_value = get_z_value(line)
                if z_value > z_max:
                    z_max = z_value
    return z_max

def adjust_gcode_feedrate(file_path, output_path):

    desired_travel_feedrate = 300 # EDIT THIS VALUE TO SET YOUR DESIRED FEEDRATE
    clearance_offset = 0.5 # EDIT THIS OFFSET! Distance below the max Z height that we'll consider travel moves. In Fusion: Heights tab -> Clearance Height -> Offset

    # Read the original G-code file
    with open(file_path, 'r') as file:
        lines = file.readlines()
        
    # Set state variables
    new_lines = []
    in_travel = False
    previous_feedrate = None
    first_line_after_travel = False
    z_max = get_highest_z_value(lines)
    travel_threshold_height = z_max - clearance_offset
    ignore_line_characters = ['%', '(', 'N']
    print(f"z_max: {z_max}, travel_threshold_height: {travel_threshold_height}")
    
    # Process each line of G-code
    for index, line in enumerate(lines):
        line_number = index + 1
        # print(f'line_number: {line_number}, z_max: {z_max}')
        new_line = line
        stripped_line = line.strip()
        
        if line[0] in ignore_line_characters:
            print(f"First characters was in ignore_line_characters. Skipping line {line_number}. Line was {line.strip()}")
        
        else:
            if 'F' in line: # Regardless of type of move (G0, G1, G3 etc.) if there is a feedrate we store it as the previous_feedrate
                # print(f'F in line number {line_number}')
                line_feedrate = float(stripped_line.split('F')[1])
                previous_feedrate = line_feedrate # Always set previous_feedrate to the current feedrate

            if 'G0' in line:
                # print(f"G0 in line {line_number}")
                # Fusion 360 only uses a couple G0 moves at the beginning
                if 'Z' in line:
                    z_value = get_z_value(line)
                    if z_value >= travel_threshold_height:
                        # If we have Z, it has to be positive to set to fast travel
                        # I think Fusion never uses G0 for unsafe moves with Z<0 but better safe than sorry
                        new_line = set_line_feedrate(line, desired_travel_feedrate)
                else:
                    # If we are not moving in Z, it's safe to do fast travel
                    new_line = set_line_feedrate(line, desired_travel_feedrate)
            
            if 'G1' in line:
                # print(f'G1 in line {line_number}')
                if 'Z' in line:
                    # print(f'Z in line {line_number}')
                    z_value = get_z_value(line)
                    if z_value >= travel_threshold_height:
                        print(f"Z >= threshold on line {line_number}, we are in travel moves!")
                        new_line = set_line_feedrate(line, desired_travel_feedrate)
                        in_travel = True
                    else: # Unsafe move, Z is in material <0
                        if in_travel:
                            print(f"Z < threshold on line {line_number}, we are no longer in travel!")
                            first_line_after_travel = True # This should become true when we are (were) in travel but Z is now <0
                            in_travel = False
                if in_travel:
                    new_line = set_line_feedrate(line, desired_travel_feedrate)
                else:
                    if first_line_after_travel:
                        if 'F' not in line: # If there's already a feedrate for the first line after travel, just leave it
                            new_line = set_line_feedrate(line, previous_feedrate)
                            first_line_after_travel = False
                        
        # Append the modified line to the new lines list
        new_lines.append(new_line)

    # Write the modified G-code to the output file
    with open(output_path, 'w') as file:
        file.writelines(new_lines)

    print(f"Adjusted G-code saved to {output_path}")

def process_all_gcode_files():
    # Get current directory
    current_dir = os.getcwd()
    # Create a new folder called "speedy"
    output_folder = os.path.join(current_dir, 'speedy')
    os.makedirs(output_folder, exist_ok=True)

    # Iterate through all files in the current directory
    for file_name in os.listdir(current_dir):
        # Check if the file is a G-code file (ends with .nc or .gcode)
        if file_name.lower().endswith(('.nc', '.gcode')):
            file_path = os.path.join(current_dir, file_name)
            # Create new file name with "_speedy" appended
            output_file_name = f"{os.path.splitext(file_name)[0]} speedy{os.path.splitext(file_name)[1]}"
            output_file_path = os.path.join(output_folder, output_file_name)
            # Adjust the G-code feed rate
            adjust_gcode_feedrate(file_path, output_file_path)

# Run the script to process all G-code files
process_all_gcode_files()
