'''
@author: Timo Vehvilainen
'''
from __future__ import division
from staff import Staff
from note import Note 
from corruptedFileError import CorruptedFileError
import sys

class Parse(object):
    '''
    The Parse class is used to handle the input given by the user.
    '''
    
    '''
                                -Initializer-
    
    PARAMETERS:
        -the input stream
    '''
    def __init__(self, input):
        
        #If no name, author, bar amount or time signature are provided in the file,
        # they are defaulted to "None", "None", 4 and 4/4. 
        self.staff = Staff("None", "None", 4, 4/4)
        
        try:
            line = self.getNextLine(input)
            
            if line.strip() != "#SHEETMUSIC":
                raise CorruptedFileError("Unknown data file (missing header)")
            
            line = self.getNextLine(input)
            while line != "" and line != "#END":
                line = line.strip().upper()
                if line == "#SONG INFO":
                    line = self.handleInfo(input)
                if line == "#TIME":
                    line = self.handleTime(input)
                if line  == "#NOTES":
                    line = self.handleNotes(input)
                if line == "#LYRICS":
                    line = self.handleLyrics(input)
                line = self.getNextLine(input)
            
        #If the file is faulty in some way, raise an error
        except CorruptedFileError as e:
            print("Corrupted file error:", e)
                   
    '''
                            -handleInfo-
            This function handles the parsing of the song name and author.
            
            PARAMETERS:
                - the input stream
            
            RETURNS:
            - the next line in the stream after the #SONG INFO section has been handled
    '''
    def handleInfo(self, input):
        line = self.getNextLine(input)
        while (line != "") and (not line.startswith("#")):
            
            if line.lower().startswith("author"):
                author = line.split(":")[1].strip()
                self.staff.setAuthor(author)
            
            elif line.lower().startswith("title"):
                title = line.split(":")[1].strip()
                self.staff.setTitle(title)
            
            line = self.getNextLine(input)
        return line
    
    '''
                            -handleTime-
            This function handles number of bars (initially) and the time
            signature. 
            
            The time signature is stored as a floating point number, 
            indicating how many whole notes fit into one bar. So for example, a
            time signature of 1 = "4/4", and 0.75 = "3/4".
            
            PARAMETERS:
                - the input stream
            
            RETURNS:
            - the next line in the stream after the #TIME section has been handled
    '''
    def handleTime(self, input):          
        line = self.getNextLine(input)
        while line != "" and (not line.startswith("#")):
            
            if line.startswith("signature"): 
                given_sig = line.split(":")[1].strip()
                try:
                    given_sig = self.convertTime(given_sig)
                except:
                    raise CorruptedFileError("Invalid Time signature")
                self.staff.setTime(given_sig)
            
            elif line.startswith("bars"):
                try:
                    bars = int(line.split(":")[1].strip())
                except ValueError:
                    raise CorruptedFileError("Invalid bar number")
                self.staff.setLength(bars)
            
            line = self.getNextLine(input)
        return line
    
    '''
                            -handleNotes-
        This function is used to parse the note information in the stream.
        
        It converts the note names (such as 'g1' or 'eb2') to numeric information
        and feeds it to the staff object. 
        The highest note possible is 'g#2' (numeric value 0 and shift +1) and 
        the lowest note possible is 'cb1' (numeric value 11 and shift -1). 
        Any notes that have pitches other than are in this range of letters 
        are treated as rests.
        
        If the octave is not provided, it defaults to 1.
        
        The duration of the notes is also parsed, as a floating point number, 
        where a whole note has duration 1. 
        The longest duration possible is 3/2, and 
        the shortest duration possible is 1/16. 
        
        PARAMETERS:
            - the input stream
            
        RETURNS:
            - the next line in the stream after the #NOTES section has been handled
    '''
    
    def handleNotes(self, input):
        line = self.getNextLine(input)
        
        #a temporary array to hold all the notes
        notes = []
        
        #if no duration is specified, it defaults to 1/4
        duration = 1/4
        
        while line != "" and (not line.startswith("#")):
            #Handle the pitch
            if line.lower().startswith("pitch"):
                pitch = line.split(":")[1].strip().lower()
                
                #Handle sharp and flat notes
                shift = self.convertShift(pitch)
                
                #Convert the pitch name to a numeric value
                pitch_number = self.convertPitch(pitch)
                
                notes.append(Note(pitch_number, 1/4, 0, shift))
                
            #Handle the duration
            elif line.lower().startswith("duration"):
                duration = self.convertTime((line.split(":")[1].strip()))
                notes[-1].setDuration(duration)
            
            #Handle the harmony
            elif line.lower().startswith("harmony"):
                harmony_pitch = line.split(":")[1].strip().lower()
                
                #Handle sharp and flat notes
                harmony_shift = self.convertShift(harmony_pitch)
                
                #Convert the pitch name to a numeric value
                harmony_pitch_number = self.convertPitch(harmony_pitch)
                notes[-1].setHarmony(Note(harmony_pitch_number, duration, 0, harmony_shift))
                
            line = self.getNextLine(input)
            
        for note in notes:
            self.staff.addNote(note)
        return line
    
    '''
                            -handleLyrics-
            This function simply reads in a line of lyrics, separating
            them into words and further into syllables, and passing them
            to the staff as a 2D-array
            
            PARAMETERS:
                -the input stream
                
            RETURNS:
                - the next line in the stream after the #LYRICS section has been handled
    '''
    
    def handleLyrics(self, input):
        line = self.getNextLine(input)
        words = []
        
        while line != "" and (not line.startswith("#")):
            new_line = line.split(" ")
            for word in new_line:
                words.append(word)
            line = self.getNextLine(input)
        
        word_amount = len(words)
        for i in range(word_amount):
            syllables = words[0].split("-")
            words.append(syllables)
            words.pop(0)
        self.staff.setLyrics(words)
        
        return line
    
    '''
                            -modifyNote-
        This function is used to modify a single selected note in the console
        interface.
        
        PARAMETERS:
            -The ordinal number of the bar (positive integer)
            -The ordinal number of the note within the bar (positive integer)
            -The pitch of the note in the format "f1" or "c#2" for example (a string)
            -The duration of the in the format "1/4" or "0.25" for example (a string)
    '''
    def modifyNote(self, barNo, noteNo, pitch, duration):
        bar = self.staff.notes[barNo-1]
        note = bar[noteNo-1]
        
        shiftNo = self.convertShift(pitch)
        pitchNo = self.convertPitch(pitch)
        durationNo = self.convertTime(duration)
        
        note.setPitch(pitchNo)
        note.setShift(shiftNo)
        note.setDuration(durationNo)
        
        self.staff.straightenStaff()
        
        '''
                                -addHarmony
            This function is used to add harmony to a note
            
            PARAMETERS:
                -the ordinal number of the bar of the note (positive integer)
                -the ordinal number of the note in the bar (positive integer)
                -the pitch of the harmony (string)
        '''
        
    def addHarmony(self, barNo, noteNo,  pitch):
        bar = self.staff.notes[barNo-1]
        note = bar[noteNo-1]

        pitchNo = self.convertPitch(pitch) 
        shift = self.convertShift(pitch) 
        note.setHarmony(Note(pitchNo, note.getDuration(), 0, shift))
    '''
                            -editInfo-
        This function is used to edit the info of the song in the console interface.
        
        PARAMETERS:
            - The title of the song (a string)
            - The author of the song (a string)
            - the time signature of the song ("0.5", "2/4" etc.) (a string)
            - the length of the song in bars (a positive integer)
    '''
    def editInfo(self, title, author, time, length):
        time_sig = self.convertTime(time)
        
        self.staff.setTitle(title)
        self.staff.setAuthor(author)
        self.staff.setLength(length)
        self.staff.setTime(time_sig)
        
        self.staff.straightenStaff()
        
        
    '''
                            -printStaff-
        This function is meant to be called for printing the staff in its current
        state. It merely advances the call to staff.py
    '''

    def printStaff(self, out = sys.stdout):
        self.staff.printStaff(out)
        
        '''
                            -getNextLine-
        This helper function is used to extract the next non-whitespace 
        line from the input stream. 
        It is then stripped of excess whitespace for ease of handling.
            
        PARAMETERS:
            -the input stream
            
        RETURNS:
            -the next line in the input that has some content in it, stripped.
        '''

    def getNextLine(self, input):
        line = " "
        while line.isspace():
            line = input.readline()
        line = line.strip()
        return line
    
    '''
                            -convertTime-
        This helper function is used by handleTime() to read in the time signature
        either as a floating point number, or a quotient of two numbers.
        
        PARAMETERS:
            -The time signature as a string (either a quotient of the form "X/Y",
                or a floating point number)
        
        RETURNS:
            -The time signature as a floating point number, indicating how many
                 whole notes fit in one bar.
    '''
    
    def convertTime(self, time):
        try:
            return float(time)
        except ValueError:
            num, denom = time.split('/')
            return (float(num) / float(denom))
        
    '''
                            -convertPitch-
        This helper function is used to convert pitch names to a numeric value, where
        g2 = 0, f2 = 1, e2 = 2 ..., d1 = 10 and c1 = 11. Any sharps or flats are ignored, 
        as they are handled separately by convertShift().
        
        PARAMETERS:
            -The pitch in string format. For example "c2" or "gb"
        
        RETURNS:
            -The numeric value of the pitch, as specified above
    '''
        
    def convertPitch(self, pitch):
        #Handle different octaves
        if pitch[-1].isdigit():
            octave = int(pitch[-1])
        else:
            octave = 1
        
        #Change the pitch letter to a numeric value
        pitch_number = (ord(pitch[0]) - ord('g')) * (-1)
        if pitch_number > 4:
            octave += 1
        pitch_number += 7 * (2-octave)
        
        if pitch_number < 0 or pitch_number > 11:
            pitch_number = 20
        
        return pitch_number
    
    '''
                            -convertShift-
        This helper function handles the shifts of sharp and flat notes
        
        PARAMETERS:
            -The pitch in string format. For example "c#2" or "gb"
        
        RETURNS:
            -The numeric value of the shift. (1 for sharp, -1 for flat, 0 otherwise)
    '''
    
    def convertShift(self, pitch):
        #Handle sharp and flat notes
        shift = 0
        if len(pitch) >= 2:
            if pitch[1] == "#":
                shift = 1
            elif pitch[1] == "b":
                shift = -1
        
        return shift
        