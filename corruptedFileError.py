'''
Created on Mar 14, 2014

@author: Timo Vehvilainen
'''

class CorruptedFileError(Exception):

    def __init__(self, message):
        self.message = message
    def __str__(self):
        return self.message
