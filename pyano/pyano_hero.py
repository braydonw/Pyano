import time
from pynput import keyboard #reads keyboard inputs
import os  # used for finding .mid files in the project folder
import glob  # ^
import mido  # used to create, edit, or read .mid files
from IOPi import IOPi #Library for IOPI Plus expansion board
#----------------------------------------------------
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
								 #hardware control pin isnt actually necessary but I'm keeping
								 #it for consistency and future proofing
#----------------------------------------------------
#Initialize all outputs to 0
bus1.write_port(0, 0x00)
bus1.write_port(1, 0x00)
bus2.write_port(0, 0x00)
bus2.write_port(1, 0x00)
#----------------------------------------------------
#global variables
key_pressed = None
score = 0
#----------------------------------------------------
#runs when a key is pressed
def on_press(key):
	global key_pressed
	
    try:
        note_on_live(key.char)
		key_pressed = key.char
    except AttributeError:
        pass
    return
#----------------------------------------------------
#runs when a key is released
def on_release(key):
    try:
        note_off_live(key.char)
    except AttributeError:
        pass
#----------------------------------------------------
#turns on solenoids live
def note_on_live(key):
    if key == 'q':
        bus1.write_pin(1, 1)
    elif key == '2':
        bus1.write_pin(2, 1)
    elif key == 'w':
        bus1.write_pin(3, 1)
    elif key == '3':
        bus1.write_pin(4, 1)
    elif key == 'e':
        bus1.write_pin(5, 1)
    elif key == 'r':
        bus1.write_pin(6, 1)
    elif key == '5':
        bus1.write_pin(7, 1)
    elif key == 't':
        bus1.write_pin(8, 1)
    elif key == '6':
        bus1.write_pin(9, 1)
    elif key == 'y':
        bus1.write_pin(10, 1)
    elif key == '7':
        bus1.write_pin(11, 1)
    elif key == 'u':
        bus1.write_pin(12, 1)
    elif key == 'z':
        bus1.write_pin(13, 1)
    elif key == 's':
        bus1.write_pin(14, 1)
    elif key == 'x':
        bus1.write_pin(15, 1)
    elif key == 'd':
        bus1.write_pin(16, 1)
    elif key == 'c':
        bus2.write_pin(1, 1)
    elif key == 'v':
        bus2.write_pin(2, 1)
    elif key == 'g':
        bus2.write_pin(3, 1)
    elif key == 'b':
        bus2.write_pin(4, 1)
    elif key == 'h':
        bus2.write_pin(5, 1)
    elif key == 'n':
        bus2.write_pin(6, 1)
    elif key == 'j':
        bus2.write_pin(7, 1)
    elif key == 'm':
        bus2.write_pin(8, 1)
		
	return
#----------------------------------------------------
#turns off solenoids live
def note_off_live(key):
    if key == 'q':
        bus1.write_pin(1, 0)
    elif key == '2':
        bus1.write_pin(2, 0)
    elif key == 'w':
        bus1.write_pin(3, 0)
    elif key == '3':
        bus1.write_pin(4, 0)
    elif key == 'e':
        bus1.write_pin(5, 0)
    elif key == 'r':
        bus1.write_pin(6, 0)
    elif key == '5':
        bus1.write_pin(7, 0)
    elif key == 't':
        bus1.write_pin(8, 0)
    elif key == '6':
        bus1.write_pin(9, 0)
    elif key == 'y':
        bus1.write_pin(10, 0)
    elif key == '7':
        bus1.write_pin(11, 0)
    elif key == 'u':
        bus1.write_pin(12, 0)
    elif key == 'z':
        bus1.write_pin(13, 0)
    elif key == 's':
        bus1.write_pin(14, 0)
    elif key == 'x':
        bus1.write_pin(15, 0)
    elif key == 'd':
        bus1.write_pin(16, 0)
    elif key == 'c':
        bus2.write_pin(1, 0)
    elif key == 'v':
        bus2.write_pin(2, 0)
    elif key == 'g':
        bus2.write_pin(3, 0)
    elif key == 'b':
        bus2.write_pin(4, 0)
    elif key == 'h':
        bus2.write_pin(5, 0)
    elif key == 'n':
        bus2.write_pin(6, 0)
    elif key == 'j':
        bus2.write_pin(7, 0)
    elif key == 'm':
        bus2.write_pin(8, 0)
		
	return
#----------------------------------------------------
#play the MIDI file
def play_file(mid):
    
    # get the type of MIDI file
    # type 0 (single track): all messages are saved in one track
    # type 1 (synchronous): all tracks start at the same time
    # type 2 (asynchronous): each track is independent of the others
    if mid.type == 0:
        print ("MIDI Type: 0 (currently unsupported)")
        return
    if mid.type == 1:
        print ("MIDI Type: 1")
    elif mid.type == 2:
        print ("MIDI Type: 2 (currently unsupported)")
        return
    else:
        print ("MIDI Type Error")
        return
	
	# build set of all unique notes & find min and max for octave adjusting
    notes = set()

    # retrieve important information from the MIDI File
    for msg in mid:
		msg_data = str(msg)  # important
		
		#get the tempo of the song
		if msg.is_meta:
			if msg.type == 'set_tempo':
				print("SET TEMPO:")
				temp1 = msg_data.find('tempo=')
				temp2 = msg_data.find('time=')
				set_tempo = msg_data[temp1 + 6:temp2]
				print(set_tempo)
				
		#make a list of every unique note in the song
        if not msg.is_meta:
            if msg.type != 'program_change' and msg.type != 'control_change':
                # if we made it this far then the message must be note_on/off type
                octave_adjust(msg, notes)

    #skip this midi file if it does not have off commands
    if off_check == False:
        print()
        print("----------------------------------------------------")
        print()
        print("This file cannot be played becuase it does not contain 'off' commands")
        print()
        print("----------------------------------------------------")
        return
    
    
    # testing note range of each MIDI file
    min_value = min([int(i) for i in notes]) #the min and max values are strings from the MIDI file and need to be converted to ints
    max_value = max([int(i) for i in notes])
    range_notes = max_value - min_value
	
	#set the adjust value based on the range of the song
	if range_notes <= 25: 
		adjust_value = min_value - 1 #adjust the lowest note in the song to the first note on the piano
	else:
		adjust_value = 59 #adjust to play middle C plus 2 octaves on the piano        
    
    #play the song/have the user play the song       
    for msg in mid:
		#no music control for now
		#maybe pause and stop later
		
        #play next message after checking music control
        if not msg.is_meta:
            if msg.type != 'program_change' and msg.type != 'control_change':
                time.sleep(msg.time) # MUST GO BERFORE PLAY_NOTE FUNCTION
                play_note(msg, notes, adjust_value)
    
    print("---------------End of Song-------------------")
	return
