# -*- coding: utf-8 -*-

def lower_first_letter(word):
    return word[0].lower() + word[1:]

def upper_first_letter(word):
    return word[0].upper() + word[1:]

def debug_trace():
  '''Set a tracepoint in the Python debugger that works with Qt'''
  from PyQt4.QtCore import pyqtRemoveInputHook
  from pdb import set_trace
  pyqtRemoveInputHook()
  set_trace()
