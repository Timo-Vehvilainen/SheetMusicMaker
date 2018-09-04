'''
@author: Timo Vehvilainen
'''

class Note(object):
    '''
    The Note object represents one note or rest on the staff
    '''
    
    '''
                                -Initializer-
        PARAMETERS:
            - note pitch (an integer from 0 to 11), which correspond to different
                notes (lower integers mean higher pitches. g2 = 0, f2 = 1.... c1 = 11)
            - note duration (a positive number). A number of 1 means a whole note,
                0.5 means a half note etc.
            - note harmony (an integer between 0 and 11). Numbers above 0 imply a
                harmonized note that plays at the same time as the lowest note.
            - note shift (-1, 0 or 1). Implies if a note is flat of sharp.
    '''
    def __init__(self, pitch, duration, harmony = 0, shift = 0):
        self.pitch = pitch
        self.duration = duration
        self.harmony = harmony
        self.shift = shift
    
    '''
    GET- and SET- functions
    '''
        
    def getPitch(self):
        return self.pitch
    
    def setPitch(self, pitchNo):
        self.pitch = pitchNo
    
    def getDuration(self):
        return self.duration
    
    def setDuration(self, duration):
        self.duration = duration
    
    def getHarmony(self):
        return self.harmony
    
    def  setHarmony(self, harmony):
        self.harmony = harmony
    
    def getShift(self):
        return self.shift
    
    def setShift(self, shift):
        self.shift = shift
    