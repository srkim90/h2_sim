# -*- coding: utf-8 -*-

'''
  Author   : Kim, Seongrae
  Filename : config.py
  Release  : 1
  Date     : 2018-07-02
 
  Description : config module for python
 
  Notes :
  ===================
  History
  ===================
  2018/07/02  created by Kim, Seongrae
'''
import os
import re
import sys    
from time import sleep

def search(dirname):
    filenames = os.listdir(dirname)
    for filename in filenames:
        full_filename = os.path.join(dirname, filename)
        print (full_filename)

if __name__ == '__main__':
    search(sys.argv[1])
