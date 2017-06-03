#!/usr/bin/env python

import os
import argparse
import subprocess
import tempfile

from zen.compile.js.linker import *


# Parse command line args
parser = argparse.ArgumentParser(description='Compile Zen code into JavaScript code')
parser.add_argument('command',
                    help = 'choose an action for the Zen Compiler to perform')
parser.add_argument('input',
                    help = 'the Zen file you want to compile')
parser.add_argument('-o', '--output',
                    metavar = '',
                    default = '/Users/mitchell/Desktop/zen.js',
                    help = 'where to put the compiled JavaScript code')
args = parser.parse_args()

# zen run: Compile and run the input file
if args.command == 'run':
    linker = Linker(args.input, os.path.dirname(__file__))
    linker.compile()
    code = linker.write()

    # Dump the code to a place where we can easily find it for
    # debugging purposes
    with open('/Users/mitchell/Desktop/zen.js', 'w+') as dump:
        dump.write(code)

    # Write the code to a temporary file, then run it by calling Node.js
    # as a subprocess
    with tempfile.NamedTemporaryFile() as temp:
        temp.write(code)
        temp.flush()
        subprocess.call(['node', temp.name])

# zen compile: Compile the input file and write the result to the output file
elif args.command == 'compile':
    linker = Linker(args.input, os.path.dirname(__file__))
    linker.compile()
    linker.link(args.output)
