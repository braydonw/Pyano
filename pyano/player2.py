#Libraries
import os  # used for finding .mid files in the project folder
import glob  # ^
import mido  # used to create, edit, or read .mid files
import time  # used for playing notes with proper time delay
from IOPi import IOPi #Library for IOPI Plus expansion board

##currently unused libraries
##import RPi.GPIO as GPIO #Library for RPi GPIO pins

#IO setup
bus1 = IOPi(0x20) #address for first bus
bus2 = IOPi(0x21) #address for second bus

bus1.set_port_direction(0, 0x00) #set channels 1-8 on bus 1 to output
                                 #first variable is the port (0 or1)
                                 #second variable is bit by bit assignment (0 = out, 1 = in)
bus1.set_port_direction(1, 0x00) #set channes 9-16 on bus 1 to output
bus2.set_port_direction(0, 0x00) #set channels 1-8 on bus 2 to output
bus2.set_port_direction(1, 0xC0) #set channels 9-15 on bus 2 to output
                                 #pin 16 is set to input for hardware control

##Old code for hardware control
##bus2.set_pin_pullup(15, 1) #enable the 100k pull-up resistor inside pin 15
##bus2.set_pin_pullup(16, 1) #enable the 100k pull-up resistor inside pin 16
##bus2.invert_pin(15, 1) #invert the pin reading to maintain an active high pin
##bus2.invert_pin(16, 1) #invert the pin reading to maintain an active high pin
##bus2.set_interrupt_defaults(1, 0x00) #set the default interrupt state to low
##bus2.set_interrupt_type(1, 0xFF) #interrupt is registered when the pin does not match the default
##bus2.set_interrupt_on_port(1, 0xC0) #interrupt monitoring is only enabled on pins 15 and 16 of bus 2
##bus2.reset_interrupts() #reset interrupt status
##bus2.set_interrupt_polarity(0) #set pin IA to active Low
##bus2.mirror_interrupts(1) #only mirror interrupts from port 1 to pin IA



#Initialize all outputs to 0
bus1.write_port(0, 0x00)
bus1.write_port(1, 0x00)
bus2.write_port(0, 0x00)
bus2.write_port(1, 0x00)

#-------------------------Variables-------------------------------------
off_check = False #check if the midi file has off commands
current_song = 0 #determines which song is being played
progress = 0 #progress of the current song

#Music control
pause = False #determines wether the song is paused or playing
skip = False #Skips the current song when set to True
back = False
stop = False #Used to end the whole player program

#-------------------------Functions-------------------------------------

