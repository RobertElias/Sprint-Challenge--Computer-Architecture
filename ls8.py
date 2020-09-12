#!/usr/bin/env python3

"""Main."""
#python3 ls8.py sctest.ls8
import sys
from cpu import *

command = sys.argv[1]

cpu = CPU()

cpu.load(command)
cpu.run()