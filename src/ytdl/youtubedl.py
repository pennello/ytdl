# chris 040115

'''Wrapper for youtube-dl command-line construction.'''

from .ssl import needshack

def args(a):
  '''
  Pass in arguments you want for youtube-dl.  Will provide some base
  common arguments.
  '''
  r = 'youtube-dl','-i'
  if needshack(): r += '--no-check-certificate',
  return r + a
