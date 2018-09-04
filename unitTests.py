'''
@author: Timo Vehvilainen
'''

import unittest
from parse import Parse
from staff import Staff
from note import Note
from corruptedFileError import CorruptedFileError


class Test(unittest.TestCase):

    def testEmpty(self):
        sheet = open('data/empty.txt', 'r')
        parse = Parse(sheet)
        parse.printStaff()
        sheet.close()

    def testSingleNote(self):
        sheet = open('data/single_note.txt', 'r')
        parse = Parse(sheet)
        parse.printStaff()
        sheet.close()
    
    def testMultipleNotes(self):
        sheet = open('data/multiple_notes.txt', 'r')
        parse = Parse(sheet)
        parse.printStaff()
        sheet.close()
        
    def testBarOverlap(self):
        sheet = open('data/bar_overlap.txt', 'r')
        parse = Parse(sheet)
        parse.printStaff()
        sheet.close()
    
    def testRests(self):
        sheet = open('data/rests.txt', 'r')
        parse = Parse(sheet)
        parse.printStaff()
        sheet.close()
    
    def testLyrics(self):
        sheet = open('data/lyrics.txt', 'r')
        parse = Parse(sheet)
        parse.printStaff()
        sheet.close()
    
    def testHarmony(self):
        sheet = open('data/harmony.txt', 'r')
        parse = Parse(sheet)
        parse.printStaff()
        sheet.close()
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()