#-----------------------------------------------------------------------
def play_file(mid):
    
    #global variables used in this function
    global current_song
    global progress
    global pause
    global skip
    global back
    global stop
    
    #variables
    message_count = 0 #used to keep track of progress of a song
    current_message = 0 #used to keep track of the progress of a song
    
    # get the type of MIDI file
    # type 0 (single track): all messages are saved in one track
    # type 1 (synchronous): all tracks start at the same time
    # type 2 (asynchronous): each track is independent of the others
    if mid.type == 0:
        print ("MIDI Type: 0 (currently unsupported)")
        return
    elif mid.type == 1:
        print ("MIDI Type: 1")
    elif mid.type == 2:
        print ("MIDI Type: 2 (currently unsupported)")
        return
    else:
        print ("MIDI Type Error")
        return

    # get the length of MIDI file in seconds
    print("Length: {}s".format(round(mid.length, 2)))

    # print file meta data
    print("---")
    for msg in mid:  # msg is each decoded MIDI message / line
        msg_data = str(msg)  # important
        if msg.is_meta:
            if msg.type == 'time_signature':
                print("TIME SIGNATURE:")
                temp1 = msg_data.find('numerator=')
                temp2 = msg_data.find('denominator=')
                numerator = msg_data[temp1 + 10:temp2]
                print('numerator: {}'.format(numerator))
                temp1 = msg_data.find('clocks_per_click=')
                denominator = msg_data[temp2 + 12:temp1]
                print('denominator: {}'.format(denominator))
                temp2 = msg_data.find('notated_32nd_notes_per_beat=')
                clocks_per_click = msg_data[temp1 + 17:temp2]
                print('clocks_per_click: {}'.format(clocks_per_click))
                temp1 = msg_data.find('time=')
                notated_notes = msg_data[temp2 + 28:temp1]
                print('notated_32nd_notes_per_beat: {}'.format(notated_notes))
            if msg.type == 'key_signature':
                # if no key_signature event occurs: C major is assumed (per MIDI standard)
                print("KEY SIGNATURE:")
                key_signature = 'C'
                temp1 = msg_data.find('key=')
                temp2 = msg_data.find('time=')
                key_signature = msg_data[temp1 + 5:temp2 - 2]
                print(key_signature)
            if msg.type == 'set_tempo':
                print("SET TEMPO:")
                temp1 = msg_data.find('tempo=')
                temp2 = msg_data.find('time=')
                set_tempo = msg_data[temp1 + 6:temp2]
                print(set_tempo)
    print("---")

    notes = set()  # testing note range of each MIDI file - build set of all unique notes & find min and max for key shifting


    
    # go through the MIDI file and collect note values
    for msg in mid:
        if not msg.is_meta:
            # ignore any program/control changes for now
            if msg.type != 'program_change' and msg.type != 'control_change':
                # if we made it this far then the message must be note_on/off type
                play_note_test(msg, notes)
                message_count = message_count + 1 #increment the message counter

    
    #skip this midi file if it does not have off commands
    if off_check == False:
        print()
        print("---------------------------------------------------------------------")
        print()
        print("This file cannot be played becuase it does not contain 'off' commands")
        print()
        print("---------------------------------------------------------------------")
        return
    
    
    # testing note range of each MIDI file
    min_value = min([int(i) for i in notes]) #the min and max values are strings from the MIDI file and need to be converted to ints
    max_value = max([int(i) for i in notes])
    range_notes = max_value - min_value
    adjust_value = min_value - 1 #the number that needs to be subtracted from every note to make it playable
    
    print("All Notes: {}".format(notes))
    print("Min Note: {} Max Note: {}".format(min_value, max_value))
    print("Range: ", range_notes)
    print("---")           
    print("Total Message Count: ", message_count)
    print("---")
    
    #go through MIDI File and actually play notes          
    for msg in mid:
        
        #music control check
        if pause == True: #what to do when the pause variable is true
            print()
            print("Pause")
            print()
            #turn off solenoids while song is paused
            bus1.write_port(0, 0x00)
            bus1.write_port(1, 0x00)
            bus2.write_port(0, 0x00)
            bus2.write_port(1, 0x00)
            
        while pause == True: #do not continue while pause variable is true     
            #This block needs to be in here so that skipping while paused is pausible
            if skip == True: #skip the rest of this song if the skip variable is true
                print()
                print("Skip")
                print()
                return    
            #needed for going back while paused
            if back == True:
                print()
                print("Back")
                print()
                if progress > 5: #only decrement by 1 if progress is greater than 5%
                    current_song = current_song - 1
                else: #decrement by 2 if progress is 5% or less
                    current_song = current_song - 2
                return
            #needed for ending the program while paused
            if stop == True: #ends the program
                return
            time.sleep(0.2) #Check every 200 miliseconds
    
        if skip == True: #skip the rest of this song if the skip variable is true
            print()
            print("Skip")
            print()
            return
        
        if back == True:
            print()
            print("Back")
            print()
            if progress > 5: #only decrement by 1 if progress is greater than 5%
                 current_song = current_song - 1
            else: #decrement by 2 if progress is 5% or less
                current_song = current_song - 2
            return
        
        if stop == True: #will end the program
            return
        
        #play next message after checking music control
        if not msg.is_meta:
            # ignore any program/control changes for now
            if msg.type != 'program_change' and msg.type != 'control_change':
                # if we made it this far then the message must be note_on/off type
                time.sleep(msg.time) # MUST GO BERFORE PLAY_NOTE FUNCTION
                play_note(msg, notes, adjust_value)
                
                #song progress
                current_message = current_message + 1
                progress_old = progress
                #print("Current Message: ", current_message) #I was using this for debugging 
                progress = int((current_message / message_count)*100) #saves the progress of the song as an intger value
                #comment the next 2 lines if you don't want to see the progress in terminal
                if progress_old != progress: #only print the progress when it updates
                    print ("{} % complete" .format(progress)) #output progress for debugging
    
    print("---------------End of Song-------------------")
    

