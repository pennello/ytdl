# chris 032515 Utilities.

import errno
import os
import sys

def segment(itr,n):
  r = ()
  for x in itr:
    r += x,
    if len(r) == n:
      yield r
      r = ()
  if r: yield r

def write(fobj,x):
  fobj.write('%s\n' % x)
  fobj.flush()

def log(x): write(sys.stderr,x)

def out(x=''):
  if isinstance(x, unicode): x = x.encode('utf8')
  write(sys.stdout,x)

def makedirs(name,mode=0o777,exist_ok=False):
  try: os.makedirs(name,mode)
  except os.error,e:
    if not exist_ok or e.errno != errno.EEXIST: raise
