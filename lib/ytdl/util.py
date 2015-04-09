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

def log(msg):
  sys.stderr.write(msg + '\n')
  sys.stderr.flush()

def makedirs(name,mode=0o777,exist_ok=False):
  try: os.makedirs(name,mode)
  except os.error,e:
    if not exist_ok or e.errno != errno.EEXIST: raise

def out(s=''):
  if isinstance(s, unicode): s = s.encode('utf8')
  sys.stdout.write(s + '\n')
  sys.stdout.flush()
