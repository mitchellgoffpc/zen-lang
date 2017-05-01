#!/usr/bin/env python

import os
import argparse
import subprocess

from zen.compile.js.linker import *


# Parse command line args
parser = argparse.ArgumentParser(description='Compile Zen code into JavaScript code')
parser.add_argument('command',
                    help = 'pick an action for the Zen Compiler to perform')
parser.add_argument('input',
                    help = 'the Zen file you want to compile')
parser.add_argument('-o', '--output',
                    metavar = '',
                    default = '/Users/mitchell/Desktop/zen.js',
                    help = 'where to put the compiled JavaScript code')
args = parser.parse_args()

if args.command == 'run':
    linker = Linker(args.input, os.path.dirname(__file__))
    linker.compile()
    linker.link('/Users/mitchell/Desktop/zen.js')

    # Pass JS code to Node.js
    subprocess.call(['node', '/Users/mitchell/Desktop/zen.js'])
