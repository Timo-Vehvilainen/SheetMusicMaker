'''
@author: Timo Vehvilainen
'''

from __future__ import division
from __future__ import print_function
from note import Note 
from corruptedFileError import CorruptedFileError
import sys


class Staff(object):
    '''
    The Staff object represents the staff on which different notes, rests and lyrics
    are placed
    '''

    '''
                            -Initializer-
        PARAMETERS:
            -title of the song (a string)
            -author of the song (a string)
            -the lenght of the song in bars (a positive integer)
            -the time signature of the song (a floating point number)
            -the lyrics of the song in a 2D-array (words on rows, syllables on columns)
    '''

    def __init__(self, title, author, lengthInBars, time_sig, lyrics = [[]]):
        
        self.title = title
        self.author = author        
        self.time = time_sig
        self.length = lengthInBars
        self.lyrics = lyrics
        
        #The notes are stored in an 2D-array where each small array
        #represents a single bar
        self.notes = []
        for bar in range(self.length):
            self.notes.append([])
    
    '''
        SET-FUNCTIONS
    '''
            
    def setAuthor(self, author):
        self.author = author
    
    def setTitle(self, title):
        self.title = title
        
    def setLength(self, length):
        #The setLength()-function adds empty bars or removes bars from the end of
        # the staff, depending on the situation
        self.length = length
        while len(self.notes) > length:
            self.notes.pop()
        while len(self.notes) < length:
            self.notes.append([])
    
    def setTime(self, time):
        self.time = time
    
    def setLyrics(self, lyrics):
        self.lyrics = lyrics
    
    '''
                                -addNote-
        This function is used to add a new note the end first bar that isn't full.
        It is used for adding notes in sequence from a file.
        
        PARAMETERS:
            -The Note-object to be added 
    '''
    def addNote(self, noteNew):
        barNo = 0
        while barNo < self.length and (self.addDurations(self.notes[barNo])) >= self.time:
            barNo += 1
        if barNo == self.length:
            self.setLength(self.length + 1)
        self.notes[barNo].append(noteNew)
        self.straightenStaff()
        
    '''
                                -addDurations-
        This helper function adds together all the durations of the notes
        in a single bar.
        
        PARAMETERS:
            -The bar (array of Note objects) to be summed up
            
        RETURNS:
            -The summed duration of all the notes in the bar
    '''
    
    def addDurations(self, bar):
        duration = 0
        for note in bar:
            duration += note.getDuration()
        return duration
    
    '''
                            -straightenStaff-
        This helper function is used to deal with notes that are too long for the
        bar to hold, and part of it is moved into the next bar. This procedure is
        done to all bars, and extra bars are added if needed.
        
    '''
    
    def straightenStaff(self):
        # Overly full bars are handled as such:
        #1. split the first note that crosses the set bar length into 2 parts
        #2. insert all the extra notes from the overly filled bar into a temporary
        #    array
        #3. move all the extra notes from the temporary array to the beginning
        #    of the next bar.
        #4. Repeat this procedure for the next bar, creating new bars if necessary
        
        for barNo, bar in enumerate(self.notes):
            
            added_durations = 0
            for i, note in enumerate(bar):
                added_durations += note.getDuration()
                
                if added_durations > self.time:
                    difference = added_durations - self.time
                    if difference < note.getDuration():  
                        
                        #Set the first half of the split not to the appropriate length
                        note.setDuration(note.getDuration() - difference)
                        if note.harmony != 0:
                            note.getHarmony().setDuration(note.getDuration() - difference)
                        
                        #Create a new note, that has the rest of the split note
                        new_note = Note(note.getPitch(), difference, note.getHarmony(), note.getShift())
                        
                        #See if the split note was the last note of the bar or not,
                        #and use the proper function for adding the latter half
                        if i == (len(bar) - 1):
                            bar.append(new_note)
                        else:
                            bar.insert(i+1, new_note)
                            
                    #Move the extra notes into a temporary array
                    extra_notes = []
                    while self.addDurations(bar) > self.time:
                        extra_notes.insert(0, bar.pop())
                        
                    #See if a new bar needs to be added
                    if barNo == (self.length - 1):
                        self.setLength(self.length + 1)
                    
                    #Insert the extra notes to the beginning of the next bar
                    while len(extra_notes) > 0:
                        self.notes[barNo+1].insert(0, extra_notes.pop())
                        
    '''
                                -printStaff-
        The main function used to print out the current condition of the staff
        
        PARAMETERS:
            -an output stream (defaults to sys.stdout)
    '''
    def printStaff(self, out = sys.stdout):
        print ("Title:", self.title)
        print ("Author:", self.author)
        print ("Time Signature (amount of whole notes in a bar):", self.time)
        print ("Length in bars:", self.length, "\n")
        
        self.reduceRests()
        
        matrix = self.initializeMatrix()
        matrix = self.insertNotes(matrix)
        
        #So that the program isn't too sensitive to the existence of the file containing
        #the G-cleff, its non-existence is ignored by this try-except clause
        try:
            g_cleff = open("data/G-cleff.txt", "r")
            for i in range(len(matrix)):
                line = g_cleff.readline()[:-1]
                out.write(line)
                for j in matrix[i]:
                    out.write(j)
                out.write("\n")
            g_cleff.close()
            g_cleff = True
        except IOError:
            g_cleff = False
            for i in range(len(matrix)):
                for j in matrix[i]:
                    out.write(j)
                out.write("\n")
        
        #Add lyrics separately
        big_string = self.addLyrics(g_cleff)
            
        #Finally, write the string containing the lyrics
        if big_string != "":
            out.write(big_string)
    
    '''
                            -addLyrics-
        This is used for adding lyrics to the sheet music
        
        PARAMETERS:
            -a True or False value,, indicating whether the cleff was successfully
            printed or not
        
        RETURNS:
            -The spaced out lyrics in a single string
    '''
            
    def addLyrics(self, g_cleff):
        big_string = ""
        #Construction of the lyrics in one big string, with syllables under each note
        if len(self.lyrics[0]) != 0:
            #Depending if the G-cleff was printed or not, offset the beginning of
            #the lyrics by 11 spaces
            if g_cleff == True:
                big_string += "           "
            syllable_count = 0
            word_count = 0
            for barNo, bar in enumerate(self.notes):
                #5 spaces for each bar line
                big_string += "    "
                for i, note in enumerate(bar): 
                    if note.getPitch() in range(12):
                        #Add the next syllable to the string
                        big_string += self.lyrics[word_count][syllable_count]
                        #If it is not the last syllable of the word, add a hyphen
                        if syllable_count < (len(self.lyrics[word_count]) - 1):
                            big_string += "-"
                        #Add spaces so that the distance to the next note is 5 spaces
                        for j in range(5 - len(self.lyrics[word_count][syllable_count]) - 1):
                            big_string += " "
                        syllable_count += 1
                        #If it was the last syllable of the word, go to the next word, 
                        #and add an extra space instead of a hyphen
                        if syllable_count == len(self.lyrics[word_count]):
                            big_string += " "
                            word_count += 1
                            syllable_count = 0
                        #End once we have printed the last word
                        if word_count == len(self.lyrics):
                            break
                    else:
                        #If the note is a rest, just add 5 spaces
                        big_string += "     "
                #Break from the upper loop aswell, when we are finished
                if word_count == len(self.lyrics):
                            break
                big_string += " "
        return big_string
        
    '''
                                -initializeMatrix-
        This helper function creates a 2D-array (essentially a matrix)
        of characters which, when printed out in sequence, produce the 
        graphical representation of an empty staff (with no notes or rests).
        
        RETURNS:
            -the initialized character matrix
    '''
    def initializeMatrix(self):
        matrix = []
        self.fillRests()
        #5 columns are needed for each note and bar line.
        note_bar_amount = self.countNotesAndBars()
        
        for row in range(13):
            matrix.append([])
            for column in range(note_bar_amount * 5 + 1):
                if (row % 2 != 0 and row <= 9):
                    matrix[row].append("-")
                else:
                    matrix[row].append(" ")
        return matrix
    
    '''
                            -countNotesAndBars-
           This is used by InitializeMatrix() for counting enough space
           for every note and barline.    
           
           RETURNS:
               -an integer adding all the notes and bars together
    '''
    
    def countNotesAndBars(self):
        counter = 0
        for bar in self.notes:
            for note in bar:
                counter += 1
            counter += 1
        return counter
    
    '''
                                -insertNotes-
        This function is used by printStaff() to enter all the notes, rests
        and bar lines to the staff.
        
        PARAMETERS:
            -the character matrix as initialized by initializeMatrix()
            
        RETURNS:
            -the same matrix after the notes, rests, and bar lines have been added
    '''
    
    def insertNotes(self, matrix):
        column = 0
        
        #Insert the first bar line at the very beginning of the staff
        for j in range(len(matrix)):
                if j > 0 and j < 10:
                    matrix[j][column] = "|"
        
        
        for barNo, bar in enumerate(self.notes):
            for i, note in enumerate(bar):
                
                #The row of the matrix for each note is determined by the pitch,
                #and 5 columns are reserved for each note
                row = note.getPitch()
                column += 5
                
                #if the pitch (or row) is not one of the accepted values, it is
                #determined to be a rest.
                if row == 20:
                    self.insertRest(matrix, column, note)
                    continue
                
                #Depending on the duration of the note, the head, the stem and 
                #possibly the flag of the note might differ, so they are handled
                #separately.
                self.insertHead(matrix, row, column, note)
                if note.getDuration() < 1:
                    if note.getPitch() < 5:
                        stem_direction = "down"
                    else:
                        stem_direction = "up"
                    self.insertStem(matrix, row, column, note, stem_direction)
                    if note.getDuration() < (1/4):
                        self.insertFlag(matrix, row, column, note, stem_direction)
                
                if note.harmony != 0:
                    self.insertHarmony(matrix, column, note)
                #If the note is sharp or flat, we insert the appropriate marking,
                #and place the same shift on all the other such notes in the same bar
                if note.getShift() != 0:
                    for other_note in bar:
                        if other_note.getPitch() == note.getPitch():
                            if other_note.getShift() == 0:
                                other_note.setShift(note.getShift)
                        harmony_note = other_note.getHarmony()
                        if other_note.getHarmony() != 0:
                            if harmony_note.getPitch() == note.getPitch():
                                if harmony_note.getShift() == 0:
                                    harmony_note.setShift(note.getShift)
                    self.insertShift(matrix, row, column, note)
            column += 5
            
            #After each bar, insert a vertical bar line
            for j in range(len(matrix)):
                if j > 0 and j < 10:
                    matrix[j][column] = "|"
                    
        return matrix
    
    '''
                            -insertHarmony-
        Inserts the harmony notes to the matrix to be printed
        
        PARAMETERS:
            - the character matrix as initialized by initilizeMatrix()
            - the column of the matrix that insertNotes() is currently going through
            - the Note object, the harmony of which to be added
    '''
    
    def insertHarmony(self, matrix, column, note):
        harmony_note = note.getHarmony()
        row = harmony_note.getPitch()
        if row == 20:
            return
        self.insertHead(matrix, row, column, harmony_note)
        if harmony_note.getDuration() < 1:
            if note.getPitch() < 5:
                if harmony_note.getPitch() < 9:
                    stem_direction = "down"
                else:
                    stem_direction = "up"
            else:
                if harmony_note.getPitch() > 2:
                    stem_direction = "up"
                else:
                    stem_direction = "down"
            self.insertStem(matrix, row, column, harmony_note, stem_direction)
            if note.getDuration() < (1/4):
                self.insertFlag(matrix, row, column, harmony_note, stem_direction)
        if harmony_note.getShift() != 0:
                    self.insertShift(matrix, row, column, harmony_note)
    
    '''
                                -fillRests-
        This function is used to fill unfilled bars with the appropriate rests.
    '''

    def fillRests(self):
        for bar in self.notes:
            if self.addDurations(bar) < self.time:
                
                #First the bar (note array) is just appended with a rest of the
                #exactly right length.
                difference = self.time - self.addDurations(bar)
                bar.append(Note(20, difference))
                
                #It is then modified into smaller notes that have writable 
                #durations. For example 7/4 = 3/2 + 1/4
                writable_notes = [1, 3/2, 3/4, 1/2, 3/8, 1/4, 1/8, 3/16, 1/16]
                while difference not in writable_notes:
                    for i in writable_notes:
                        if i < difference:
                            bar[-1].setDuration(i)
                            difference -= i
                            bar.append(Note(20, difference))
                            
    '''
                                -insertRest-
        This function is used by insertNotes() to enter a rest into the 
        character matrix
        
        PARAMETERS:
            - the character matrix as initialized by initilizeMatrix()
            - the column of the matrix that insertNotes() is currently going through
            - the Note object to be added
    '''
    
    def insertRest(self, matrix, column, note):
        
        #Whole rests and half rests are similar to each other in design, 
        #so they are printed using a shared method
        if note.getDuration() >= (1/2):
            
            #A whole rest is above the middle line
            if note.getDuration() >= 1:
                startrow = 6
            
            #A half rest is below the middle line
            else:
                startrow = 4
                
            for col in range(column-2, column+1):
                matrix[startrow][col] = "="
                matrix[5][col] = "|"
        
        #A quarter note is unique in design    
        elif note.getDuration() >= (1/4):
            matrix[4][column] = "/"
            matrix[5][column] = "\\"
            matrix[6][column] = "/"
            matrix[7][column] = "\\"
        
        #All the rest below a quarter have a similar design
        else:
            matrix[4][column-3] = "\\"
            matrix[4][column-2] = "_"
            matrix[4][column-1] = "_"
            matrix[4][column] = "/"
            matrix[5][column-1] = "/"
            matrix[6][column-2] = "/"
            
            #if the rest is even shorter than 1/8th, add an extra flag to the design 
            if note.getDuration() <= (1/16):
                matrix[5][column-2] = "_"
                matrix[5][column-3] = "_"
                matrix[5][column-4] = "\\"
        
        #if the rest is of a dotted length, add the dot
        if note.getDuration() in [3/16, 3/8, 3/4, 3/2]:
            matrix[4][column+1] = "."
            
    '''
                                -insertHead-
        This function is used by insertNotes() to insert the head of a note 
        on the character matrix
        
        PARAMETERS:
            - the character matrix as initialized by initilizeMatrix()
            - the row and column of the matrix that insertNotes() is currently going through
            - the Note object to be added
    '''
            
    def insertHead(self, matrix, row, column, note):
        if note.getDuration() >= (1/2):
            matrix[row][column-1] = "("
            matrix[row][column] = ")"
        else:
            matrix[row][column-1] = "@"
            matrix[row][column] = "@"
        if note.getPitch() == 11:
            matrix[row][column-2] = "-"
            matrix[row][column+1] = "-"
        if note.getDuration() in [3/16, 3/8, 3/4, 3/2]:
            matrix[row][column+1] = "."
            
    '''
                                -insertStem-
        This function is used by insertNotes() to insert the stem of a note 
        on the character matrix
        
        PARAMETERS:
            - the character matrix as initialized by initilizeMatrix()
            - the row and column of the matrix that insertNotes() is currently going through
            - the Note object to be added
    '''
    
    def insertStem(self, matrix, row, column, note, stem_direction):
        for i in range(1, 4):
            if stem_direction == "down":
                matrix[row+i][column-1] = "|"
            else:
                matrix[row-i][column] = "|"
    
    '''
                                -insertFlag-
        This function is used by insertNotes() to insert the flag of a note with
        length shorter than 1/4 on the character matrix
        
        PARAMETERS:
            - the character matrix as initialized by initilizeMatrix()
            - the row and column of the matrix that insertNotes() is currently going through
            - the Note object to be added
    '''
    
    def insertFlag(self, matrix, row, column, note, stem_direction):
        if stem_direction == "down":
            matrix[row+3][column-2] = "\\"
        else:
            matrix[row-3][column+1] = "\\"
        if note.getDuration() <= (1/16):
            if stem_direction == "down":
                matrix[row+2][column-2] = "\\"
            else:
                matrix[row-2][column+1] = "\\"
            
    '''
                                -insertShift-
        This function is used by insertNotes() to enter the marking for a 
        sharp or a flat note.
        
        PARAMETERS:
            - the character matrix as initialized by initilizeMatrix()
            - the row and column of the matrix that insertNotes() is currently going through
            - the Note object which contains the pitch shift
    '''
    def insertShift(self, matrix, row, column, note):
        if note.getShift() > 0:
            matrix[row][column-3] = "#"
        else:
            matrix[row][column-3] = "b"
            
    '''
                                -reduceRests-
        This function combines adjacent rests, and is used for clean-up before
        printing the staff.
    '''
    
    def reduceRests(self):
        for bar in self.notes:
            for i in range(len(bar) - 1):
                note  = bar[i]
                next_note = bar[i + 1]
                if note.getPitch() == 0 and next_note.getPitch() == 0:
                    combined_duration = note.getDuration() + next_note.getDuration()
                    if combined_duration <= 1:
                        note.setDuration(combined_duration)
                        bar.remove(next_note)
                
                