#----------------------------------------------------
def octave_adjust(msg, notes):
	global off_check
	
	#get the note number and its status
    msg_data = str(msg)
    temp1 = msg_data.find('note_')
    temp2 = msg_data.find('channel')
    status = msg_data[temp1 + 5:temp2]  # status = on or off
    temp1 = msg_data.find('note=')
    temp2 = msg_data.find('velocity=')
    note = msg_data[temp1 + 5:temp2]  # note represented as MIDI #
    notes.add(note)  # testing note range of each MIDI file
    
    #check if the midi file has off commands
    if status == 'off ':
        off_check = True
        
    return
#----------------------------------------------------
def play_note(msg, notes, adjust_value):
    msg_data = str(msg)
    temp1 = msg_data.find('note_')
    temp2 = msg_data.find('channel')
    status = msg_data[temp1 + 5:temp2]  # status = on or off (redundant: just use msg.type == 'note_on')
    temp1 = msg_data.find('note=')
    temp2 = msg_data.find('velocity=')
    note = msg_data[temp1 + 5:temp2]  # note represented as MIDI #
	
	#adjust each note
    note = int(note) - adjust_value
	
	#if the note is in the second octave, have the user play the note
	if note >= 12 and note <= 24:
		user_play_note(note)
	else: 
		#play the note on the piano
		if status == 'on ':
			note_on(note)
		elif status == 'off ':
			note_off(note)
			
	return
#----------------------------------------------------
#used to take inputs from the user
def user_play_note(note):
	global key_pressed
	miss_count = 0
	
	note_key = note2key(note)
	#check once before entering the loop
	if key_pressed == note_key: #a perfect score would actually require the user to hit the note before this point
		scoring(miss_count) #passing a 0 would be the highet possible score
		return
	#enter a loop that checks for the correct note every 100 milliseconds
	else
		miss_count += 1
		time.sleep(.1)
		while key_pressed != note_key:
			#end the loop after 20 misses
			if miss_count == 20:
				break
			miss_count += 1
			time.sleep(.1)
		scoring(miss_count)
	return
#----------------------------------------------------
#uses the miss count to get a score for each note and adds it to the total score
def scoring(miss_count):
	global score
	
	score += (20 - miss_count)
	
	return
#----------------------------------------------------
#turns on solenoids
def note_on(note):
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
		
	return
#----------------------------------------------------
#turns off solenoids
def note_off(note):
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
		
	return
#----------------------------------------------------
def note2key(note):
	if note == 12:
		note_key = 'z'
	elif note == 13:
		note_key = 's'
	elif note == 14:
		note_key = 'x'
	elif note == 15:
		note_key = 'd'
	elif note == 16:
		note_key = 'c'
	elif note == 17:
		note_key = 'v'
	elif note == 18:
		note_key = 'g'
	elif note == 19:
		note_key = 'b'
	elif note == 20:
		note_key = 'h'
	elif note == 21:
		note_key = 'n'
	elif note == 22:
		note_key = 'j'
	elif note == 23:
		note_key = 'm'
	elif note == 24:
		note_key = ','
	
	return note_key
#----------------------------------------------------
def clear_pins():
	#clear outputs
	bus1.write_port(0, 0x00)
	bus1.write_port(1, 0x00)
	bus2.write_port(0, 0x00)
	bus2.write_port(1, 0x00)
	return
#----------------------------------------------------
def main():
    
	#find MIDI files to use in Pyano Hero
	#probably will just use one MIDI file but I copy pasted this code
	midi_file_list = []
    os.chdir("/home/pi/pyano-git/pyano_hero_songs")
    for midi_file in glob.glob("*.mid"):
        midi_file_list.append(midi_file)
		
    #start the keyboard listener thread
    listener = keyboard.Listener(
        on_press=on_press,
		on_release=on_release)
    listener.start()
    
	#run through the MIDI files
	#may add pause and stop functionality later. back and skip unnecessary
	for midi_file in midi_file_list:
		mid = mido.MidiFile(midi_file)  # mid is the current mido MIDI file playing
        play_file(mid)
        print()
		print('Final Score: ', score)
		
		#reset variables and clear outputs
		clear_pins()
		key_pressed = None
		score = 0
	
    #end the listener thread
    listener.stop()
	
	#clear outputs again just in case
	bus1.write_port(0, 0x00)
	bus1.write_port(1, 0x00)
	bus2.write_port(0, 0x00)
	bus2.write_port(1, 0x00)	
#----------------------------------------------------
if __name__ == "__main__":
    main()