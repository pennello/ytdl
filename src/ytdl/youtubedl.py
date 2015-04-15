# chris 040115 Wrapper for youtube-dl command-line construction.

def args(a):
  return ('youtube-dl','-i','--no-check-certificate') + a
