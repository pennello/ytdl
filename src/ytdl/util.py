# chris 032515

'''Utilities.'''

import errno
import os
import sys

def segment(itr,n):
  '''
  Segment iterable contents into tuples of length n.  Last tuple might
  be short.
  '''
  r = ()
  for x in itr:
    r += x,
    if len(r) == n:
      yield r
      r = ()
  if r: yield r

def write(fobj,x):
  '''
  Write object x to file object, including newline and flush, also
  encoding to UTF-8 if required.
  '''
  if isinstance(x, unicode): x = x.encode('utf8')
  fobj.write('%s\n' % x)
  fobj.flush()

def log(x):
  '''Write to standard error.'''
  write(sys.stderr,x)

def out(x=''):
  '''Write to standard out.'''
  write(sys.stdout,x)

# TODO Deprecate when moved to Python 3?
def makedirs(name,mode=0o777,exist_ok=False):
  '''Like Python 3's makedirs with exist_ok.'''
  try: os.makedirs(name,mode)
  except os.error,e:
    if not exist_ok or e.errno != errno.EEXIST: raise