#-------------------------------------------------------------------------
def play_note_test(msg, notes):
    msg_data = str(msg)
    temp1 = msg_data.find('note_')
    temp2 = msg_data.find('channel')
    status = msg_data[temp1 + 5:temp2]  # status = on or off
    temp1 = msg_data.find('note=')
    temp2 = msg_data.find('velocity=')
    note = msg_data[temp1 + 5:temp2]  # note represented as MIDI #
    notes.add(note)  # testing note range of each MIDI file
    
    #check if the midi file has off commands
    global off_check
    
    if status == 'off ':
        off_check = True
        
    return


#----------------------------------------------------------------------------
def play_note(msg, notes, adjust_value):
    msg_data = str(msg)
    temp1 = msg_data.find('note_')
    temp2 = msg_data.find('channel')
    status = msg_data[temp1 + 5:temp2]  # status = on or off (redundant: just use msg.type == 'note_on')
    temp1 = msg_data.find('note=')
    temp2 = msg_data.find('velocity=')
    note = msg_data[temp1 + 5:temp2]  # note represented as MIDI #
    note = int(note) - adjust_value #adjust notes to playable range

    #adjust for notes that are still outside the range of the piano
    while note > 24:
        note = note - 24

    #print to terminal for debug purposes
    #print("Note {} {}".format(note, status))
    
    # google easier way? use dictionaries??
    #Output to solenoids
    if status == 'off ':
        if note == 1:
            bus1.write_pin(1, 0)
        elif note == 2:
            bus1.write_pin(2, 0)
        elif note == 3:
            bus1.write_pin(3, 0)
        elif note == 4:
            bus1.write_pin(4, 0)
        elif note == 5:
            bus1.write_pin(5, 0)
        elif note == 6:
            bus1.write_pin(6, 0)
        elif note == 7:
            bus1.write_pin(7, 0)
        elif note == 8:
            bus1.write_pin(8, 0)
        elif note == 9:
            bus1.write_pin(9, 0)
        elif note == 10:
            bus1.write_pin(10, 0)
        elif note == 11:
            bus1.write_pin(11, 0)
        elif note == 12:
            bus1.write_pin(12, 0)
        elif note == 13:
            bus1.write_pin(13, 0)
        elif note == 14:
            bus1.write_pin(14, 0)
        elif note == 15:
            bus1.write_pin(15, 0)
        elif note == 16:
            bus1.write_pin(16, 0)
        elif note == 17:
            bus2.write_pin(1, 0)
        elif note == 18:
            bus2.write_pin(2, 0)
        elif note == 19:
            bus2.write_pin(3, 0)
        elif note == 20:
            bus2.write_pin(4, 0)
        elif note == 21:
            bus2.write_pin(5, 0)
        elif note == 22:
            bus2.write_pin(6, 0)
        elif note == 23:
            bus2.write_pin(7, 0)
        elif note == 24:
            bus2.write_pin(8, 0)
        elif note == 25:
            bus2.write_pin(9, 0)
            
    if status == 'on ':
        if note == 1:
            bus1.write_pin(1, 1)
        elif note == 2:
            bus1.write_pin(2, 1)
        elif note == 3:
            bus1.write_pin(3, 1)
        elif note == 4:
            bus1.write_pin(4, 1)
        elif note == 5:
            bus1.write_pin(5, 1)
        elif note == 6:
            bus1.write_pin(6, 1)
        elif note == 7:
            bus1.write_pin(7, 1)
        elif note == 8:
            bus1.write_pin(8, 1)
        elif note == 9:
            bus1.write_pin(9, 1)
        elif note == 10:
            bus1.write_pin(10, 1)
        elif note == 11:
            bus1.write_pin(11, 1)
        elif note == 12:
            bus1.write_pin(12, 1)
        elif note == 13:
            bus1.write_pin(13, 1)
        elif note == 14:
            bus1.write_pin(14, 1)
        elif note == 15:
            bus1.write_pin(15, 1)
        elif note == 16:
            bus1.write_pin(16, 1)
        elif note == 17:
            bus2.write_pin(1, 1)
        elif note == 18:
            bus2.write_pin(2, 1)
        elif note == 19:
            bus2.write_pin(3, 1)
        elif note == 20:
            bus2.write_pin(4, 1)
        elif note == 21:
            bus2.write_pin(5, 1)
        elif note == 22:
            bus2.write_pin(6, 1)
        elif note == 23:
            bus2.write_pin(7, 1)
        elif note == 24:
            bus2.write_pin(8, 1)
        elif note == 25:
            bus2.write_pin(9, 1)
        
   
     
    return

