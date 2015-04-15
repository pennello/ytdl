# chris 040115 Wrapper for youtube-dl command-line construction.

from .ssl import needshack

def args(a):
  r = 'youtube-dl','-i'
  if needshack(): r += '--no-check-certificates',
  return r + a
