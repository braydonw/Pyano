import glob, os, shutil

def main():
    '''
    copies all MIDI files on all USB drives to project folder
    filenames that already exist are still copied & updated
    '''
    
    # ADD TRY/EXCEPT FOR PYANO VS PYANO-GIT FOLDER NAMES, ETC.
    
    dest_dir = "/home/pi/Auto USB Transfer"
    usb_list = os.listdir("/media/pi")
    usb_list.remove("SETTINGS")
    if not usb_list:
        print("There are no USB drives inserted.")
    else:
        for drive in usb_list:
            source_dir = ("/media/pi/%s" %drive)
            files = glob.iglob(os.path.join(source_dir, "*.mid"))
            for f in files:
                if os.path.isfile(f):
                    shutil.copy2(f, dest_dir) # copy2 saves metadata
                    print("Added {}".format(f))

if __name__ == "__main__":
    main()
