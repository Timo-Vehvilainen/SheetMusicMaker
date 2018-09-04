#!/usr/bin/env python2

'''
@author: Timo Vehvilainen
'''

from parse import Parse
from staff import Staff
from corruptedFileError import CorruptedFileError
import sys
import StringIO

'''
                    -THE MAIN FUNCTION-
        This is the function meant to be called by an actual user. 
        
        It can be called with a single argument, which is a name of a .txt file in 
        the same folder as main.py. The sheet music information in that file
        is then loaded, and can be further modified in the interactive mode.
        
        If no file is specified, it defaults to using a 4-bar (4/4) empty staff, 
        specified in empty.txt.
'''

def main(argv = []):
    #If there are no arguments, use empty.txt
    if len(sys.argv) <= 1:
        sheet = open('data/empty.txt', 'r')
    else:
        #Else, try opening the file and using it. If failed, use empty.txt
        try:
            sheet = open(sys.argv[1], 'r')
            parse = Parse(sheet)
        except:
            print("Corrupted file error. Starting from an empty file.")
            sheet = open('data/empty.txt', 'r')
            parse = Parse(sheet)
    
    selection = 0
    
    #List the different choices for the user
    while selection != 6:
        print("What would you like to do with the sheet music?\n")
        print("1. Modify a note")
        print("2. Add a harmony note")
        print("3. Edit song info")
        print("4. Modify lyrics")
        print("5. Save to file")
        print("6. Exit Sheet Music Maker\n")
        
        #Print the staff in its current condition
        parse.printStaff()
        
        try:
            selection = int(raw_input("\nSelection: "))
            
            #This clause is for modifying existing notes, or harmonizing them
            if selection == 1 or selection == 2:
                if selection == 1:
                    print("Please select a note to modify...")
                else:
                    print("Please select a note to harmonize...")
                
                #Select the bar from which to pick a note
                barNo = -1
                maxBars = len(parse.staff.notes)
                while barNo not in range(1, maxBars + 1):
                    print("Enter the bar of the note [1 - %d]:\n" % maxBars)
                    barNo = int(raw_input())
                
                #Select a note from that specified bar
                maxNotes = len(parse.staff.notes[barNo-1])
                if maxNotes > 1:
                    noteNo = -1
                    while noteNo not in range(1, maxNotes + 1):
                        print("Enter the number of the note in the bar [1 - %d]:\n" % maxNotes)
                        noteNo = int(raw_input())
                else:
                    noteNo = 1
                
                #Enter a pitch for the note or harmony
                if selection == 1:
                    pitch = raw_input("Enter the new pitch of the note [cb1 - g#2] or 'rest':\n")
                else:
                    pitch = raw_input("Enter the new pitch of the note [cb1 - g#2]")

                #If harmonizing, the duration must be the same as the note to be harmonized
                #Otherwise, specify the new duration
                if selection == 1:
                    duration = raw_input("Enter the new duration of the note (1/16 - 3/2):\n")
                    parse.modifyNote(barNo, noteNo, pitch, duration)
                else:
                    parse.addHarmony(barNo, noteNo, pitch)
            
            #This clause is for editing the title, author, lenght and time signature
            elif selection == 3:
                title = raw_input("Please enter the song title:\n")
                author = raw_input("Please enter the song author:\n")
                length = int(raw_input("Please enter the number of bars in the song:\n"))
                time = raw_input("Please enter the time signature of the song:\n")
                
                parse.editInfo(title, author, time, length)
                
            #Adding Lyrics
            elif selection == 4:
                lyrics = raw_input("Please enter the lyrics on a single line (syllables separated by '-', words by a space\n")
                
                buf = StringIO.StringIO(lyrics)
                parse.handleLyrics(buf)
                buf.close()
            
            #Saving the sheet music into a file
            elif selection == 5:
                f = open("data/SheetMusicMaker_Output.txt", "w")
                parse.printStaff(f)
                f.close()
                print("Sheet music written to data/SheetMusicMaker_Output.txt\n")
                
            #If an invalid selection was made, raise and error to go to the except-clause
            elif selection != 6:
                raise IOError
                
        except:
            #Display what kind of error was raised
            print("Invalid input:", sys.exc_info()[0])
            print("Try again.")
            selection = 0
    
    #Exit the program on choice No. 6
    print("Exiting the program.")
    sheet.close()
    
main()