#--------------------------End of Functions----------------------------------



#-------------------------------Main--------------------------------------------
def main():
    
    #global variables that get modified in this function
    global off_check
    global progress
    global current_song
    global pause
    global skip
    global stop
    
    
##    #GPIO Setup --- Not currently used
##    #This has to be in the main function for it to work
##    GPIO.setmode(GPIO.BCM)
##    GPIO.setup(23, GPIO.IN,  pull_up_down=GPIO.PUD_OFF) #set pin 23 as input and dissable the internal 
##    GPIO.add_event_detect(23, GPIO.FALLING, callback=button_pressed) #detect a falling edge on pin 23

    # build and display midi_file_list from all .mid files in project directory
    midi_file_list = []
    os.chdir("/home/pi/pyano-git")
    #os.chdir("/Users/braydon/Documents/GitHub/Pyano")
    for midi_file in glob.glob("*.mid"):
        midi_file_list.append(midi_file)
    print("\nList of MIDI files in project folder:")
    #print(*midi_file_list, sep="\n")
    print("Total: {} files \n".format(len(midi_file_list)))
    
    #index the midi file list with a list of integers for easier access
    # I THINK THIS MAKES SONG_LIST THE SAME THING AS MIDI_FILE_LIST???
    song_list = [None] * len(midi_file_list)
    file_count = 0
    for midi_file in midi_file_list:
        song_list[file_count] = midi_file
        file_count += 1
        
##    # play each file in midi_file_list
##    file_count = 0
##    for midi_file in midi_file_list:  # midi_file is a string of the current MIDI file name
##        file_count = file_count + 1
##        mid = mido.MidiFile(midi_file)  # mid is the current mido MIDI file playing
##        print("Playing file {}: {}".format(file_count, midi_file))
##        play_file(mid)
##        print()
##        
##        off_check = False #reset off_check after every song
##        pause = False #reset the pause state so that the next song starts playing automatically
##        skip = False #set the skip variable to flase after every song
##        
##        #make sure all outputs are low before playing the next song
##        bus1.write_port(0, 0x00)
##        bus1.write_port(1, 0x00)
##        bus2.write_port(0, 0x00)
##        bus2.write_port(1, 0x00)
##        
##        #reset progress bar before playing next song
##        progress = 0
    
    file_count_max = file_count #number of the last song in the list
    while stop == False:
        mid = mido.MidiFile(song_list[current_song]) # midi_file is a string of the current MIDI file name
        print("playing File: ", song_list[current_song]) # mid is the current mido MIDI file playing
        play_file(mid)
        print()
        
        off_check = False #reset off_check after every song
        pause = False #reset the pause state so that the next song starts playing automatically
        skip = False #set the skip variable to flase after every song
        back = False #reset back variable after every song
        
        #make sure all outputs are low before playing the next song
        bus1.write_port(0, 0x00)
        bus1.write_port(1, 0x00)
        bus2.write_port(0, 0x00)
        bus2.write_port(1, 0x00)
        
        current_song += 1 #increment current song so that the next song plays automatically
        
        if current_song < 0: #in case of trying to go back during the first song
            current_song = 0
            
        if current_song == file_count_max: #ends the infinite loop when after the last song is played
            stop = True 
        
    print(" ")
    print("------------------------------------------")
    print(" ")
    print("-------------End of Song List-------------")
    
if __name__ == "__main__":
    main()

#---------------------------End of Main-------------------------------------



#---------------------------End of Program----------------------------------
    
# add support for type 0 and type 2 MIDI files
# add error checking for control and program change? What if multiple channels?
# GPIO / multiplexing / board Adan bought?
# make sure it contains piano data then isolate that data;
# make sure our piano is capable of playing all of the notes in the file;
# have it where you can plug in USB and pull all MIDI files to project folder (no duplicates)
# need to show how time is calculated using time_signature values

