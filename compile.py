# Simple .py -> .pyc Python 2-ish compilation behavior.

import os.path
import py_compile
import sys

for file in sys.argv[1:]:
  cfile, _ = os.path.splitext(file)
  cfile += '.pyc'
  py_compile.compile(file, cfile)
