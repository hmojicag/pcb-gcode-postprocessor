from os import listdir
from os.path import isfile, join

print('PCB-Gcode-Postprocessor running...')

# Find the Drill and Etching files in this directory
filesInDir = [f for f in listdir('.') if isfile(join('.', f))]
gcodeDrillFiles = []
gcodeEtchFiles = []
for f in filesInDir:
    if f.endswith('drill.tap'):
        print('Found Drill File: ' + f)
        gcodeDrillFiles.append(f)
    if f.endswith('etch.tap'):
        print('Found Etching File: ' + f)
        gcodeEtchFiles.append(f)

if len(gcodeDrillFiles) == 0:
    print('No Drill Files Found')
if len(gcodeEtchFiles) == 0:
    print('No Etching Files Found')

if len(gcodeDrillFiles) == 0 and len(gcodeEtchFiles) == 0 :
    print('Nothing to do here :D ....Exit application...')
    quit()
    
# PostProcess the etch.tap file function
# ---------------------------------------------------------------
def postProcessEtchFile(fileName):
    with open(fileName, 'r') as f:
        # Read the file to a list
        f_list = f.readlines()

    #Delete any comment line
    #On GCode, comments are in parenthesis
    f_post = []
    file_size = len(f_list)
    for i in range(0, file_size):
        line = f_list.pop(0) #Pop next item on list
        if not line.startswith('(') and line:
            f_post.append(line)
            # This line is not a comment and is not empty
            if line.startswith('M05'):
                # This is a Turn Off Spindle function
                # Check if we are almost at the end of the file
                if i > (file_size - 5):
                    #Append a Go Home
                    f_post.append('G00 X0.0000 Y0.0000\n')
                else:
                    print('This M05 is not at the end of the file')

    # Write changes on file
    with open('ArduinoShield.bot.etch.tap', 'w') as f:
        # Replace file content
        for line in f_post:
            f.write(line)
        
# ---------------------------------------------------------------
# Postprocess the .drill.tap file funtion
def postProcessDrillFile(fileName):
    with open(fileName, 'r') as f:
        # Read the file to a list
        f_list = f.readlines()

    f_post = []
    file_size = len(f_list)
    is_change_drill_block = False
    moving_G0_Z_pos = ''
    for i in range(0, file_size):
        line = f_list.pop(0) #Pop next item on list
        block_this_line = False
        if not line.startswith('(') and line:
            # This line is not a comment and is not empty
            if line.startswith('M05'):
                # This line starts the drill change code block
                is_change_drill_block = True
            if is_change_drill_block and line.startswith('G00 Z'):
                # Store the G0 travel position
                moving_G0_Z_pos = line
            if not is_change_drill_block and line.startswith('T'):
                # Don't add Change tool codes
                block_this_line = True
            if not is_change_drill_block and not block_this_line:
                # Add the line to the file
                f_post.append(line)
            if is_change_drill_block and line.startswith('M03'):
                # This line ends the drill change code block
                f_post.append(moving_G0_Z_pos)
                is_change_drill_block = False
            if not is_change_drill_block and line.startswith('G90'):
                #Insert a M03 at the beginning of the file (after the G90)
                f_post.append('M03\n')
            if line.startswith('M02'):
                # This is the last command on the file
                f_post.append('M05\n') #Turn Off Spindle
                f_post.append('G00 X0.0000 Y0.0000\n') #Go Home
                f_post.append('M02\n') #End program

    # Write changes on file
    with open('ArduinoShield.bot.drill.tap', 'w') as f:
        # Replace file content
        for line in f_post:
            f.write(line)
        

# ---------------------------------------------------------------
# Execution


for etchFile in gcodeEtchFiles:
    print('Processing ' + etchFile + '...')
    postProcessEtchFile(etchFile)

for drillFile in gcodeDrillFiles:
    print('Processing ' + drillFile + '...')
    postProcessDrillFile(drillFile)

print('My job is done here .... exit app ....')